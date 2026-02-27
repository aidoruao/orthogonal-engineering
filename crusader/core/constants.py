"""
Crusader Combat Refrigerator - Constants
Version: 1.0.0
Schema ID: CRUSADER-1.0
Author: Orthogonal Engineering Framework
License: AGAPE (Free Forever)

System-wide constants for the Crusader combat refrigerator.
"""

import math
from enum import Enum, IntEnum
from typing import Dict, List, Tuple

# ============================================================================
# GPIO PIN CONSTANTS
# ============================================================================


class GPIOPins(IntEnum):
    """GPIO pin assignments for Raspberry Pi."""

    # Warfare Systems
    SPRAYER_PUMP = 17  # Peristaltic pump control
    UV_LED_ARRAY = 27  # UV-C LED array control
    FAN_MOTOR = 22  # Brushless DC fan control
    STICKY_TRAP_SENSOR = 5  # Sticky trap monitoring

    # Monitoring Systems
    TEMPERATURE_SENSOR = 4  # DS18B20 temperature sensor
    HUMIDITY_SENSOR = 17  # DHT22 humidity sensor (shared with sprayer)
    MOTION_SENSOR = 27  # PIR motion sensor (shared with UV)
    DOOR_SENSOR = 22  # Magnetic door sensor (shared with fan)

    # Control Systems
    EMERGENCY_STOP = 23  # Emergency stop button
    SYSTEM_LED = 24  # Status LED
    BUZZER = 25  # Audible alert buzzer

    # Power Management
    SENSOR_POWER_ENABLE = 18  # 3.3V regulator enable
    PUMP_POWER_ENABLE = 19  # 12V pump power enable
    UV_POWER_ENABLE = 20  # 5V UV power enable
    FAN_POWER_ENABLE = 21  # 12V fan power enable


# ============================================================================
# TIME CONSTANTS (seconds)
# ============================================================================


class TimeConstants:
    """Time-related constants in seconds."""

    # System Timing
    MAIN_CYCLE_INTERVAL = 60.0  # Main control loop interval
    SENSOR_POLL_INTERVAL = 60.0  # Sensor polling interval
    HEALTH_CHECK_INTERVAL = 300.0  # System health check interval
    WITNESS_UPDATE_INTERVAL = 3600.0  # Witness hash update interval

    # Warfare Timing
    SPORE_DEPLOYMENT_INTERVAL = 3600.0  # Default spore deployment interval
    SPORE_DEPLOYMENT_DURATION = 5.0  # Spore deployment duration
    UV_STERILIZATION_INTERVAL = 7200.0  # UV sterilization interval
    UV_STERILIZATION_DURATION = 30.0  # UV sterilization duration
    AIR_CURTAIN_DURATION = 60.0  # Air curtain activation duration
    STICKY_TRAP_CHECK_INTERVAL = 3600.0  # Sticky trap monitoring interval

    # Maintenance Timing
    CALIBRATION_INTERVAL = 86400.0  # 24 hours
    COMPREHENSIVE_CHECK_INTERVAL = 3600.0  # 1 hour
    BACKUP_INTERVAL = 86400.0  # 24 hours

    # Safety Timing
    EMERGENCY_SHUTDOWN_DELAY = 2.0  # Emergency shutdown delay
    DEBOUNCE_TIME = 0.05  # 50ms debounce for switches
    WATCHDOG_TIMEOUT = 30.0  # Watchdog timeout

    # Pattern Timing
    MORNING_PATTERN_START = 6 * 3600  # 06:00 in seconds
    MORNING_PATTERN_END = 8 * 3600  # 08:00 in seconds
    EVENING_PATTERN_START = 18 * 3600  # 18:00 in seconds
    EVENING_PATTERN_END = 20 * 3600  # 20:00 in seconds


# ============================================================================
# ENVIRONMENTAL CONSTANTS
# ============================================================================


class EnvironmentalConstants:
    """Environmental and biological constants."""

    # Temperature Ranges (°C)
    OPTIMAL_TEMPERATURE = 25.0  # Optimal for Beauveria bassiana
    MIN_TEMPERATURE = 2.0  # Minimum safe temperature
    MAX_TEMPERATURE = 40.0  # Maximum safe temperature
    CRITICAL_TEMPERATURE_HIGH = 35.0  # Critical high temperature
    CRITICAL_TEMPERATURE_LOW = 3.0  # Critical low temperature

    # Humidity Ranges (%)
    OPTIMAL_HUMIDITY = 70.0  # Optimal for Beauveria bassiana
    MIN_HUMIDITY = 30.0  # Minimum safe humidity
    MAX_HUMIDITY = 80.0  # Maximum safe humidity
    CRITICAL_HUMIDITY_HIGH = 75.0  # Critical high humidity
    CRITICAL_HUMIDITY_LOW = 35.0  # Critical low humidity

    # Biological Constants
    SPORE_VIABILITY_THRESHOLD = 0.8  # 80% viability required
    SPORE_CONCENTRATION = 0.1  # 0.1% spore concentration
    SPORE_SHELF_LIFE_DAYS = 30  # Spore solution shelf life

    # UV Sterilization
    UV_WAVELENGTH_NM = 275  # UVC wavelength
    UV_EXPOSURE_THRESHOLD = 300  # Max daily exposure in seconds
    UV_INTENSITY_THRESHOLD = 1000  # Minimum intensity in µW/cm²

    # Air Quality
    CO2_THRESHOLD_PPM = 1000  # CO2 threshold
    VOC_THRESHOLD_PPB = 500  # VOC threshold


# ============================================================================
# HARDWARE CONSTANTS
# ============================================================================


class HardwareConstants:
    """Hardware specifications and limits."""

    # Pump Specifications
    PUMP_FLOW_RATE_ML_PER_MIN = 10.0  # Peristaltic pump flow rate
    PUMP_MAX_PRESSURE_PSI = 30.0  # Maximum pressure
    RESERVOIR_CAPACITY_ML = 1000.0  # Spore reservoir capacity
    LOW_RESERVOIR_THRESHOLD_ML = 100.0  # Low reservoir warning

    # Fan Specifications
    FAN_MIN_RPM = 1000  # Minimum fan speed
    FAN_MAX_RPM = 5000  # Maximum fan speed
    FAN_PWM_FREQUENCY = 25000  # PWM frequency in Hz
    FAN_CURRENT_LIMIT_AMPS = 2.0  # Current limit

    # UV LED Specifications
    UV_LED_POWER_MW = 1000  # UV LED power
    UV_LED_BEAM_ANGLE = 60  # Beam angle in degrees
    UV_LED_EFFICIENCY = 0.3  # Electrical to optical efficiency

    # Power Specifications
    SYSTEM_VOLTAGE = 12.0  # Main system voltage
    SENSOR_VOLTAGE = 3.3  # Sensor voltage
    UV_VOLTAGE = 5.0  # UV LED voltage
    MAX_SYSTEM_CURRENT_AMPS = 5.0  # Maximum system current

    # PCB Specifications
    PCB_THICKNESS_MM = 1.6  # PCB thickness
    COPPER_WEIGHT_OZ = 1.0  # Copper weight
    MIN_TRACE_WIDTH_MM = 0.2  # Minimum trace width
    MIN_CLEARANCE_MM = 0.2  # Minimum clearance


# ============================================================================
# SYSTEM LIMITS AND THRESHOLDS
# ============================================================================


class SystemLimits:
    """System operational limits and thresholds."""

    # Cycle Limits
    MAX_CYCLES_PER_DAY = 1440  # 24 hours * 60 minutes
    MAX_SPORE_DEPLOYMENTS_PER_DAY = 24  # Maximum deployments per day
    MAX_UV_CYCLES_PER_DAY = 12  # Maximum UV cycles per day

    # Fly Detection
    FLY_COUNT_HIGH_THRESHOLD = 50  # High fly count warning
    FLY_COUNT_CRITICAL_THRESHOLD = 100  # Critical fly count
    DETECTION_CONFIDENCE_THRESHOLD = 0.7  # 70% confidence required

    # Error Thresholds
    MAX_ERRORS_PER_HOUR = 10  # Maximum errors per hour
    MAX_CONSECUTIVE_FAILURES = 3  # Maximum consecutive failures
    SYSTEM_ERROR_THRESHOLD = 100  # Total system errors before shutdown

    # Performance Thresholds
    MIN_SUCCESS_RATE = 0.95  # 95% minimum success rate
    MAX_RESPONSE_TIME_MS = 1000  # Maximum response time
    MIN_UPTIME_PERCENT = 99.9  # 99.9% minimum uptime

    # Resource Thresholds
    MEMORY_USAGE_THRESHOLD = 0.8  # 80% memory usage warning
    CPU_USAGE_THRESHOLD = 0.7  # 70% CPU usage warning
    DISK_USAGE_THRESHOLD = 0.9  # 90% disk usage warning


# ============================================================================
# MATHEMATICAL CONSTANTS
# ============================================================================


class MathematicalConstants:
    """Mathematical and conversion constants."""

    # Conversion Factors
    CELSIUS_TO_KELVIN = 273.15
    ML_TO_LITERS = 0.001
    SECONDS_TO_HOURS = 1 / 3600
    SECONDS_TO_DAYS = 1 / 86400

    # Physical Constants
    STANDARD_PRESSURE_PA = 101325  # Standard atmospheric pressure
    GAS_CONSTANT = 8.314462618  # Ideal gas constant J/(mol·K)
    AVOGADRO_NUMBER = 6.02214076e23  # Avogadro's number

    # Geometric Constants
    PI = math.pi
    E = math.e
    GOLDEN_RATIO = 1.618033988749895

    # Statistical Constants
    CONFIDENCE_95_Z_SCORE = 1.96
    CONFIDENCE_99_Z_SCORE = 2.576
    STANDARD_NORMAL_MEAN = 0.0
    STANDARD_NORMAL_STD = 1.0


# ============================================================================
# PATTERN CONSTANTS
# ============================================================================


class PatternConstants:
    """Deployment pattern constants."""

    # Pattern Intensities
    INTENSITY_LOW = 0.3
    INTENSITY_MEDIUM = 0.6
    INTENSITY_HIGH = 1.0

    # Pattern Durations (seconds)
    SHORT_PATTERN_DURATION = 30
    MEDIUM_PATTERN_DURATION = 60
    LONG_PATTERN_DURATION = 300

    # Pattern Probabilities
    RANDOM_PATTERN_PROBABILITY = 0.1  # 10% chance
    ADAPTIVE_PATTERN_THRESHOLD = 5  # Fly count threshold

    # Pattern Sequences
    MORNING_SEQUENCE = ["defense", "circulation", "defense"]
    EVENING_SEQUENCE = ["circulation", "defense", "purge"]
    ADAPTIVE_SEQUENCE = ["defense", "circulation"]


# ============================================================================
# CRYPTOGRAPHIC CONSTANTS
# ============================================================================


class CryptographicConstants:
    """Cryptographic and hash constants."""

    # Hash Algorithms
    HASH_ALGORITHM = "sha256"
    HASH_DIGEST_SIZE = 32  # 256 bits = 32 bytes
    MERKLE_TREE_DEPTH = 8

    # Witness Constants
    WITNESS_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    WITNESS_SALT_SIZE = 16  # 128-bit salt
    WITNESS_NONCE_SIZE = 8  # 64-bit nonce

    # Signature Constants (if enabled)
    SIGNATURE_ALGORITHM = "ECDSA"
    CURVE_NAME = "secp256k1"
    SIGNATURE_SIZE = 64  # 64 bytes for ECDSA

    # Key Constants
    PUBLIC_KEY_SIZE = 33  # Compressed public key
    PRIVATE_KEY_SIZE = 32  # 256-bit private key


# ============================================================================
# FILE AND PATH CONSTANTS
# ============================================================================


class FileConstants:
    """File system and path constants."""

    # Directory Paths
    LOG_DIRECTORY = "./monitoring/logs/"
    CONFIG_DIRECTORY = "./core/"
    DATA_DIRECTORY = "./monitoring/data/"
    BACKUP_DIRECTORY = "./backups/"
    WITNESS_DIRECTORY = "./monitoring/logs/witness/"

    # File Names
    CONFIG_FILE = "config.yaml"
    CONSTANTS_FILE = "constants.py"
    MAIN_FILE = "main.py"
    AUDIT_LOG_FILE = "audit.log"
    ERROR_LOG_FILE = "error.log"
    OPERATION_LOG_FILE = "operation.log"
    WITNESS_LOG_FILE = "merkle_updates.log"

    # File Extensions
    PYTHON_EXTENSION = ".py"
    YAML_EXTENSION = ".yaml"
    JSON_EXTENSION = ".json"
    LOG_EXTENSION = ".log"
    CSV_EXTENSION = ".csv"

    # File Size Limits (bytes)
    MAX_LOG_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
    MAX_CONFIG_FILE_SIZE = 1 * 1024 * 1024  # 1 MB
    MAX_DATA_FILE_SIZE = 100 * 1024 * 1024  # 100 MB


# ============================================================================
# ENUMERATIONS
# ============================================================================


class SystemMode(Enum):
    """System operational modes."""

    ACTIVE = "active"  # Full operational mode
    STANDBY = "standby"  # Reduced power mode
    SERVICE = "service"  # Maintenance mode
    SAFE = "safe"  # Safe/error mode
    SHUTDOWN = "shutdown"  # Shutdown mode


class DeploymentIntensity(Enum):
    """Deployment intensity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    MAX = "max"


class SensorType(Enum):
    """Sensor types."""

    TEMPERATURE = "temperature"
    HUMIDITY = "humidity"
    MOTION = "motion"
    OPTICAL = "optical"
    DOOR = "door"
    PRESSURE = "pressure"
    CO2 = "co2"
    VOC = "voc"


class AlertLevel(Enum):
    """Alert severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


# ============================================================================
# COLOR CONSTANTS (for display/LED)
# ============================================================================


class ColorConstants:
    """Color constants for display and LEDs."""

    # RGB Colors (0-255)
    GREEN = (0, 255, 0)  # Normal operation
    YELLOW = (255, 255, 0)  # Warning
    RED = (255, 0, 0)  # Error
    BLUE = (0, 0, 255)  # Service mode
    WHITE = (255, 255, 255)  # Active
    OFF = (0, 0, 0)  # Off

    # Display Colors
    BACKGROUND = (0, 0, 0)
    TEXT = (255, 255, 255)
    HIGHLIGHT = (0, 255, 255)
    WARNING_TEXT = (255, 255, 0)
    ERROR_TEXT = (255, 0, 0)


# ============================================================================
# AUDIO CONSTANTS
# ============================================================================


class AudioConstants:
    """Audio alert constants."""

    # Frequencies (Hz)
    BEEP_FREQUENCY = 1000
    WARNING_FREQUENCY = 2000
    ERROR_FREQUENCY = 3000
    ALARM_FREQUENCY = 4000

    # Durations (ms)
    SHORT_BEEP_DURATION = 100
    MEDIUM_BEEP_DURATION = 500
    LONG_BEEP_DURATION = 1000

    # Patterns
    SINGLE_BEEP = [100]
    DOUBLE_BEEP = [100, 100]
    TRIPLE_BEEP = [100, 100, 100]
    SOS_PATTERN = [100, 100, 100, 300, 300, 300, 100, 100, 100]


# ============================================================================
# EXPORT ALL CONSTANTS
# ============================================================================

# Create dictionaries for easy access
GPIO_PINS = {pin.name: pin.value for pin in GPIOPins}
TIME_CONSTANTS = {
    k: v for k, v in TimeConstants.__dict__.items() if not k.startswith("_")
}
ENVIRONMENTAL_CONSTANTS = {
    k: v for k, v in EnvironmentalConstants.__dict__.items() if not k.startswith("_")
}
HARDWARE_CONSTANTS = {
    k: v for k, v in HardwareConstants.__dict__.items() if not k.startswith("_")
}
SYSTEM_LIMITS = {
    k: v for k, v in SystemLimits.__dict__.items() if not k.startswith("_")
}
MATH_CONSTANTS = {
    k: v for k, v in MathematicalConstants.__dict__.items() if not k.startswith("_")
}
PATTERN_CONSTANTS = {
    k: v for k, v in PatternConstants.__dict__.items() if not k.startswith("_")
}
CRYPTO_CONSTANTS = {
    k: v for k, v in CryptographicConstants.__dict__.items() if not k.startswith("_")
}
FILE_CONSTANTS = {
    k: v for k, v in FileConstants.__dict__.items() if not k.startswith("_")
}


# Combined constants dictionary for easy access (lazy evaluation)
def get_all_constants():
    """Get all constants as a dictionary (lazy evaluation to avoid circular dependencies)."""
    return {
        "environmental": ENVIRONMENTAL_CONSTANTS,
        "time": TIME_CONSTANTS,
        "hardware": HARDWARE_CONSTANTS,
        "system_limits": SYSTEM_LIMITS,
        "math": MATH_CONSTANTS,
        "patterns": PATTERN_CONSTANTS,
        "crypto": CRYPTO_CONSTANTS,
        "files": FILE_CONSTANTS,
    }


ALL_CONSTANTS = get_all_constants()

# Export all constants
__all__ = [
    "EnvironmentalConstants",
    "TimeConstants",
    "HardwareConstants",
    "SystemLimits",
    "MathematicalConstants",
    "PatternConstants",
    "CryptographicConstants",
    "FileConstants",
    "ENVIRONMENTAL_CONSTANTS",
    "TIME_CONSTANTS",
    "HARDWARE_CONSTANTS",
    "SYSTEM_LIMITS",
    "MATH_CONSTANTS",
    "PATTERN_CONSTANTS",
    "CRYPTO_CONSTANTS",
    "FILE_CONSTANTS",
    "ALL_CONSTANTS",
    "get_all_constants",
]

if __name__ == "__main__":
    print("Crusader Combat Refrigerator - Constants Module")
    print(f"Version: {SYSTEM_LIMITS.get('VERSION', '1.0.0')}")
    print(f"Total constants: {sum(len(c) for c in get_all_constants().values())}")
    print("Constants loaded successfully.")
