"""
Crusader Combat Refrigerator - Time Utilities
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

Time utility functions for scheduling, timing, and temporal operations.
"""

import asyncio
import calendar
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum, auto
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# Optional import for timezone support
try:
    import pytz
except ImportError:
    pytz = None


class TimeUnit(Enum):
    """Time units for scheduling."""

    MILLISECONDS = auto()
    SECONDS = auto()
    MINUTES = auto()
    HOURS = auto()
    DAYS = auto()
    WEEKS = auto()


class ScheduleType(Enum):
    """Types of schedules."""

    INTERVAL = auto()  # Fixed interval
    CRON = auto()  # Cron-like schedule
    ONCE = auto()  # One-time execution
    DAILY = auto()  # Daily at specific time
    WEEKLY = auto()  # Weekly on specific day/time
    MONTHLY = auto()  # Monthly on specific day/time
    YEARLY = auto()  # Yearly on specific date/time


@dataclass
class ScheduledTask:
    """Scheduled task definition."""

    task_id: str
    name: str
    schedule_type: ScheduleType
    schedule_config: Dict[str, Any]
    callback: Callable
    enabled: bool = True
    last_execution: Optional[datetime] = None
    next_execution: Optional[datetime] = None
    execution_count: int = 0
    error_count: int = 0
    max_retries: int = 3
    timeout_seconds: float = 30.0
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class TimerResult:
    """Timer execution result."""

    task_id: str
    start_time: datetime
    end_time: datetime
    duration_seconds: float
    success: bool
    error: Optional[str] = None
    result: Optional[Any] = None


class Scheduler:
    """
    Advanced scheduler for timing and scheduling operations.
    Supports interval-based, cron-like, and calendar-based scheduling.
    """

    def __init__(self):
        """Initialize the scheduler."""
        self.tasks: Dict[str, ScheduledTask] = {}
        self.running = False
        self.scheduler_task: Optional[asyncio.Task] = None
        self.task_lock = asyncio.Lock()

        # Timezone support (simplified - would use pytz in production)
        self.timezone_offset = 0  # UTC offset in hours

        # Statistics
        self.statistics = {
            "total_tasks_executed": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "average_execution_time_ms": 0.0,
            "total_execution_time_seconds": 0.0,
        }

    def initialize(self):
        """Initialize the scheduler."""
        print("🔧 Initializing Scheduler...")
        self.running = True
        self.scheduler_task = asyncio.create_task(self._scheduler_loop())
        print("✅ Scheduler initialized")

    async def shutdown(self):
        """Shutdown the scheduler."""
        print("🔴 Shutting down Scheduler...")
        self.running = False

        if self.scheduler_task and not self.scheduler_task.done():
            self.scheduler_task.cancel()
            try:
                await self.scheduler_task
            except asyncio.CancelledError:
                pass

        # Cancel all pending tasks
        async with self.task_lock:
            self.tasks.clear()

        print("✅ Scheduler shutdown complete")

    async def _scheduler_loop(self):
        """Main scheduler loop."""
        while self.running:
            try:
                await self._check_and_execute_tasks()
                await asyncio.sleep(1)  # Check every second
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"❌ Error in scheduler loop: {e}")
                await asyncio.sleep(5)  # Wait before retry

    async def _check_and_execute_tasks(self):
        """Check and execute due tasks."""
        current_time = datetime.now()
        tasks_to_execute = []

        async with self.task_lock:
            for task_id, task in self.tasks.items():
                if not task.enabled:
                    continue

                if task.next_execution and current_time >= task.next_execution:
                    tasks_to_execute.append(task)

        # Execute tasks
        for task in tasks_to_execute:
            asyncio.create_task(self._execute_task(task))

    async def _execute_task(self, task: ScheduledTask):
        """Execute a scheduled task."""
        task.last_execution = datetime.now()
        task.execution_count += 1

        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                task.callback(task.metadata), timeout=task.timeout_seconds
            )

            # Update task
            async with self.task_lock:
                task.next_execution = self._calculate_next_execution(task)
                task.error_count = 0

            # Update statistics
            self.statistics["total_tasks_executed"] += 1
            self.statistics["successful_executions"] += 1

            print(f"✅ Executed task: {task.name}")

        except asyncio.TimeoutError:
            await self._handle_task_error(task, "Task timeout")
        except Exception as e:
            await self._handle_task_error(task, str(e))

    async def _handle_task_error(self, task: ScheduledTask, error_message: str):
        """Handle task execution error."""
        task.error_count += 1
        self.statistics["failed_executions"] += 1

        print(f"❌ Task {task.name} failed: {error_message}")

        # Check if we should retry
        if task.error_count <= task.max_retries:
            print(
                f"🔄 Retrying task {task.name} ({task.error_count}/{task.max_retries})"
            )
            # Schedule retry with exponential backoff
            retry_delay = min(300, 2**task.error_count)  # Max 5 minutes
            await asyncio.sleep(retry_delay)
            asyncio.create_task(self._execute_task(task))
        else:
            print(f"🛑 Task {task.name} failed after {task.max_retries} retries")
            # Disable task
            async with self.task_lock:
                task.enabled = False

    def _calculate_next_execution(self, task: ScheduledTask) -> Optional[datetime]:
        """Calculate next execution time for a task."""
        current_time = datetime.now()

        if task.schedule_type == ScheduleType.INTERVAL:
            interval = task.schedule_config.get("interval_seconds", 60)
            return current_time + timedelta(seconds=interval)

        elif task.schedule_type == ScheduleType.DAILY:
            hour = task.schedule_config.get("hour", 0)
            minute = task.schedule_config.get("minute", 0)
            next_time = current_time.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

            if next_time <= current_time:
                next_time += timedelta(days=1)

            return next_time

        elif task.schedule_type == ScheduleType.WEEKLY:
            weekday = task.schedule_config.get("weekday", 0)  # 0=Monday, 6=Sunday
            hour = task.schedule_config.get("hour", 0)
            minute = task.schedule_config.get("minute", 0)

            current_weekday = current_time.weekday()
            days_ahead = weekday - current_weekday

            if days_ahead <= 0:  # Target day already passed this week
                days_ahead += 7

            next_time = current_time + timedelta(days=days_ahead)
            next_time = next_time.replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

            return next_time

        elif task.schedule_type == ScheduleType.ONCE:
            # One-time tasks don't have next execution
            return None

        # Default: no next execution
        return None

    def schedule_interval(
        self,
        name: str,
        callback: Callable,
        interval_seconds: float,
        metadata: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
    ) -> str:
        """
        Schedule a task to run at fixed intervals.

        Returns:
            Task ID for tracking
        """
        import uuid

        task_id = str(uuid.uuid4())

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            schedule_type=ScheduleType.INTERVAL,
            schedule_config={"interval_seconds": interval_seconds},
            callback=callback,
            metadata=metadata,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            next_execution=datetime.now() + timedelta(seconds=interval_seconds),
        )

        async def add_task():
            async with self.task_lock:
                self.tasks[task_id] = task

        # Run in event loop
        asyncio.create_task(add_task())

        print(f"📅 Scheduled interval task: {name} (every {interval_seconds}s)")
        return task_id

    def schedule_daily(
        self,
        name: str,
        callback: Callable,
        hour: int,
        minute: int = 0,
        metadata: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
    ) -> str:
        """
        Schedule a task to run daily at specific time.

        Args:
            hour: 0-23
            minute: 0-59
        """
        import uuid

        task_id = str(uuid.uuid4())

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            schedule_type=ScheduleType.DAILY,
            schedule_config={"hour": hour, "minute": minute},
            callback=callback,
            metadata=metadata,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

        # Calculate first execution
        task.next_execution = self._calculate_next_execution(task)

        async def add_task():
            async with self.task_lock:
                self.tasks[task_id] = task

        asyncio.create_task(add_task())

        print(f"📅 Scheduled daily task: {name} at {hour:02d}:{minute:02d}")
        return task_id

    def schedule_once(
        self,
        name: str,
        callback: Callable,
        delay_seconds: float = 0,
        metadata: Optional[Dict[str, Any]] = None,
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
    ) -> str:
        """
        Schedule a one-time task.

        Args:
            delay_seconds: Delay before execution (0 for immediate)
        """
        import uuid

        task_id = str(uuid.uuid4())

        task = ScheduledTask(
            task_id=task_id,
            name=name,
            schedule_type=ScheduleType.ONCE,
            schedule_config={"delay_seconds": delay_seconds},
            callback=callback,
            metadata=metadata,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            next_execution=datetime.now() + timedelta(seconds=delay_seconds),
        )

        async def add_task():
            async with self.task_lock:
                self.tasks[task_id] = task

        asyncio.create_task(add_task())

        print(f"📅 Scheduled one-time task: {name} (in {delay_seconds}s)")
        return task_id

    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a scheduled task."""
        async with self.task_lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                print(f"❌ Cancelled task: {task_id}")
                return True
            return False

    def enable_task(self, task_id: str) -> bool:
        """Enable a disabled task."""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = True
            # Recalculate next execution
            self.tasks[task_id].next_execution = self._calculate_next_execution(
                self.tasks[task_id]
            )
            return True
        return False

    def disable_task(self, task_id: str) -> bool:
        """Disable a task."""
        if task_id in self.tasks:
            self.tasks[task_id].enabled = False
            return True
        return False

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a task."""
        task = self.tasks.get(task_id)
        if not task:
            return None

        return {
            "task_id": task.task_id,
            "name": task.name,
            "enabled": task.enabled,
            "schedule_type": task.schedule_type.name,
            "last_execution": task.last_execution.isoformat()
            if task.last_execution
            else None,
            "next_execution": task.next_execution.isoformat()
            if task.next_execution
            else None,
            "execution_count": task.execution_count,
            "error_count": task.error_count,
            "max_retries": task.max_retries,
        }

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get status of all tasks."""
        return [self.get_task_status(task_id) for task_id in self.tasks.keys()]

    def get_statistics(self) -> Dict[str, Any]:
        """Get scheduler statistics."""
        return self.statistics.copy()


def timer_decorator(name: Optional[str] = None):
    """
    Decorator to time function execution.

    Usage:
        @timer_decorator("my_function")
        async def my_function():
            ...
    """

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            task_id = f"{name or func.__name__}_{int(start_time)}"

            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                print(f"⏱️  {name or func.__name__} completed in {duration:.3f}s")
                return TimerResult(
                    task_id=task_id,
                    start_time=datetime.fromtimestamp(start_time),
                    end_time=datetime.fromtimestamp(start_time + duration),
                    duration_seconds=duration,
                    success=True,
                    result=result,
                )

            except Exception as e:
                duration = time.time() - start_time
                print(f"⏱️  {name or func.__name__} failed after {duration:.3f}s: {e}")

                return TimerResult(
                    task_id=task_id,
                    start_time=datetime.fromtimestamp(start_time),
                    end_time=datetime.fromtimestamp(start_time + duration),
                    duration_seconds=duration,
                    success=False,
                    error=str(e),
                )

        return wrapper

    return decorator


class Timer:
    """Simple timer for measuring execution time."""

    def __init__(self):
        """Initialize timer."""
        self.start_time = None
        self.end_time = None

    def start(self):
        """Start the timer."""
        self.start_time = time.perf_counter()
        self.end_time = None

    def stop(self):
        """Stop the timer."""
        self.end_time = time.perf_counter()

    def elapsed(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        if self.end_time is None:
            return time.perf_counter() - self.start_time
        return self.end_time - self.start_time

    def reset(self):
        """Reset the timer."""
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()


class TimeUtils:
    """Static time utility functions."""

    @staticmethod
    def get_current_timestamp() -> str:
        """Get current timestamp in ISO format."""
        return datetime.now().isoformat()

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in human-readable format."""
        if seconds < 1:
            return f"{seconds * 1000:.0f}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f}h"
        else:
            days = seconds / 86400
            return f"{days:.1f}d"

    @staticmethod
    def parse_time_string(time_str: str) -> Optional[datetime]:
        """Parse time string in various formats."""
        formats = [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M",
            "%Y-%m-%d",
            "%H:%M:%S",
            "%H:%M",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt)
            except ValueError:
                continue

        return None

    @staticmethod
    def is_time_between(
        start_time: str, end_time: str, current_time: Optional[datetime] = None
    ) -> bool:
        """Check if current time is between two times."""
        if current_time is None:
            current_time = datetime.now()

        start = TimeUtils.parse_time_string(start_time)
        end = TimeUtils.parse_time_string(end_time)

        if not start or not end:
            return False

        # Handle overnight ranges
        if end < start:
            return (
                current_time.time() >= start.time() or current_time.time() <= end.time()
            )
        else:
            return start.time() <= current_time.time() <= end.time()

    @staticmethod
    def calculate_time_until(target_time: Union[datetime, str]) -> float:
        """Calculate seconds until target time."""
        if isinstance(target_time, str):
            target_time = TimeUtils.parse_time_string(target_time)
            if not target_time:
                return float("inf")

        now = datetime.now()
        if target_time <= now:
            return 0

        return (target_time - now).total_seconds()

    @staticmethod
    def get_time_of_day() -> str:
        """Get time of day category."""
        hour = datetime.now().hour

        if 5 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"

    @staticmethod
    def is_weekday() -> bool:
        """Check if today is a weekday."""
        return datetime.now().weekday() < 5

    @staticmethod
    def get_days_in_month(year: int, month: int) -> int:
        """Get number of days in a month."""
        return calendar.monthrange(year, month)[1]

    @staticmethod
    def add_time(
        dt: datetime, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0
    ) -> datetime:
        """Add time to a datetime."""
        return dt + timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def subtract_time(
        dt: datetime, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0
    ) -> datetime:
        """Subtract time from a datetime."""
        return dt - timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)

    @staticmethod
    def time_difference(start: datetime, end: datetime) -> Dict[str, int]:
        """Calculate time difference between two datetimes."""
        diff = end - start
        days = diff.days
        seconds = diff.seconds

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": diff.total_seconds(),
            "total_minutes": diff.total_seconds() / 60,
            "total_hours": diff.total_seconds() / 3600,
            "total_days": diff.total_seconds() / 86400,
        }

    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to human-readable string."""
        if seconds < 60:
            return f"{seconds:.1f} seconds"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f} minutes"
        elif seconds < 86400:
            hours = seconds / 3600
            return f"{hours:.1f} hours"
        else:
            days = seconds / 86400
            return f"{days:.1f} days"

    @staticmethod
    def get_timezone_info() -> Dict[str, Any]:
        """Get timezone information."""
        now = datetime.now()
        return {
            "local_time": now.isoformat(),
            "utc_time": datetime.utcnow().isoformat(),
            "timezone": str(now.astimezone().tzinfo),
            "utc_offset": now.astimezone().utcoffset(),
            "dst_offset": now.astimezone().dst(),
            "is_dst": bool(now.astimezone().dst()),
        }

    @staticmethod
    def convert_timezone(dt: datetime, from_tz: str, to_tz: str) -> datetime:
        """Convert datetime between timezones."""
        try:
            from_zone = pytz.timezone(from_tz)
            to_zone = pytz.timezone(to_tz)

            # Localize the datetime
            localized = from_zone.localize(dt)
            # Convert to target timezone
            converted = localized.astimezone(to_zone)

            return converted
        except Exception as e:
            print(f"❌ Timezone conversion failed: {e}")
            return dt

    @staticmethod
    def get_season(date: Optional[datetime] = None) -> str:
        """Get the season for a given date."""
        if date is None:
            date = datetime.now()

        month = date.month
        day = date.day

        # Northern hemisphere seasons
        if (month == 12 and day >= 21) or (month <= 2) or (month == 3 and day < 20):
            return "winter"
        elif (month == 3 and day >= 20) or (month <= 5) or (month == 6 and day < 21):
            return "spring"
        elif (month == 6 and day >= 21) or (month <= 8) or (month == 9 and day < 23):
            return "summer"
        else:
            return "autumn"

    @staticmethod
    def is_leap_year(year: int) -> bool:
        """Check if a year is a leap year."""
        return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

    @staticmethod
    def get_week_number(date: Optional[datetime] = None) -> int:
        """Get ISO week number for a date."""
        if date is None:
            date = datetime.now()
        return date.isocalendar()[1]

    @staticmethod
    def get_quarter(date: Optional[datetime] = None) -> int:
        """Get quarter of the year for a date."""
        if date is None:
            date = datetime.now()
        return (date.month - 1) // 3 + 1

    @staticmethod
    def get_fiscal_year(date: Optional[datetime] = None, start_month: int = 7) -> int:
        """Get fiscal year for a date."""
        if date is None:
            date = datetime.now()

        year = date.year
        if date.month >= start_month:
            return year + 1
        else:
            return year

    @staticmethod
    def validate_date(year: int, month: int, day: int) -> bool:
        """Validate if a date is valid."""
        try:
            datetime(year, month, day)
            return True
        except ValueError:
            return False

    @staticmethod
    def validate_time(hour: int, minute: int, second: int = 0) -> bool:
        """Validate if a time is valid."""
        return 0 <= hour <= 23 and 0 <= minute <= 59 and 0 <= second <= 59

    @staticmethod
    def get_moon_phase(date: Optional[datetime] = None) -> str:
        """Get approximate moon phase for a date."""
        if date is None:
            date = datetime.now()

        # Simple approximation based on days since known new moon
        # This is a simplified calculation for demonstration
        known_new_moon = datetime(2024, 1, 11)  # Example new moon date
        days_since = (date - known_new_moon).days
        phase_days = days_since % 29.53  # Lunar cycle

        if phase_days < 1:
            return "new moon"
        elif phase_days < 7.4:
            return "waxing crescent"
        elif phase_days < 14.8:
            return "first quarter"
        elif phase_days < 22.1:
            return "waxing gibbous"
        elif phase_days < 29.53:
            return "waning gibbous"
        else:
            return "waning crescent"

    @staticmethod
    def get_astrological_sign(date: Optional[datetime] = None) -> str:
        """Get astrological sign for a date."""
        if date is None:
            date = datetime.now()

        month = date.month
        day = date.day

        if (month == 3 and day >= 21) or (month == 4 and day <= 19):
            return "Aries"
        elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
            return "Taurus"
        elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
            return "Gemini"
        elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
            return "Cancer"
        elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
            return "Leo"
        elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
            return "Virgo"
        elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
            return "Libra"
        elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
            return "Scorpio"
        elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
            return "Sagittarius"
        elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
            return "Capricorn"
        elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
            return "Aquarius"
        else:
            return "Pisces"

    @staticmethod
    def get_chinese_zodiac(year: int) -> str:
        """Get Chinese zodiac animal for a year."""
        animals = [
            "Rat",
            "Ox",
            "Tiger",
            "Rabbit",
            "Dragon",
            "Snake",
            "Horse",
            "Goat",
            "Monkey",
            "Rooster",
            "Dog",
            "Pig",
        ]
        return animals[(year - 1900) % 12]

    @staticmethod
    def get_day_of_year(date: Optional[datetime] = None) -> int:
        """Get day of year for a date."""
        if date is None:
            date = datetime.now()
        return date.timetuple().tm_yday

    @staticmethod
    def get_seconds_since_midnight(date: Optional[datetime] = None) -> int:
        """Get seconds since midnight for a date."""
        if date is None:
            date = datetime.now()
        return date.hour * 3600 + date.minute * 60 + date.second

    @staticmethod
    def format_timestamp(
        timestamp: float, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """Format a Unix timestamp to string."""
        return datetime.fromtimestamp(timestamp).strftime(format_str)

    @staticmethod
    def parse_timestamp(
        timestamp_str: str, format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> datetime:
        """Parse a timestamp string to datetime."""
        return datetime.strptime(timestamp_str, format_str)

    @staticmethod
    def get_iso_week_date(date: Optional[datetime] = None) -> Dict[str, int]:
        """Get ISO week date components."""
        if date is None:
            date = datetime.now()

        iso_year, iso_week, iso_day = date.isocalendar()
        return {
            "iso_year": iso_year,
            "iso_week": iso_week,
            "iso_day": iso_day,
        }

    @staticmethod
    def get_epoch_time(date: Optional[datetime] = None) -> float:
        """Get Unix epoch time for a date."""
        if date is None:
            date = datetime.now()
        return date.timestamp()

    @staticmethod
    def from_epoch_time(epoch_time: float) -> datetime:
        """Create datetime from Unix epoch time."""
        return datetime.fromtimestamp(epoch_time)

    @staticmethod
    def get_microsecond_precision() -> int:
        """Get current time with microsecond precision."""
        return datetime.now().microsecond

    @staticmethod
    def sleep(seconds: float):
        """Sleep for specified seconds."""
        time.sleep(seconds)

    @staticmethod
    def sleep_ms(milliseconds: float):
        """Sleep for specified milliseconds."""
        time.sleep(milliseconds / 1000.0)

    @staticmethod
    def measure_execution_time(func: Callable, *args, **kwargs) -> Dict[str, Any]:
        """Measure execution time of a function."""
        start_time = time.perf_counter()
        start_cpu = time.process_time()

        result = func(*args, **kwargs)

        end_time = time.perf_counter()
        end_cpu = time.process_time()

        return {
            "result": result,
            "wall_time_seconds": end_time - start_time,
            "cpu_time_seconds": end_cpu - start_cpu,
            "start_time": start_time,
            "end_time": end_time,
        }

    @staticmethod
    def create_timer() -> "Timer":
        """Create a new timer instance."""
        return Timer()

    @staticmethod
    def create_scheduler() -> "Scheduler":
        """Create a new scheduler instance."""
        return Scheduler()
