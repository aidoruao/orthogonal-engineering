"""
Crusader Combat Refrigerator - Display Interface System
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Display interface system for the Crusader combat refrigerator.
Provides visual feedback, status information, and user interaction.
Supports multiple display types (LCD, OLED, TFT) with fallback modes.
"""

import asyncio
import math
import random
import textwrap
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Tuple, Union

from ..core.constants import EnvironmentalConstants, HardwareConstants, TimeConstants
from ..core.utils.time_utils import TimeUtils


class DisplayType(Enum):
    """Supported display types."""

    LCD_16x2 = auto()  # 16x2 character LCD
    LCD_20x4 = auto()  # 20x4 character LCD
    OLED_128x64 = auto()  # 128x64 pixel OLED
    TFT_240x320 = auto()  # 240x320 pixel TFT
    SIMULATED = auto()  # Simulated display for testing
    TERMINAL = auto()  # Terminal/console output


class DisplayMode(Enum):
    """Display operational modes."""

    NORMAL = auto()  # Normal operation
    DIAGNOSTIC = auto()  # Diagnostic information
    CONFIGURATION = auto()  # Configuration mode
    MAINTENANCE = auto()  # Maintenance mode
    EMERGENCY = auto()  # Emergency information
    SCREENSAVER = auto()  # Screensaver mode
    OFF = auto()  # Display off (power saving)


class DisplayStatus(Enum):
    """Display system status."""

    READY = auto()  # Ready for operation
    ACTIVE = auto()  # Actively displaying
    UPDATING = auto()  # Updating display content
    ERROR = auto()  # Display error
    DIM = auto()  # Dimmed (power saving)
    CALIBRATING = auto()  # Calibrating display
    MAINTENANCE = auto()  # Under maintenance


class DisplayPage(Enum):
    """Standard display pages."""

    SYSTEM_STATUS = auto()  # Overall system status
    WARFARE_STATUS = auto()  # Warfare subsystem status
    ENVIRONMENTAL = auto()  # Environmental conditions
    PERFORMANCE = auto()  # Performance metrics
    DIAGNOSTICS = auto()  # Diagnostic information
    CONFIGURATION = auto()  # Configuration settings
    MAINTENANCE = auto()  # Maintenance information
    EMERGENCY = auto()  # Emergency alerts
    SPLASH = auto()  # Splash screen
    BOOT = auto()  # Boot sequence


@dataclass
class DisplayConfig:
    """Display configuration."""

    # Display specifications
    display_type: DisplayType = DisplayType.LCD_16x2
    width: int = 16  # Characters or pixels
    height: int = 2  # Lines or pixels
    contrast: int = 50  # 0-100 contrast level
    brightness: int = 70  # 0-100 brightness level
    backlight_timeout: int = 30  # Seconds before dimming
    screensaver_timeout: int = 300  # Seconds before screensaver

    # Update parameters
    update_interval_seconds: float = 1.0
    scroll_speed_chars_per_second: float = 5.0
    blink_interval_seconds: float = 0.5

    # Content parameters
    max_lines: int = 4
    max_chars_per_line: int = 20
    wrap_text: bool = True
    scroll_long_text: bool = True

    # Power management
    power_saving_enabled: bool = True
    dim_brightness: int = 20  # Brightness when dimmed
    off_timeout_minutes: int = 10  # Minutes before turning off

    # Fallback configuration
    fallback_to_terminal: bool = True
    log_to_file: bool = True
    log_file_path: str = "logs/display.log"


@dataclass
class DisplayContent:
    """Content to display."""

    page: DisplayPage
    lines: List[str]  # Text lines to display
    priority: int = 1  # 1-10, higher = more important
    duration_seconds: Optional[float] = None  # None = until replaced
    blink_lines: List[int] = None  # Lines to blink (0-indexed)
    scroll_lines: List[int] = None  # Lines to scroll
    metadata: Optional[Dict[str, Any]] = None

    def validate(self, config: DisplayConfig) -> bool:
        """Validate content against display capabilities."""
        if len(self.lines) > config.max_lines:
            return False

        for line in self.lines:
            if len(line) > config.max_chars_per_line:
                if not config.wrap_text and not config.scroll_long_text:
                    return False

        return True


@dataclass
class DisplayState:
    """Current display state."""

    display_type: DisplayType
    mode: DisplayMode
    status: DisplayStatus
    current_page: DisplayPage
    current_content: Optional[DisplayContent]
    brightness: int
    contrast: int
    backlight_on: bool
    last_update: datetime
    update_count: int
    error_count: int
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class DisplayEvent:
    """Display event record."""

    event_id: str
    timestamp: datetime
    event_type: str
    page: Optional[DisplayPage]
    content_preview: Optional[str]
    success: bool
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        if self.page:
            data["page"] = self.page.name
        return data


@dataclass
class DisplayMetrics:
    """Display performance metrics."""

    timestamp: datetime
    update_rate_hz: float
    error_rate_percent: float
    brightness_average: float
    content_changes_per_minute: float
    response_time_ms: float
    power_consumption_mw: float
    backlight_uptime_percent: float
    metadata: Optional[Dict[str, Any]] = None


class DisplayInterface:
    """
    Display interface system for Crusader combat refrigerator.
    Manages display output, content rendering, and user feedback.
    """

    def __init__(self, config: Optional[DisplayConfig] = None):
        """Initialize display interface."""
        self.config = config or DisplayConfig()
        self.mode = DisplayMode.NORMAL
        self.status = DisplayStatus.READY
        self.current_page = DisplayPage.SPLASH

        # Content management
        self.current_content: Optional[DisplayContent] = None
        self.content_queue: List[DisplayContent] = []
        self.content_history: List[DisplayContent] = []
        self.page_templates: Dict[DisplayPage, DisplayContent] = {}

        # State tracking
        self.state = DisplayState(
            display_type=self.config.display_type,
            mode=self.mode,
            status=self.status,
            current_page=self.current_page,
            current_content=None,
            brightness=self.config.brightness,
            contrast=self.config.contrast,
            backlight_on=True,
            last_update=datetime.now(),
            update_count=0,
            error_count=0,
        )

        # Performance tracking
        self.metrics_history: List[DisplayMetrics] = []
        self.event_history: List[DisplayEvent] = []

        # Hardware interface (simulated for now)
        self.hardware_connected = False
        self.simulation_mode = True

        # Async components
        self._update_task: Optional[asyncio.Task] = None
        self._content_task: Optional[asyncio.Task] = None
        self._monitoring_task: Optional[asyncio.Task] = None
        self._shutdown_event = asyncio.Event()

        # Initialize templates
        self._initialize_templates()

        print(
            f"DisplayInterface initialized with {self.config.display_type.name} display"
        )

    def _initialize_templates(self) -> None:
        """Initialize display page templates."""
        # System Status template
        self.page_templates[DisplayPage.SYSTEM_STATUS] = DisplayContent(
            page=DisplayPage.SYSTEM_STATUS,
            lines=[
                "Crusader System",
                "Status: OPERATIONAL",
                "Mode: NORMAL",
                "Uptime: 00:00:00",
            ],
            priority=5,
            duration_seconds=10.0,
        )

        # Warfare Status template
        self.page_templates[DisplayPage.WARFARE_STATUS] = DisplayContent(
            page=DisplayPage.WARFARE_STATUS,
            lines=["Warfare Systems", "Spores: READY", "UV: ACTIVE", "AirCurtain: ON"],
            priority=5,
            duration_seconds=10.0,
        )

        # Environmental template
        self.page_templates[DisplayPage.ENVIRONMENTAL] = DisplayContent(
            page=DisplayPage.ENVIRONMENTAL,
            lines=["Environment", "Temp: 22.5°C", "Humidity: 45%", "Flies: 0"],
            priority=4,
            duration_seconds=8.0,
        )

        # Diagnostics template
        self.page_templates[DisplayPage.DIAGNOSTICS] = DisplayContent(
            page=DisplayPage.DIAGNOSTICS,
            lines=["Diagnostics", "CPU: 15%", "Mem: 45%", "Disk: 60%"],
            priority=3,
            duration_seconds=8.0,
        )

        # Emergency template
        self.page_templates[DisplayPage.EMERGENCY] = DisplayContent(
            page=DisplayPage.EMERGENCY,
            lines=["! EMERGENCY !", "System Error", "Check logs", "Contact support"],
            priority=10,  # Highest priority
            duration_seconds=None,  # Stay until cleared
            blink_lines=[0, 1],  # Blink emergency lines
        )

        # Splash template
        self.page_templates[DisplayPage.SPLASH] = DisplayContent(
            page=DisplayPage.SPLASH,
            lines=[
                "CRUSADER",
                "Combat Refrigerator",
                "Version 1.0.0",
                "Initializing...",
            ],
            priority=1,
            duration_seconds=5.0,
        )

    async def start(self) -> bool:
        """Start the display interface."""
        if self.status in [DisplayStatus.ACTIVE, DisplayStatus.UPDATING]:
            print("Display interface already running")
            return False

        print("Starting display interface")
        self.status = DisplayStatus.UPDATING

        try:
            # Connect to hardware
            await self._connect_hardware()

            # Initialize display
            await self._initialize_display()

            # Show splash screen
            await self.show_page(DisplayPage.SPLASH)

            # Start async tasks
            self._update_task = asyncio.create_task(self._update_loop())
            self._content_task = asyncio.create_task(self._content_loop())
            self._monitoring_task = asyncio.create_task(self._monitoring_loop())

            self.status = DisplayStatus.ACTIVE
            print("Display interface started successfully")
            return True

        except Exception as e:
            self.status = DisplayStatus.ERROR
            print(f"Failed to start display interface: {e}")
            return False

    async def stop(self) -> bool:
        """Stop the display interface."""
        if self.status in [DisplayStatus.READY, DisplayStatus.ERROR]:
            print("Display interface not running")
            return False

        print("Stopping display interface")
        self.status = DisplayStatus.UPDATING

        try:
            # Signal shutdown
            self._shutdown_event.set()

            # Clear display
            await self._clear_display()

            # Show shutdown message
            await self._display_text(["Shutting down", "Goodbye"], duration=2.0)

            # Turn off backlight
            await self.set_backlight(False)

            # Cancel tasks
            for task in [self._update_task, self._content_task, self._monitoring_task]:
                if task:
                    task.cancel()

            # Wait for shutdown
            await asyncio.sleep(1.0)

            self.status = DisplayStatus.READY
            self._shutdown_event.clear()
            print("Display interface stopped")
            return True

        except Exception as e:
            self.status = DisplayStatus.ERROR
            print(f"Error stopping display interface: {e}")
            return False

    async def show_page(
        self, page: DisplayPage, custom_content: Optional[List[str]] = None
    ) -> bool:
        """Show a standard display page."""
        if page not in self.page_templates:
            print(f"Unknown page: {page}")
            return False

        template = self.page_templates[page]

        # Use custom content if provided
        if custom_content:
            content = DisplayContent(
                page=page,
                lines=custom_content,
                priority=template.priority,
                duration_seconds=template.duration_seconds,
                blink_lines=template.blink_lines,
                scroll_lines=template.scroll_lines,
                metadata=template.metadata,
            )
        else:
            content = template

        # Validate content
        if not content.validate(self.config):
            print(f"Content validation failed for page: {page}")
            return False

        # Add to queue based on priority
        self._add_to_queue(content)

        # Update current page
        self.current_page = page

        print(f"Display page queued: {page.name}")
        return True

    async def show_text(
        self,
        lines: List[str],
        duration_seconds: Optional[float] = 5.0,
        priority: int = 3,
        blink_lines: Optional[List[int]] = None,
    ) -> bool:
        """Show custom text on display."""
        content = DisplayContent(
            page=DisplayPage.SYSTEM_STATUS,  # Use system status as default
            lines=lines,
            priority=priority,
            duration_seconds=duration_seconds,
            blink_lines=blink_lines,
            scroll_lines=None,
        )

        # Validate content
        if not content.validate(self.config):
            print("Content validation failed")
            return False

        # Add to queue
        self._add_to_queue(content)

        print(f"Custom text queued: {len(lines)} lines, priority {priority}")
        return True

    async def show_emergency(
        self, message: str, details: Optional[List[str]] = None
    ) -> bool:
        """Show emergency message."""
        lines = ["! EMERGENCY !", message]
        if details:
            # Add details, truncating if necessary
            max_detail_lines = self.config.max_lines - 2
            lines.extend(details[:max_detail_lines])

        content = DisplayContent(
            page=DisplayPage.EMERGENCY,
            lines=lines,
            priority=10,  # Highest priority
            duration_seconds=None,  # Stay until cleared
            blink_lines=[0, 1],  # Blink emergency header
            metadata={"emergency": True, "timestamp": datetime.now().isoformat()},
        )

        # Clear queue and show emergency immediately
        self.content_queue = [content]
        self.current_page = DisplayPage.EMERGENCY

        print(f"Emergency displayed: {message}")
        return True

    async def clear_emergency(self) -> bool:
        """Clear emergency display."""
        if self.current_page == DisplayPage.EMERGENCY:
            self.content_queue = []
            await self.show_page(DisplayPage.SYSTEM_STATUS)
            print("Emergency cleared")
            return True
        return False

    async def set_brightness(self, brightness: int) -> bool:
        """Set display brightness."""
        brightness = max(0, min(100, brightness))

        if self.simulation_mode:
            print(f"Setting brightness to {brightness}%")
            self.state.brightness = brightness
            return True
        else:
            # Hardware implementation would go here
            raise NotImplementedError("Hardware brightness control not implemented")

    async def set_backlight(self, on: bool) -> bool:
        """Turn backlight on/off."""
        if self.simulation_mode:
            state = "ON" if on else "OFF"
            print(f"Setting backlight {state}")
            self.state.backlight_on = on
            return True
        else:
            # Hardware implementation would go here
            raise NotImplementedError("Hardware backlight control not implemented")

    async def set_mode(self, mode: DisplayMode) -> bool:
        """Set display mode."""
        print(f"Setting display mode to {mode.name}")
        self.mode = mode
        self.state.mode = mode

        # Mode-specific actions
        if mode == DisplayMode.OFF:
            await self.set_backlight(False)
        elif mode == DisplayMode.DIM:
            await self.set_brightness(self.config.dim_brightness)
        elif mode == DisplayMode.NORMAL:
            await self.set_backlight(True)
            await self.set_brightness(self.config.brightness)

        return True

    def get_status(self) -> DisplayState:
        """Get current display status."""
        return self.state

    def get_metrics(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get performance metrics."""
        history = self.metrics_history[-limit:] if self.metrics_history else []
        return [asdict(metric) for metric in history]

    def get_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get display events."""
        history = self.event_history[-limit:] if self.event_history else []
        return [event.to_dict() for event in history]

    async def _connect_hardware(self) -> None:
        """Connect to display hardware."""
        if self.simulation_mode:
            print(
                f"Simulating hardware connection for {self.config.display_type.name} display"
            )
            await asyncio.sleep(0.5)
            self.hardware_connected = True
        else:
            # Actual hardware connection would go here
            raise NotImplementedError("Hardware connection not implemented")

    async def _initialize_display(self) -> None:
        """Initialize the display hardware or simulation."""
        if self.simulation_mode:
            print(f"Initializing simulated {self.config.display_type.name} display")
            await asyncio.sleep(0.2)

            # Initialize display state based on type
            if self.config.display_type in [DisplayType.LCD_16x2, DisplayType.LCD_20x4]:
                self.state.columns = (
                    16 if self.config.display_type == DisplayType.LCD_16x2 else 20
                )
                self.state.rows = (
                    2 if self.config.display_type == DisplayType.LCD_16x2 else 4
                )
                self.state.resolution = f"{self.state.columns}x{self.state.rows}"
            elif self.config.display_type == DisplayType.OLED_128x64:
                self.state.columns = 128
                self.state.rows = 64
                self.state.resolution = "128x64"
            elif self.config.display_type == DisplayType.TFT_240x320:
                self.state.columns = 240
                self.state.rows = 320
                self.state.resolution = "240x320"
            elif self.config.display_type == DisplayType.TERMINAL:
                self.state.columns = 80
                self.state.rows = 24
                self.state.resolution = "80x24"

            self.state.initialized = True
            print(f"Display initialized: {self.state.resolution}")
        else:
            # Hardware initialization would go here
            raise NotImplementedError("Hardware initialization not implemented")

    async def _update_metrics(self) -> None:
        """Update display performance metrics."""
        current_time = TimeUtils.get_current_time()

        metric = DisplayMetrics(
            timestamp=current_time,
            mode=self.mode,
            brightness=self.state.brightness,
            backlight_on=self.state.backlight_on,
            emergency_active=self.state.emergency_active,
            page_count=len(self.page_history),
            event_count=len(self.event_history),
        )

        self.metrics_history.append(metric)

        # Keep history within limits
        if len(self.metrics_history) > self.config.metrics_history_size:
            self.metrics_history = self.metrics_history[
                -self.config.metrics_history_size :
            ]

    async def _record_event(
        self, event_type: str, message: str, severity: str = "INFO"
    ) -> None:
        """Record a display event."""
        current_time = TimeUtils.get_current_time()

        event = DisplayEvent(
            timestamp=current_time,
            event_type=event_type,
            message=message,
            severity=severity,
        )

        self.event_history.append(event)

        # Keep history within limits
        if len(self.event_history) > self.config.event_history_size:
            self.event_history = self.event_history[-self.config.event_history_size :]

    async def _render_page(self, page: DisplayPage) -> None:
        """Render a page to the display."""
        if self.simulation_mode:
            print(f"\n{'=' * 40}")
            print(f"DISPLAY: {page.title}")
            print(f"{'=' * 40}")

            if page.content:
                for line in page.content.split("\n"):
                    print(f"  {line}")

            if page.metadata:
                print(f"\nMetadata:")
                for key, value in page.metadata.items():
                    print(f"  {key}: {value}")

            print(f"{'=' * 40}\n")
        else:
            # Hardware rendering would go here
            raise NotImplementedError("Hardware rendering not implemented")

    async def _validate_content(self, content: DisplayContent) -> bool:
        """Validate display content before rendering."""
        if not content.validate():
            return False

        # Check content length against display capabilities
        if self.config.display_type in [DisplayType.LCD_16x2, DisplayType.LCD_20x4]:
            max_chars = self.state.columns * self.state.rows
            content_chars = len(content.text)
            if content_chars > max_chars:
                print(
                    f"Warning: Content ({content_chars} chars) exceeds display capacity ({max_chars} chars)"
                )
                return False

        return True

    async def _maintain_display(self) -> None:
        """Perform display maintenance tasks."""
        if not self.simulation_mode:
            # Hardware maintenance would go here
            # This could include:
            # - Clearing stuck pixels
            # - Adjusting contrast
            # - Checking backlight health
            # - Updating firmware if needed
            pass

        # Update metrics
        await self._update_metrics()

        # Check for stale emergency messages
        if self.state.emergency_active:
            current_time = TimeUtils.get_current_time()
            emergency_age = (
                current_time - self.state.emergency_timestamp
            ).total_seconds()
            if emergency_age > self.config.emergency_timeout:
                await self.clear_emergency()
                await self._record_event(
                    "EMERGENCY_CLEARED", "Emergency message timed out", "WARNING"
                )

    async def _cleanup(self) -> None:
        """Clean up display resources."""
        if self.simulation_mode:
            print("Cleaning up simulated display")
        else:
            # Hardware cleanup would go here
            # This could include:
            # - Turning off backlight
            # - Clearing display
            # - Releasing GPIO pins
            # - Closing serial connections
            pass

        self.state.running = False
        self.hardware_connected = False
        self.state.initialized = False

    def __del__(self) -> None:
        """Destructor to ensure cleanup."""
        if self.state.running:
            print("Warning: DisplayInterface destroyed while still running")
