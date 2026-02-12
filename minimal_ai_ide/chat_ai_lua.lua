-- chat_ai_lua.lua
-- Σ_LORA AI Chat Bridge for Advanced Peripherals
-- Simple Lua script that connects Chat Box peripheral to Python AI server

-- ==================== CONFIGURATION ====================

local AI_SERVER_URL = "http://localhost:8080/chat/message"
local COMMAND_PREFIX = "!ai "
local AI_NAME = "Σ_LORA_AI"
local CHECK_INTERVAL = 1  -- Check chat every 1 second
local MAX_MESSAGE_LENGTH = 256

-- ==================== LOGGING ====================

local function log(message)
    local timestamp = os.time()
    local timeStr = os.date("%H:%M:%S", timestamp)
    print("[" .. timeStr .. "] " .. message)

    -- Also write to log file
    local logFile = "/chat_ai.log"
    local file = fs.open(logFile, "a")
    if file then
        file.writeLine("[" .. timeStr .. "] " .. message)
        file.close()
    end
end

local function logError(message)
    log("[ERROR] " .. message)
end

local function logInfo(message)
    log("[INFO] " .. message)
end

-- ==================== CHAT BOX SETUP ====================

local function setupChatBox()
    -- Find Chat Box peripheral
    local sides = {"top", "bottom", "left", "right", "front", "back"}

    for _, side in ipairs(sides) do
        if peripheral.getType(side) == "chatBox" then
            logInfo("Found Chat Box on side: " .. side)
            return peripheral.wrap(side)
        end
    end

    logError("No Chat Box peripheral found!")
    logInfo("Please attach a Chat Box to any side of the computer")
    return nil
end

-- ==================== AI SERVER COMMUNICATION ====================

local function callAIServer(player, message)
    logInfo("Sending to AI: " .. player .. ": " .. message)

    local payload = {
        player = player,
        message = message,
        timestamp = os.date("%Y-%m-%dT%H:%M:%S"),
        world = "overworld",
        dimension = "0"
    }

    local requestBody = textutils.serializeJSON(payload)
    local headers = {
        ["Content-Type"] = "application/json"
    }

    local response = http.post(AI_SERVER_URL, requestBody, headers)

    if not response then
        logError("AI server connection failed")
        return nil, "AI server unreachable"
    end

    local responseText = response.readAll()
    response.close()

    local success, data = pcall(textutils.unserializeJSON, responseText)

    if not success then
        logError("Failed to parse AI response: " .. responseText)
        return nil, "Invalid AI response"
    end

    if data.error then
        logError("AI error: " .. data.error)
        return nil, data.error
    end

    if not data.success then
        logError("AI processing failed: " .. (data.error or "Unknown error"))
        return nil, data.error or "AI processing failed"
    end

    logInfo("AI response received successfully")
    return data, nil
end

-- ==================== CHAT PROCESSING ====================

local function processChatMessage(chatBox, player, message)
    -- Check if message is for AI
    if not message:find("^" .. COMMAND_PREFIX) then
        return false  -- Not an AI command
    end

    logInfo("Processing AI command from " .. player .. ": " .. message)

    -- Call AI server
    local aiResponse, errorMsg = callAIServer(player, message)

    if not aiResponse then
        -- Send error to chat
        chatBox.sendMessage("[" .. AI_NAME .. "] Error: " .. errorMsg, player)
        return true
    end

    -- Send AI response to chat
    if aiResponse.response then
        -- Truncate if too long
        local responseText = aiResponse.response
        if #responseText > MAX_MESSAGE_LENGTH then
            responseText = responseText:sub(1, MAX_MESSAGE_LENGTH) .. "..."
        end

        chatBox.sendMessage(responseText, player)
        logInfo("AI response sent to chat: " .. responseText)
    end

    -- Execute Lua command if provided
    if aiResponse.command then
        logInfo("Executing AI command...")

        -- Save command to file and execute
        local tempFile = "/ai_command.lua"
        local file = fs.open(tempFile, "w")
        if file then
            file.write("-- AI Generated Command\n")
            file.write("-- Player: " .. player .. "\n")
            file.write("-- Original: " .. message .. "\n\n")
            file.write(aiResponse.command)
            file.close()

            -- Execute in background
            shell.run(tempFile)

            -- Clean up
            fs.delete(tempFile)
        else
            logError("Failed to create command file")
        end
    end

    -- Log constraint info if available
    if aiResponse.constraints and aiResponse.christ_score then
        logInfo("Σ_LORA Christ Score: " .. string.format("%.2f", aiResponse.christ_score))

        local failedConstraints = {}
        for constraint, satisfied in pairs(aiResponse.constraints) do
            if not satisfied then
                table.insert(failedConstraints, constraint)
            end
        end

        if #failedConstraints > 0 then
            logInfo("Failed constraints: " .. table.concat(failedConstraints, ", "))
        end
    end

    return true
end

-- ==================== MAIN LOOP ====================

local function mainLoop(chatBox)
    logInfo("Σ_LORA AI Chat Bridge started")
    logInfo("AI Server: " .. AI_SERVER_URL)
    logInfo("Command Prefix: " .. COMMAND_PREFIX)
    logInfo("AI Name: " .. AI_NAME)
    logInfo("")
    logInfo("Type '" .. COMMAND_PREFIX .. "help' in Minecraft chat for assistance")
    logInfo("=" .. string.rep("=", 40))

    -- Send startup message to chat
    chatBox.sendMessage("[" .. AI_NAME .. "] Online! Type '" .. COMMAND_PREFIX .. "help' for assistance")

    local lastMessages = {}
    local messageHistory = {}

    while true do
        -- Get recent messages from chat box
        local messages = chatBox.getMessages()

        if messages then
            for _, msg in ipairs(messages) do
                -- Create unique message ID
                local msgId = msg.player .. ":" .. msg.message .. ":" .. tostring(msg.timestamp)

                -- Check if we've already processed this message
                if not lastMessages[msgId] then
                    lastMessages[msgId] = true

                    -- Keep only recent message IDs (prevent memory leak)
                    table.insert(messageHistory, msgId)
                    if #messageHistory > 100 then
                        local oldId = table.remove(messageHistory, 1)
                        lastMessages[oldId] = nil
                    end

                    -- Process the message
                    local isAICommand = processChatMessage(chatBox, msg.player, msg.message)

                    if isAICommand then
                        logInfo("Processed AI command from " .. msg.player)
                    end
                end
            end
        end

        -- Sleep to prevent CPU overload
        os.sleep(CHECK_INTERVAL)
    end
end

-- ==================== HELP COMMAND HANDLER ====================

local function sendHelpMessage(chatBox, player)
    local helpMessage = [[
[Σ_LORA_AI] Available Commands:
!ai help - Show this help message
!ai dig <description> - Dig/mine with safety
!ai build <description> - Build structures
!ai find <item> - Find resources
!ai craft <item> - Crafting assistance
!ai explore <area> - Exploration help
!ai status - Check AI system status

Σ_LORA Constraints Applied:
✓ LOGOS - Logical consistency
✓ CHALCEDON - Human-AI collaboration
✓ GRACE - Error forgiveness
✓ ESCHATON - Purpose alignment
✓ AGAPE - User benefit
✓ KENOSIS - No autonomy
]]

    chatBox.sendMessage(helpMessage, player)
end

-- ==================== STARTUP ====================

local function main()
    print("=" .. string.rep("=", 50))
    print("Σ_LORA AI CHAT BRIDGE - ADVANCED PERIPHERALS")
    print("=" .. string.rep("=", 50))

    -- Check for HTTP API
    if not http then
        print("ERROR: HTTP API not enabled!")
        print("Enable it in ComputerCraft config:")
        print("  config/computercraft.toml")
        print("  http.enabled = true")
        return
    end

    -- Setup Chat Box
    local chatBox = setupChatBox()
    if not chatBox then
        print("Please attach a Chat Box peripheral and restart")
        return
    end

    -- Test AI server connection
    print("Testing AI server connection...")
    local response = http.get("http://localhost:8080/")

    if response then
        local data = response.readAll()
        response.close()

        local success, parsed = pcall(textutils.unserializeJSON, data)
        if success and parsed.status == "online" then
            print("✓ AI server connected: " .. parsed.service)
        else
            print("✗ AI server response invalid")
            print("Make sure Python server is running:")
            print("  python chat_ai_bridge.py")
        end
    else
        print("✗ AI server not responding")
        print("Start the server: python chat_ai_bridge.py")
    end

    print("=" .. string.rep("=", 50))
    print("Starting chat monitoring...")
    print("Press Ctrl+T to stop")
    print("=" .. string.rep("=", 50))

    -- Start main loop
    local success, err = pcall(function()
        mainLoop(chatBox)
    end)

    if not success then
        logError("Main loop crashed: " .. err)
        print("Error: " .. err)
        print("Restart the script to continue")
    end
end

-- Run main function
main()
