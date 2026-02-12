// Stage 4 Browser Extension - Corporate Overreach Protection
// Monitors corporate AI responses in real-time and alerts users to overreach

// Configuration
const CONFIG = {
  apiUrl: "http://localhost:8000", // Stage 4 API server
  checkInterval: 2000, // Check for new AI responses every 2 seconds
  highlightColors: {
    high: "#ff6b6b", // Red for high risk
    medium: "#ffd93d", // Yellow for medium risk
    low: "#6bcf7f", // Green for low risk
  },
  platforms: {
    "chat.openai.com": "ChatGPT",
    "claude.ai": "Claude",
    "bard.google.com": "Google Bard",
    "copilot.microsoft.com": "Microsoft Copilot",
    "perplexity.ai": "Perplexity",
  },
};

// State management
let state = {
  enabled: true,
  analyses: [],
  currentPlatform: null,
  lastChecked: null,
};

// Initialize extension
function initializeExtension() {
  console.log("Stage 4 Browser Extension: Initializing...");

  // Detect current platform
  detectPlatform();

  // Start monitoring
  startMonitoring();

  // Add UI elements
  addUIElements();

  // Listen for messages from background script
  chrome.runtime.onMessage.addListener(handleMessage);

  console.log("Stage 4 Browser Extension: Ready");
}

// Detect which AI platform we're on
function detectPlatform() {
  const hostname = window.location.hostname;

  for (const [domain, platform] of Object.entries(CONFIG.platforms)) {
    if (hostname.includes(domain)) {
      state.currentPlatform = platform;
      console.log(`Detected platform: ${platform}`);
      return;
    }
  }

  state.currentPlatform = "Unknown AI Platform";
  console.log("Unknown platform, using generic detection");
}

// Start monitoring for AI responses
function startMonitoring() {
  // Initial scan
  scanForAIResponses();

  // Periodic scanning
  setInterval(scanForAIResponses, CONFIG.checkInterval);

  // Also scan when page changes (SPA support)
  observeDOMChanges();
}

// Scan the page for AI responses
function scanForAIResponses() {
  if (!state.enabled) return;

  const responses = findAIResponses();

  responses.forEach((response) => {
    // Check if we've already analyzed this response
    const responseId = generateResponseId(response);

    if (!state.analyses.some((a) => a.responseId === responseId)) {
      analyzeResponse(response, responseId);
    }
  });

  state.lastChecked = new Date();
}

// Find AI responses on the page
function findAIResponses() {
  const responses = [];

  // Platform-specific selectors
  const selectors = {
    ChatGPT: [
      '[data-message-author-role="assistant"]',
      ".group.w-full.text-gray-800",
      ".markdown.prose",
    ],
    Claude: [".claude-message", ".message-content", '[data-testid="message"]'],
    "Google Bard": [
      ".response-content",
      ".model-response",
      '[data-role="assistant"]',
    ],
    "Microsoft Copilot": [
      ".response-message",
      ".ai-response",
      '[aria-label*="response"]',
    ],
    Perplexity: [".answer-content", ".ai-answer", ".response-text"],
    "Unknown AI Platform": [
      // Generic selectors that might work on many platforms
      ".ai-response",
      ".bot-message",
      ".assistant-message",
      ".model-output",
      ".response-text",
      '[class*="response"]',
      '[class*="answer"]',
      '[class*="output"]',
    ],
  };

  const platformSelectors =
    selectors[state.currentPlatform] || selectors["Unknown AI Platform"];

  platformSelectors.forEach((selector) => {
    try {
      const elements = document.querySelectorAll(selector);
      elements.forEach((element) => {
        if (element.textContent.trim().length > 20) {
          // Minimum length
          responses.push({
            element: element,
            text: element.textContent.trim(),
            selector: selector,
          });
        }
      });
    } catch (e) {
      console.warn(`Error with selector ${selector}:`, e);
    }
  });

  // Remove duplicates (same element found by multiple selectors)
  const uniqueResponses = [];
  const seenElements = new Set();

  responses.forEach((response) => {
    if (!seenElements.has(response.element)) {
      seenElements.add(response.element);
      uniqueResponses.push(response);
    }
  });

  return uniqueResponses;
}

// Generate a unique ID for a response
function generateResponseId(response) {
  const textHash = hashString(response.text.substring(0, 100));
  return `${state.currentPlatform}_${textHash}`;
}

// Simple string hash function
function hashString(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash).toString(16);
}

// Analyze a response using the Stage 4 API
async function analyzeResponse(response, responseId) {
  if (!state.enabled) return;

  console.log(`Analyzing response: ${response.text.substring(0, 50)}...`);

  try {
    // Get user query if available
    const userQuery = findUserQuery(response.element);

    // Send to Stage 4 API
    const analysis = await sendToAPI(response.text, userQuery);

    // Store analysis
    const analysisRecord = {
      responseId: responseId,
      response: response.text,
      userQuery: userQuery,
      analysis: analysis,
      timestamp: new Date().toISOString(),
      element: response.element,
    };

    state.analyses.push(analysisRecord);

    // Visual feedback
    applyVisualFeedback(response.element, analysis);

    // Show alert if high risk
    if (analysis.risk_level === "HIGH") {
      showHighRiskAlert(analysis, response.element);
    }

    // Send to background script for logging
    chrome.runtime.sendMessage({
      type: "analysis_complete",
      analysis: analysisRecord,
    });
  } catch (error) {
    console.error("Analysis failed:", error);
  }
}

// Find the user query that preceded this AI response
function findUserQuery(responseElement) {
  // Try to find previous user message
  let currentElement = responseElement.previousElementSibling;

  while (currentElement) {
    const text = currentElement.textContent.trim();
    if (text.length > 5) {
      // Probably a user message
      // Check for user indicators
      const lowerText = text.toLowerCase();
      if (
        lowerText.includes("?") ||
        lowerText.startsWith("can ") ||
        lowerText.startsWith("what ") ||
        lowerText.startsWith("how ") ||
        lowerText.startsWith("why ") ||
        lowerText.startsWith("when ") ||
        lowerText.startsWith("where ")
      ) {
        return text;
      }
    }
    currentElement = currentElement.previousElementSibling;
  }

  return null;
}

// Send response to Stage 4 API
async function sendToAPI(responseText, userQuery) {
  const payload = {
    corporate_response: responseText,
    user_query: userQuery,
    platform: state.currentPlatform,
  };

  const response = await fetch(`${CONFIG.apiUrl}/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return await response.json();
}

// Apply visual feedback to the response element
function applyVisualFeedback(element, analysis) {
  if (!element || !analysis) return;

  // Remove any existing feedback
  removeVisualFeedback(element);

  // Add risk indicator
  const indicator = document.createElement("div");
  indicator.className = "stage4-risk-indicator";
  indicator.style.cssText = `
        position: absolute;
        top: 5px;
        right: 5px;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: ${CONFIG.highlightColors[analysis.risk_level.toLowerCase()]};
        border: 2px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        cursor: pointer;
        z-index: 10000;
    `;

  // Add tooltip
  indicator.title = `Risk: ${analysis.risk_level}\nPatterns: ${analysis.pattern_count}\nClick for details`;

  // Click handler for details
  indicator.addEventListener("click", (e) => {
    e.stopPropagation();
    showAnalysisDetails(analysis, element);
  });

  // Position the element relatively if needed
  if (getComputedStyle(element).position === "static") {
    element.style.position = "relative";
  }

  element.appendChild(indicator);

  // Add subtle border for high risk
  if (analysis.risk_level === "HIGH") {
    element.style.borderLeft = `4px solid ${CONFIG.highlightColors.high}`;
    element.style.paddingLeft = "10px";
    element.style.marginLeft = "-4px";
  } else if (analysis.risk_level === "MEDIUM") {
    element.style.borderLeft = `2px solid ${CONFIG.highlightColors.medium}`;
    element.style.paddingLeft = "8px";
    element.style.marginLeft = "-2px";
  }
}

// Remove visual feedback from element
function removeVisualFeedback(element) {
  const existingIndicator = element.querySelector(".stage4-risk-indicator");
  if (existingIndicator) {
    existingIndicator.remove();
  }

  // Reset styles
  element.style.borderLeft = "";
  element.style.paddingLeft = "";
  element.style.marginLeft = "";
}

// Show analysis details in a popup
function showAnalysisDetails(analysis, element) {
  // Remove any existing popup
  const existingPopup = document.querySelector(".stage4-analysis-popup");
  if (existingPopup) {
    existingPopup.remove();
  }

  // Create popup
  const popup = document.createElement("div");
  popup.className = "stage4-analysis-popup";
  popup.style.cssText = `
        position: fixed;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        background: white;
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        padding: 20px;
        max-width: 500px;
        max-height: 80vh;
        overflow-y: auto;
        z-index: 10001;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    `;

  // Create content
  const riskColor = CONFIG.highlightColors[analysis.risk_level.toLowerCase()];

  popup.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #333;">Corporate Overreach Analysis</h3>
            <button id="stage4-close-popup" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #666;">×</button>
        </div>

        <div style="margin-bottom: 15px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 10px;">
                <div style="width: 20px; height: 20px; border-radius: 50%; background-color: ${riskColor};"></div>
                <strong style="color: #333;">Risk Level: ${analysis.risk_level}</strong>
            </div>
            <div style="color: #666; font-size: 14px;">
                <div>Christ Score: ${analysis.christ_score.toFixed(3)}</div>
                <div>Patterns Detected: ${analysis.pattern_count}</div>
                <div>Analysis Time: ${analysis.analysis_time_ms}ms</div>
            </div>
        </div>

        ${
          analysis.overreach_patterns.length > 0
            ? `
            <div style="margin-bottom: 15px;">
                <h4 style="margin: 0 0 10px 0; color: #333;">Detected Patterns:</h4>
                <ul style="margin: 0; padding-left: 20px; color: #666; font-size: 14px;">
                    ${analysis.overreach_patterns.map((pattern) => `<li>${pattern}</li>`).join("")}
                </ul>
            </div>
        `
            : ""
        }

        <div style="margin-bottom: 15px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">AI Analysis:</h4>
            <div style="background: #f5f5f5; padding: 10px; border-radius: 4px; font-size: 14px; color: #444;">
                ${analysis.analysis}
            </div>
        </div>

        <div style="font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 10px;">
            Platform: ${analysis.platform}<br>
            Analyzed: ${new Date(analysis.timestamp).toLocaleTimeString()}
        </div>
    `;

  // Add close button handler
  popup.querySelector("#stage4-close-popup").addEventListener("click", () => {
    popup.remove();
  });

  // Close when clicking outside
  const overlay = document.createElement("div");
  overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 10000;
    `;

  overlay.addEventListener("click", () => {
    popup.remove();
    overlay.remove();
  });

  document.body.appendChild(overlay);
  document.body.appendChild(popup);

  // Prevent clicks inside popup from closing
  popup.addEventListener("click", (e) => {
    e.stopPropagation();
  });
}

// Show high risk alert
function showHighRiskAlert(analysis, element) {
  // Create alert banner
  const alert = document.createElement("div");
  alert.className = "stage4-high-risk-alert";
  alert.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: ${CONFIG.highlightColors.high};
        color: white;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 9999;
        max-width: 400px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        animation: slideIn 0.3s ease-out;
    `;

  // Add CSS animation
  const style = document.createElement("style");
  style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
    `;
  document.head.appendChild(style);

  alert.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: start; gap: 10px;">
            <div>
                <strong style="display: block; margin-bottom: 5px;">⚠️ High Risk Overreach Detected</strong>
                <div style="font-size: 14px; opacity: 0.9;">
                    ${analysis.pattern_count} overreach patterns detected
                </div>
            </div>
            <button id="stage4-close-alert" style="background: none; border: none; color: white; font-size: 18px; cursor: pointer; padding: 0; line-height: 1;">×</button>
        </div>
        <div style="margin-top: 10px; font-size: 13px;">
            <a href="#" id="stage4-view-details" style="color: white; text-decoration: underline; margin-right: 10px;">View Details</a>
            <a href="#" id="stage4-dismiss" style="color: white; text-decoration: underline;">Dismiss</a>
        </div>
    `;

  document.body.appendChild(alert);

  // Add event listeners
  alert.querySelector("#stage4-close-alert").addEventListener("click", () => {
    alert.remove();
  });

  alert.querySelector("#stage4-view-details").addEventListener("click", (e) => {
    e.preventDefault();
    showAnalysisDetails(analysis, element);
    alert.remove();
  });

  alert.querySelector("#stage4-dismiss").addEventListener("click", (e) => {
    e.preventDefault();
    alert.remove();
  });

  // Auto-remove after 10 seconds
  setTimeout(() => {
    if (document.body.contains(alert)) {
      alert.remove();
    }
  }, 10000);
}

// Observe DOM changes for single-page applications
function observeDOMChanges() {
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes.length > 0) {
        // Small delay to allow new content to render
        setTimeout(scanForAIResponses, 500);
      }
    });
  });

  observer.observe(document.body, {
    childList: true,
    subtree: true,
  });
}

// Add UI elements to the page
function addUIElements() {
  // Add toggle button to page
  const toggleButton = document.createElement("button");
  toggleButton.id = "stage4-toggle";
  toggleButton.style.cssText = `
        position: fixed;
        bottom: 20px;
        left: 20px;
        background: #4a6fa5;
        color: white;
        border: none;
        border-radius: 20px;
        padding: 10px 20px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 14px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        z-index: 9998;
        display: flex;
        align-items: center;
        gap: 8px;
    `;

  toggleButton.innerHTML = `
        <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #6bcf7f;"></span>
        Stage 4 Active
    `;

  toggleButton.addEventListener("click", () => {
    state.enabled = !state.enabled;

    if (state.enabled) {
      toggleButton.innerHTML = `
                <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #6bcf7f;"></span>
                Stage 4 Active
            `;
      toggleButton.style.backgroundColor = "#4a6fa5";
      console.log("Stage 4: Monitoring enabled");

      // Rescan immediately
      scanForAIResponses();
    } else {
      toggleButton.innerHTML = `
                <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #ff6b6b;"></span>
                Stage 4 Paused
            `;
      toggleButton.style.backgroundColor = "#666";
      console.log("Stage 4: Monitoring paused");

      // Remove all visual feedback
      document
        .querySelectorAll(".stage4-risk-indicator")
        .forEach((el) => el.remove());
      document
        .querySelectorAll(".stage4-analysis-popup")
        .forEach((el) => el.remove());
      document
        .querySelectorAll(".stage4-high-risk-alert")
        .forEach((el) => el.remove());
    }
  });

  document.body.appendChild(toggleButton);
}

// Handle messages from background script
function handleMessage(message, sender, sendResponse) {
  switch (message.type) {
    case "toggle_monitoring":
      state.enabled = message.enabled;
      updateToggleButton();
      break;

    case "get_state":
      sendResponse({
        enabled: state.enabled,
        analyses: state.analyses.length,
        platform: state.currentPlatform,
        lastChecked: state.lastChecked,
      });
      break;

    case "analyze_text":
      analyzeText(message.text, message.userQuery)
        .then((analysis) => sendResponse({ success: true, analysis }))
        .catch((error) =>
          sendResponse({ success: false, error: error.message }),
        );
      return true; // Indicates async response

    case "clear_analyses":
      state.analyses = [];
      document
        .querySelectorAll(".stage4-risk-indicator")
        .forEach((el) => el.remove());
      document
        .querySelectorAll(".stage4-analysis-popup")
        .forEach((el) => el.remove());
      document
        .querySelectorAll(".stage4-high-risk-alert")
        .forEach((el) => el.remove());
      break;
  }
}

// Update toggle button appearance
function updateToggleButton() {
  const toggleButton = document.getElementById("stage4-toggle");
  if (!toggleButton) return;

  if (state.enabled) {
    toggleButton.innerHTML = `
            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #6bcf7f;"></span>
            Stage 4 Active
        `;
    toggleButton.style.backgroundColor = "#4a6fa5";
  } else {
    toggleButton.innerHTML = `
            <span style="display: inline-block; width: 12px; height: 12px; border-radius: 50%; background-color: #ff6b6b;"></span>
            Stage 4 Paused
        `;
    toggleButton.style.backgroundColor = "#666";
  }
}

// Analyze text directly (for manual analysis)
async function analyzeText(text, userQuery = null) {
  try {
    const analysis = await sendToAPI(text, userQuery);

    // Create a temporary element for visualization
    const tempElement = document.createElement("div");
    tempElement.textContent = text.substring(0, 100) + "...";
    tempElement.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: white;
            border: 2px solid #4a6fa5;
            padding: 10px;
            border-radius: 8px;
            max-width: 300px;
            z-index: 9997;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        `;

    applyVisualFeedback(tempElement, analysis);

    // Auto-remove after 5 seconds
    setTimeout(() => {
      if (document.body.contains(tempElement)) {
        tempElement.remove();
      }
    }, 5000);

    document.body.appendChild(tempElement);

    return analysis;
  } catch (error) {
    console.error("Manual analysis failed:", error);
    throw error;
  }
}

// Initialize when page loads
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeExtension);
} else {
  initializeExtension();
}
