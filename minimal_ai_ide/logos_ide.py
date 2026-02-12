#!/usr/bin/env python3
"""
Logos IDE - Minimal AI IDE with Textual TUI

A terminal-based IDE that integrates:
1. File search for 22k+ files (not tree-based)
2. Text editor with syntax highlighting
3. AI panel using Logos Proxy with invariant auditing
4. Status bar showing git commit and last invariant

PRINCIPLE: "Minimum viable IDE" - no VS Code competitor, just essentials
PERFORMANCE: Indexes files once, uses fuzzy search, handles 22k files efficiently
AUDIT: Every AI interaction creates verifiable invariant linked to git state
"""

import asyncio
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.css.query import NoMatches
from textual.reactive import reactive
from textual.screen import Screen
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

# Try to import LogosProxy
try:
    from logos_proxy import LogosProxy

    LOGOS_PROXY_AVAILABLE = True
except ImportError:
    LOGOS_PROXY_AVAILABLE = False
    print("⚠️  LogosProxy not found, AI panel will be disabled")


class FileIndex:
    """
    Efficient file index for 22k+ files

    Performance rules:
    1. Index files once on startup
    2. Never use os.walk on every keystroke
    3. Cache file list in memory
    4. Filter with list comprehension
    5. Lazy load file content
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.file_index = []
        self.file_extensions = {
            ".py",
            ".cpp",
            ".h",
            ".hpp",
            ".md",
            ".txt",
            ".json",
            ".yaml",
            ".yml",
            ".js",
            ".ts",
            ".html",
            ".css",
        }
        self.indexed = False

    def build_index(self) -> int:
        """Build file index once on startup"""
        print(f"🔍 Building file index from {self.root_path}...")
        count = 0

        # Use rglob for efficient recursive search
        for ext in self.file_extensions:
            for file_path in self.root_path.rglob(f"*{ext}"):
                if file_path.is_file():
                    self.file_index.append(file_path)
                    count += 1

                    # Show progress every 1000 files
                    if count % 1000 == 0:
                        print(f"  Indexed {count} files...")

        print(f"✅ File index built: {count} files")
        self.indexed = True
        return count

    def search(self, query: str, limit: int = 50) -> List[Path]:
        """
        Search files by name (fuzzy matching)

        Args:
            query: Search string (case-insensitive)
            limit: Maximum number of results to return

        Returns:
            List of matching file paths
        """
        if not self.indexed:
            self.build_index()

        if not query:
            return []

        query_lower = query.lower()
        results = []

        # Simple substring matching (good enough for 22k files with limit=50)
        for file_path in self.file_index:
            if query_lower in str(file_path).lower():
                results.append(file_path)
                if len(results) >= limit:
                    break

        return results

    def get_file_content(self, file_path: Path) -> str:
        """Lazy load file content"""
        try:
            return file_path.read_text(encoding="utf-8", errors="ignore")
        except Exception as e:
            return f"Error reading file: {e}"


class FileSearcher(Widget):
    """
    File search widget with input and results list
    """

    search_query = reactive("")

    def __init__(self, file_index: FileIndex):
        super().__init__()
        self.file_index = file_index
        self.search_results: List[Path] = []

    def compose(self) -> ComposeResult:
        yield Input(placeholder="Search files...", id="file-search-input")
        yield ListView(id="file-search-results")

    def on_mount(self) -> None:
        self.query_one("#file-search-input").focus()

    @on(Input.Changed, "#file-search-input")
    def on_search_changed(self, event: Input.Changed) -> None:
        """Handle search input changes"""
        self.search_query = event.value
        self.update_search_results()

    def update_search_results(self) -> None:
        """Update search results based on current query"""
        if not self.search_query:
            self.search_results = []
            self.update_results_list()
            return

        # Search files
        self.search_results = self.file_index.search(self.search_query)
        self.update_results_list()

    def update_results_list(self) -> None:
        """Update the ListView with search results"""
        list_view = self.query_one("#file-search-results")
        list_view.clear()

        for file_path in self.search_results:
            # Create relative path for display
            try:
                rel_path = file_path.relative_to(self.file_index.root_path)
            except ValueError:
                rel_path = file_path

            # Create list item with file icon based on extension
            ext = file_path.suffix.lower()
            icon = self.get_file_icon(ext)
            list_view.append(ListItem(Label(f"{icon} {rel_path}")))

    def get_file_icon(self, ext: str) -> str:
        """Get icon for file extension"""
        icons = {
            ".py": "🐍",
            ".cpp": "⚙️",
            ".h": "📄",
            ".hpp": "📄",
            ".md": "📝",
            ".txt": "📄",
            ".json": "📊",
            ".yaml": "⚙️",
            ".yml": "⚙️",
            ".js": "📜",
            ".ts": "📜",
            ".html": "🌐",
            ".css": "🎨",
        }
        return icons.get(ext, "📄")


class EditorPane(Widget):
    """
    Editor widget with syntax highlighting
    """

    def __init__(self):
        super().__init__()
        self.current_file: Optional[Path] = None
        self.text_area: Optional[TextArea] = None

    def compose(self) -> ComposeResult:
        yield TextArea(
            id="editor-textarea",
            language="python",
            theme="monokai",
            show_line_numbers=True,
            tab_behavior="indent",
            soft_wrap=False,
        )

    def on_mount(self) -> None:
        self.text_area = self.query_one("#editor-textarea")

    def load_file(self, file_path: Path) -> None:
        """Load file into editor"""
        self.current_file = file_path

        # Set language based on file extension
        ext = file_path.suffix.lower()
        language = self.get_language_for_extension(ext)

        # Load content
        content = self.app.file_index.get_file_content(file_path)

        # Update editor
        self.text_area.language = language
        self.text_area.text = content

        # Update status bar
        self.app.update_status_bar(file_path=file_path)

    def get_language_for_extension(self, ext: str) -> str:
        """Get TextArea language for file extension"""
        language_map = {
            ".py": "python",
            ".cpp": "cpp",
            ".h": "cpp",
            ".hpp": "cpp",
            ".js": "javascript",
            ".ts": "typescript",
            ".html": "html",
            ".css": "css",
            ".md": "markdown",
            ".json": "json",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".txt": "text",
        }
        return language_map.get(ext, "text")

    def get_content(self) -> str:
        """Get current editor content"""
        return self.text_area.text if self.text_area else ""

    def save_file(self) -> bool:
        """Save current file"""
        if not self.current_file or not self.text_area:
            return False

        try:
            self.current_file.write_text(self.text_area.text, encoding="utf-8")

            # Trigger git status update
            self.app.update_git_status()

            return True
        except Exception as e:
            self.app.show_error(f"Error saving file: {e}")
            return False


class AIPanel(Widget):
    """AI chat panel with working conversation display"""

    def __init__(self):
        super().__init__()
        self.proxy = None
        self.last_invariant = ""
        self.balance = "Checking..."

        if LOGOS_PROXY_AVAILABLE:
            try:
                self.proxy = LogosProxy()
            except Exception as e:
                print(f"⚠️  LogosProxy init failed: {e}")

    def compose(self) -> ComposeResult:
        yield Label("🤖 AI Chat", classes="panel-title")
        # Use Static for simple text display (RichLog if available, else Static)
        yield Static(
            "No conversation yet.\nType below to start...",
            id="ai-chat-display",
            classes="chat-box",
        )
        yield Input(placeholder="Ask the AI...", id="ai-input")
        yield Horizontal(
            Button("Send", variant="primary", id="ai-send"),
            Button("Clear", id="ai-clear"),
            classes="ai-buttons",
        )
        yield Label("💰 Balance: Checking...", id="api-balance")

    def on_mount(self) -> None:
        asyncio.create_task(self.update_balance())

    async def update_balance(self) -> None:
        """Fetch DeepSeek API balance"""
        if not self.proxy:
            return

        try:
            import requests

            headers = {"Authorization": f"Bearer {self.proxy.api_key}"}
            response = await asyncio.to_thread(
                requests.get,
                "https://api.deepseek.com/user/balance",
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                balance_info = data.get("balance_infos", [{}])[0]
                total = balance_info.get("total_balance", "0")
                currency = balance_info.get("currency", "USD")

                balance_label = self.query_one("#api-balance")
                balance_label.update(f"💰 Balance: {total} {currency}")
        except Exception as e:
            balance_label = self.query_one("#api-balance")
            balance_label.update(f"💰 Balance: Error")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses"""
        button_id = event.button.id

        if button_id == "ai-send":
            await self.send_ai_query()
        elif button_id == "ai-clear":
            self.clear_chat()

    async def send_ai_query(self) -> None:
        """Send query and display in chat"""
        if not self.proxy:
            self.add_message("❌ Logos Proxy not available")
            return

        input_widget = self.query_one("#ai-input")
        query = input_widget.value.strip()

        if not query:
            return

        input_widget.value = ""

        # Display user message
        self.add_message(f"You: {query}")
        self.add_message("🤔 Thinking...")

        try:
            result = await asyncio.to_thread(self.proxy.query, query)

            # Clear "thinking" and show response
            self.clear_chat()
            self.add_message(f"You: {query}")

            response_text = result.get("response_text", "No response")
            self.last_invariant = result.get("invariant", "")[:16]

            # Show AI response
            self.add_message(f"AI: {response_text[:500]}...")
            if len(response_text) > 500:
                self.add_message("   ... (truncated)")
            self.add_message(f"🔐 Invariant: {self.last_invariant}...")

            # Update status bar
            self.app.update_status_bar(last_invariant=self.last_invariant)

            # Refresh balance (cost deducted)
            await self.update_balance()

        except Exception as e:
            self.add_message(f"❌ Error: {e}")

    def add_message(self, text: str):
        """Add message to chat display"""
        chat_display = self.query_one("#ai-chat-display")
        current = (
            chat_display.renderable
            if hasattr(chat_display.renderable, "plain")
            else str(chat_display.renderable)
        )
        if current.startswith("No conversation"):
            current = ""
        chat_display.update(f"{current}\n{text}" if current else text)

    def clear_chat(self):
        """Clear chat display"""
        chat_display = self.query_one("#ai-chat-display")
        chat_display.update("Chat cleared. Type below to start...")

    @on(Input.Submitted, "#ai-input")
    async def on_input_submitted(self, event: Input.Submitted) -> None:
        """Handle Enter key in input"""
        await self.send_ai_query()


class StatusBar(Widget):
    """
    Status bar showing git commit, file path, and last invariant
    """

    def __init__(self):
        super().__init__()
        self.git_commit = "NO_GIT"
        self.current_file = ""
        self.last_invariant = ""
        self.balance = "Checking..."

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label("", id="status-git"),
            Label("", id="status-file"),
            Label("", id="status-balance"),  # Add this
            Label("", id="status-invariant"),
            id="status-bar",
        )

    def on_mount(self) -> None:
        self.update_git_commit()

    def update_git_commit(self) -> None:
        """Get current git commit hash"""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=True,
                cwd=self.app.file_index.root_path,
            )
            self.git_commit = result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.git_commit = "NO_GIT"

        self.update_display()

    def update_display(self) -> None:
        """Update status bar display"""
        git_label = self.query_one("#status-git")
        file_label = self.query_one("#status-file")
        balance_label = self.query_one("#status-balance")
        invariant_label = self.query_one("#status-invariant")

        git_label.update(f"Git: {self.git_commit}")
        file_label.update(f"File: {self.current_file}" if self.current_file else "")
        balance_label.update(f"💰 {self.balance}" if self.balance else "")
        invariant_label.update(
            f"Invariant: {self.last_invariant}" if self.last_invariant else ""
        )

    def set_current_file(self, file_path: Optional[Path]) -> None:
        """Set current file path"""
        if file_path:
            try:
                self.current_file = str(
                    file_path.relative_to(self.app.file_index.root_path)
                )
            except ValueError:
                self.current_file = str(file_path)
        else:
            self.current_file = ""
        self.update_display()

    def set_last_invariant(self, invariant: str) -> None:
        """Set last invariant"""
        self.last_invariant = invariant[:8] if invariant else ""
        self.update_display()

    def set_balance(self, balance: str, currency: str = "USD"):
        """Set balance display"""
        self.balance = f"{balance} {currency}"
        self.update_display()


class LogosIDE(App):
    """
    Main Logos IDE application
    """

    CSS = """
    Screen {
        layout: grid;
        grid-size: 3 2;
        grid-gutter: 1;
        padding: 1;
    }

    #file-panel {
        width: 25%;
        border: solid $primary;
        padding: 1;
    }

    #editor-panel {
        width: 50%;
        border: solid $primary;
        padding: 1;
    }

    #ai-panel {
        width: 25%;
        border: solid $primary;
        padding: 1;
    }

    #file-search-input {
        width: 100%;
        margin-bottom: 1;
    }

    #file-search-results {
        height: 1fr;
        border: solid $panel;
    }

    #editor-textarea {
        height: 1fr;
    }

    #ai-chat-display {
        height: 1fr;
        border: solid $panel;
        padding: 1;
        overflow: auto;
        color: $text;
    }

    #ai-input {
        width: 100%;
        margin: 1 0;
    }

    .ai-buttons {
        height: auto;
        margin-bottom: 1;
    }

    #api-balance {
        height: 1;
        text-align: center;
        background: $surface;
        color: $success;
        text-style: bold;
    }

    #ai-input {
        width: 100%;
        margin-bottom: 1;
    }

    .ai-buttons {
        height: auto;
        margin-top: 1;
    }

    #status-bar {
        height: 3;
        background: $surface;
        border-top: solid $primary;
        padding: 0 1;
    }

    #status-git {
        width: 33%;
        text-style: bold;
    }

    #status-file {
        width: 34%;
        text-align: center;
    }

    #status-balance {
        width: 25%;
        text-align: center;
        color: $success;
        text-style: bold;
    }

    #status-invariant {
        width: 25%;
        text-align: right;
    }

    #status-git {
        width: 25%;
        text-style: bold;
    }

    #status-file {
        width: 25%;
        text-align: center;
    }

    .panel-title {
        text-style: bold;
        background: $surface;
        padding: 0 1;
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
        Binding("ctrl+s", "save_file", "Save"),
        Binding("ctrl+f", "focus_search", "Search Files"),
        Binding("ctrl+a", "focus_ai", "Focus AI"),
        Binding("f1", "show_help", "Help"),
    ]

    def __init__(self):
        super().__init__()
        self.file_index = FileIndex(Path.cwd())
        self.status_bar: Optional[StatusBar] = None
        self.editor_pane: Optional[EditorPane] = None
        self.ai_panel: Optional[AIPanel] = None

    def compose(self) -> ComposeResult:
        """Create child widgets for the app"""
        yield Header(show_clock=True)
        yield Horizontal(
            Vertical(
                Label("📁 File Search", classes="panel-title"),
                FileSearcher(self.file_index),
                id="file-panel",
            ),
            Vertical(
                Label("📝 Editor", classes="panel-title"),
                EditorPane(),
                id="editor-panel",
            ),
            Vertical(
                Label("🤖 AI Chat", classes="panel-title"),
                AIPanel(),
                id="ai-panel",
            ),
        )
        yield StatusBar()
        yield Footer()

    def on_mount(self) -> None:
        """Called when app starts"""
        self.status_bar = self.query_one(StatusBar)
        self.editor_pane = self.query_one(EditorPane)
        self.ai_panel = self.query_one(AIPanel)

        # Build file index in background
        asyncio.create_task(self.build_file_index_async())

        # Update git status
        self.update_git_status()

        # Show welcome message
        self.show_message("🚀 Logos IDE started. Press F1 for help.")

    async def build_file_index_async(self) -> None:
        """Build file index asynchronously"""
        count = await asyncio.to_thread(self.file_index.build_index)
        self.show_message(f"✅ Indexed {count} files. Ready for search.")

    def update_git_status(self) -> None:
        """Update git status in status bar"""
        if self.status_bar:
            self.status_bar.update_git_commit()

    def update_status_bar(
        self, file_path: Optional[Path] = None, last_invariant: str = ""
    ) -> None:
        """Update status bar with file and invariant"""
        if self.status_bar:
            if file_path:
                self.status_bar.set_current_file(file_path)
            if last_invariant:
                self.status_bar.set_last_invariant(last_invariant)

    def show_message(self, message: str) -> None:
        """Show message in status bar"""
        if self.status_bar:
            # Temporarily show message in file status area
            file_label = self.status_bar.query_one("#status-file")
            original_text = self.status_bar.current_file
            file_label.update(message)

            # Restore after 3 seconds
            async def restore_status():
                await asyncio.sleep(3)
                if self.status_bar:
                    file_label.update(f"File: {original_text}" if original_text else "")

            asyncio.create_task(restore_status())

    def show_error(self, error: str) -> None:
        """Show error message"""
        self.show_message(f"❌ {error}")

    def action_quit(self) -> None:
        """Quit the application"""
        self.exit()

    def action_save_file(self) -> None:
        """Save current file"""
        if self.editor_pane:
            if self.editor_pane.save_file():
                self.show_message("💾 File saved")
            else:
                self.show_error("Failed to save file")

    def action_focus_search(self) -> None:
        """Focus file search input"""
        try:
            search_input = self.query_one("#file-search-input")
            search_input.focus()
        except NoMatches:
            pass

    def action_focus_ai(self) -> None:
        """Focus AI input"""
        try:
            ai_input = self.query_one("#ai-input")
            ai_input.focus()
        except NoMatches:
            pass

    def action_show_help(self) -> None:
        """Show help message"""
        help_text = """
        Logos IDE Help
        ==============

        Key Bindings:
        - Ctrl+Q: Quit
        - Ctrl+S: Save current file
        - Ctrl+F: Focus file search
        - Ctrl+A: Focus AI input
        - F1: Show this help

        Navigation:
        - Click files in search results to open
        - Type in AI input and press Send
        - Use Tab to navigate between widgets

        Features:
        - File search handles 22k+ files
        - Syntax highlighting for Python, C++, etc.
        - AI chat with Logos Proxy auditing
        - Git commit tracking
        - Invariant verification
        """
        self.show_message("📖 Help - See console for details")
        print(help_text)

    @on(ListView.Selected, "#file-search-results")
    def on_file_selected(self, event: ListView.Selected) -> None:
        """Handle file selection from search results"""
        if not event.item or not self.editor_pane:
            return

        # Get the file path from the selected item
        list_item = event.item
        label = list_item.query_one(Label)
        file_name = label.renderable.strip()

        # Extract file path (remove icon and space)
        if " " in file_name:
            file_name = file_name.split(" ", 1)[1]

        # Find the actual file path
        for file_path in self.file_index.file_index:
            if str(file_path).endswith(file_name):
                self.editor_pane.load_file(file_path)
                break

    @on(Input.Submitted, "#ai-input")
    async def on_ai_input_submitted(self, event: Input.Submitted) -> None:
        """Handle AI input submission"""
        if self.ai_panel:
            await self.ai_panel.send_ai_query()


def main():
    """Main entry point"""
    try:
        app = LogosIDE()
        app.run()
    except KeyboardInterrupt:
        print("\n👋 Logos IDE closed")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
