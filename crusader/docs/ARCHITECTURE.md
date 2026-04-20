---
tags: [crusader, docs, architecture]
register: documentation
---

# Crusader Combat Refrigerator - Architecture Documentation

## Overview

The Crusader Combat Refrigerator is a Yeshua-compliant, fully transparent, and verifiable system for autonomous fly elimination using Beauveria bassiana spores, UV-C sterilization, and physical barriers. This document outlines the complete system architecture, component interactions, and design principles.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CRUSADER COMBAT REFRIGERATOR              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    CORE     │  │   WARFARE   │  │ MONITORING  │        │
│  │  System     │  │   Systems   │  │   Systems   │        │
│  │  Control    │  │             │  │             │        │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘        │
│         │                │                │                │
│  ┌──────┴────────────────┴────────────────┴──────┐        │
│  │              INTERFACE LAYER                   │        │
│  │        Display, API, Web, Notifications        │        │
│  └────────────────────────────────────────────────┘        │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                HARDWARE ABSTRACTION                   │ │
│  │          Drivers, GPIO, Sensors, Actuators            │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │                WITNESS LAYER                          │ │
│  │      SHA-256, Merkle Trees, Cryptographic Proof       │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Core System (`core/`)

The central nervous system of Crusader, responsible for orchestration, state management, and system coordination.

#### 1.1 Main Control Loop (`core/main.py`)
- **Purpose**: Primary entry point and system orchestrator
- **Responsibilities**:
  - System initialization and shutdown
  - Main scheduling loop (60-second cycles)
  - Subsystem coordination
  - Error handling and recovery
  - Performance monitoring

#### 1.2 State Machine (`core/state_machine/`)
- **Mode Manager (`mode.py`)**: Manages system operational modes (Active, Standby, Service, Safe, Shutdown)
- **Transition Manager (`transitions.py`)**: Handles complex state transitions with validation
- **Error State Manager (`error_states.py`)**: Comprehensive error detection and recovery
- **Audit Logger (`audit.py`)**: Structured logging of all system events

#### 1.3 Utilities (`core/utils/`)
- **Time Utilities (`time_utils.py`)**: Scheduling, timing, and temporal operations
- **Hash Utilities (`hash_utils.py`)**: Cryptographic hashing and Merkle tree operations
- **I/O Utilities (`io_utils.py`)**: File operations, logging, and system interactions

#### 1.4 Diagnostics (`core/diagnostics/`)
- **Memory Diagnostics (`memory_check.py`)**: Memory usage tracking and leak detection
- **Sensor Diagnostics (`sensor_check.py`)**: Sensor validation and calibration
- **Integrity Verification (`integrity_check.py`)**: System integrity and witness validation

### 2. Warfare Systems (`warfare/`)

The combat systems responsible for fly elimination and prevention.

#### 2.1 Spore Deployment System (`spore_deployment.py`)
- **Purpose**: Deploy Beauveria bassiana spores for biological control
- **Components**:
  - Peristaltic pump control with precise volume measurement
  - Spore reservoir management (1000ml capacity)
  - Deployment patterns: Morning, Evening, Adaptive, Random
  - Biological viability tracking and optimization
- **Patterns**:
  - **Morning Pattern**: High-intensity deployment at dawn (06:00-08:00)
  - **Evening Pattern**: Medium-intensity deployment at dusk (18:00-20:00)
  - **Adaptive Pattern**: Triggered by fly count (>5) and humidity (>60%)
  - **Random Pattern**: Stochastic deployment for unpredictability

#### 2.2 UV Sterilization System (`uv_sterilization.py`)
- **Purpose**: UV-C microbial control and sterilization
- **Components**:
  - UV LED array (275nm, 10W)
  - Safety interlocks (door sensor, motion detection)
  - Temperature monitoring and cooling
  - Dose calculation and efficacy tracking
- **Safety Features**:
  - Automatic shutdown on door opening
  - Motion detection for human safety
  - Temperature limits (max 50°C)
  - Daily exposure limits (300 seconds)

#### 2.3 Air Curtain System (`air_curtain.py`)
- **Purpose**: Physical barrier and airflow management
- **Components**:
  - Brushless DC fan with PWM control
  - Airflow patterns: Defense, Circulation, Purge
  - Fly detection integration
  - Power consumption monitoring
- **Patterns**:
  - **Defense Pattern**: High-speed airflow for fly exclusion
  - **Circulation Pattern**: Low-speed air movement for spore distribution
  - **Purge Pattern**: Maximum airflow for rapid air exchange

#### 2.4 Sticky Trap System (`sticky_array.py`)
- **Purpose**: Physical capture and monitoring
- **Components**:
  - 4-position adhesive trap array
  - Optical trap monitoring
  - Replacement scheduling
  - Capture efficiency tracking
- **Positions**: Top-left, Top-right, Bottom-left, Bottom-right

#### 2.5 Fly Counter System (`counter.py`)
- **Purpose**: Fly detection and population monitoring
- **Components**:
  - Optical detection (camera-based)
  - Acoustic sensing (optional)
  - Thermal imaging (optional)
  - Population trend analysis
- **Detection Methods**:
  - **Optical**: High-speed camera with image processing
  - **Acoustic**: Fly wingbeat frequency detection
  - **Thermal**: Body heat signature detection

### 3. Monitoring Systems (`monitoring/`)

Comprehensive monitoring, diagnostics, and verification systems.

#### 3.1 Sensor Manager (`sensors.py`)
- **Purpose**: Unified sensor interface and management
- **Sensor Types**:
  - **Temperature**: DS18B20 (±0.5°C precision)
  - **Humidity**: DHT22 (±2% precision)
  - **Motion**: PIR HC-SR501
  - **Optical**: Raspberry Pi Camera V2
  - **Door**: Magnetic reed switch
- **Features**:
  - Automatic calibration
  - Sensor health monitoring
  - Data validation and smoothing
  - Redundancy and failover

#### 3.2 Witness Layer (`witness.py`)
- **Purpose**: Cryptographic proof of system integrity
- **Components**:
  - SHA-256 hashing engine
  - Merkle tree construction and verification
  - Witness chain (blockchain-like structure)
  - Digital signatures (optional)
- **Features**:
  - Tamper-evident logging
  - Chain of custody
  - Real-time verification
  - Historical integrity validation

#### 3.3 Diagnostics System (`diagnostics.py`)
- **Purpose**: System health monitoring and reporting
- **Components**:
  - Real-time performance metrics
  - Resource utilization tracking
  - Error rate monitoring
  - Predictive failure analysis
- **Metrics**:
  - CPU, memory, disk usage
  - Network connectivity
  - Sensor accuracy
  - System response times

### 4. Interface Layer (`interface/`)

User interaction and system control interfaces.

#### 4.1 Display Interface (`display.py`)
- **Purpose**: Local status display and control
- **Components**:
  - OLED display (128x64)
  - Status indicators (LEDs)
  - Control buttons
  - Audible alerts (buzzer)
- **Display Content**:
  - System status and mode
  - Fly count and elimination statistics
  - Environmental conditions
  - Deployment history

#### 4.2 Web Interface (`web/`)
- **Purpose**: Remote monitoring and control
- **Components**:
  - Flask-based web server
  - Real-time dashboard
  - Historical data visualization
  - REST API (v1)
- **Features**:
  - Responsive design
  - Real-time updates (WebSocket)
  - Data export (CSV, JSON)
  - Multi-user support

#### 4.3 API Interface (`api.py`)
- **Purpose**: Programmatic system control
- **Endpoints**:
  - `/api/v1/status`: System status
  - `/api/v1/sensors`: Sensor readings
  - `/api/v1/deploy`: Manual deployment
  - `/api/v1/config`: Configuration management
- **Authentication**: API key-based (optional)

#### 4.4 Notification System (`notifications/`)
- **Purpose**: Alert and notification delivery
- **Channels**:
  - **Email**: SMTP-based alerts
  - **Slack/Discord**: Webhook integration
  - **SMS**: Twilio integration (optional)
  - **Local**: Display and buzzer alerts

### 5. Hardware Abstraction (`hardware/`)

Hardware interface and driver layer.

#### 5.1 GPIO Management (`pins.yaml`)
- **Purpose**: GPIO pin mapping and configuration
- **Pin Assignments**:
  - Warfare systems: Sprayer (17), UV (27), Fan (22)
  - Monitoring systems: Temperature (4), Humidity (17), Motion (27)
  - Control systems: Emergency stop (23), System LED (24), Buzzer (25)

#### 5.2 Device Drivers (`drivers/`)
- **Sprayer Driver (`sprayer.py`)**: Peristaltic pump control
- **UV Driver (`uvc.py`)**: UV LED array control
- **Fan Driver (`fan.py`)**: Brushless DC fan control
- **Sensor Drivers**: Individual sensor interfaces
- **Watchdog (`watchdog.py`)**: Hardware fail-safe

#### 5.3 Schematics (`schematics/`)
- **PCB Designs**:
  - Main control board (`crusader_main.kicad_pcb`)
  - Spore module (`spore_module.kicad_pcb`)
  - UV module (`uv_module.kicad_pcb`)
  - Fan module (`fan_module.kicad_pcb`)
- **Wiring Diagrams**: Complete system wiring
- **Flow Charts**: System operation sequences

### 6. Witness and Verification (`monitoring/cryptography/`)

Cryptographic verification and integrity systems.

#### 6.1 Hash Engine (`hash_engine.py`)
- **Purpose**: Cryptographic hash computation
- **Algorithms**: SHA-256, SHA-512, SHA3-256, SHA3-512
- **Features**:
  - Salt generation and application
  - HMAC computation
  - Key derivation (PBKDF2)
  - Performance optimization

#### 6.2 Merkle Tree (`merkle_tree.py`)
- **Purpose**: Efficient data integrity verification
- **Features**:
  - Incremental tree construction
  - Proof generation and verification
  - Batch validation
  - Tree rebalancing

#### 6.3 Digital Signatures (`signature.py`)
- **Purpose**: Authentication and non-repudiation
- **Algorithms**: ECDSA (secp256k1)
- **Features**:
  - Key generation and management
  - Signature creation and verification
  - Certificate handling
  - Revocation lists

## Data Flow Architecture

### 1. Sensor Data Flow
```
Sensors → Sensor Manager → Data Validation → Buffer → Monitoring Systems
    ↓
Witness Layer → Cryptographic Hashing → Storage
    ↓
Warfare Systems → Decision Making → Action Execution
```

### 2. Control Flow
```
Main Loop → State Machine → Mode Selection → Subsystem Activation
    ↓
Sensor Reading → Pattern Analysis → Deployment Decision
    ↓
Action Execution → Result Monitoring → Audit Logging
    ↓
Witness Generation → Integrity Verification → Storage
```

### 3. Witness Chain Flow
```
Event Generation → Data Hashing → Merkle Tree Update
    ↓
Chain Extension → Previous Hash Linking → New Block Creation
    ↓
Signature Application → Verification → Storage
    ↓
Periodic Validation → Integrity Checking → Alert Generation
```

## Communication Protocols

### 1. Internal Communication
- **Asynchronous Messaging**: `asyncio` for non-blocking operations
- **Event Bus**: Pub/sub pattern for subsystem communication
- **Shared State**: Thread-safe data structures with locks
- **Message Queues**: For buffered communication

### 2. External Communication
- **REST API**: HTTP/JSON for web interface
- **WebSocket**: Real-time updates for dashboard
- **Serial Protocol**: Hardware device communication
- **File-based**: Configuration and data storage

### 3. Hardware Communication
- **GPIO**: Direct pin control for actuators
- **I2C/SPI**: Sensor communication buses
- **PWM**: Motor and LED control
- **Analog**: Sensor readings

## Security Architecture

### 1. Cryptographic Security
- **Hashing**: SHA-256 for data integrity
- **Merkle Trees**: Efficient integrity verification
- **Digital Signatures**: ECDSA for authentication
- **Key Management**: Secure key storage and rotation

### 2. System Security
- **Process Isolation**: Subsystem separation
- **Resource Limits**: Memory and CPU constraints
- **Input Validation**: All inputs sanitized and validated
- **Error Handling**: Graceful degradation and recovery

### 3. Network Security
- **API Authentication**: Token-based access control
- **Data Encryption**: TLS for network communication
- **Rate Limiting**: Protection against abuse
- **Access Logging**: Comprehensive audit trails

## Performance Characteristics

### 1. Timing Requirements
- **Main Loop**: 60-second cycles (±1 second)
- **Sensor Reading**: 1-60 second intervals (configurable)
- **Response Time**: <100ms for critical operations
- **Deployment Time**: 5-30 seconds per operation

### 2. Resource Requirements
- **CPU Usage**: <30% average, <70% peak
- **Memory Usage**: <200MB baseline, <300MB peak
- **Storage**: 1GB for logs and data, 100MB for system
- **Network**: <1Mbps average, <10Mbps peak

### 3. Reliability Targets
- **Uptime**: 99.9% (8.76 hours downtime/year)
- **Mean Time Between Failures**: >1000 hours
- **Recovery Time**: <60 seconds for automatic recovery
- **Data Integrity**: 100% cryptographic verification

## Deployment Architecture

### 1. Hardware Requirements
- **Processor**: Raspberry Pi 4 (4GB RAM minimum)
- **Storage**: 32GB microSD card (Class 10)
- **Power**: 12V DC, 5A power supply
- **Enclosure**: IP54 rated, temperature controlled

### 2. Software Requirements
- **Operating System**: Raspberry Pi OS (64-bit)
- **Python**: 3.9+ with asyncio support
- **Dependencies**: See `requirements.txt`
- **Services**: systemd for process management

### 3. Network Requirements
- **Local Network**: Ethernet or WiFi connectivity
- **Internet**: Optional for updates and notifications
- **Firewall**: Port 8080 for web interface
- **DNS**: Local hostname resolution

## Monitoring and Maintenance

### 1. System Monitoring
- **Health Checks**: Automated every 5 minutes
- **Performance Metrics**: Real-time collection and display
- **Alerting**: Configurable thresholds and notifications
- **Logging**: Structured logs with rotation

### 2. Maintenance Procedures
- **Daily**: Sensor calibration verification
- **Weekly**: System integrity checks
- **Monthly**: Hardware inspection and cleaning
- **Quarterly**: Full system validation

### 3. Backup and Recovery
- **Configuration**: Automated daily backups
- **Data**: Incremental backups with retention
- **System**: Full image backups monthly
- **Recovery**: Automated restore procedures

## Compliance and Standards

### 1. Yeshua Compliance
- **Transparency**: All operations logged and verifiable
- **Verifiability**: Cryptographic proof of all actions
- **Falsifiability**: Clear failure modes and detection
- **Orthogonal Separation**: Modular, independent components

### 2. Safety Standards
- **Electrical Safety**: CE/FCC compliance for hardware
- **Biological Safety**: Proper handling of Beauveria bassiana
- **UV Safety**: IEC 62471 photobiological safety
- **Environmental**: RoHS compliance

### 3. Software Standards
- **Code Quality**: PEP 8 compliance, type hints
- **Testing**: >80% test coverage
- **Documentation**: Comprehensive and up-to-date
- **Security**: Regular vulnerability scanning

## Future Extensions

### 1. Planned Features
- **Machine Learning**: Adaptive pattern optimization
- **Multi-zone Support**: Multiple refrigerator compartments
- **Cloud Integration**: Centralized monitoring and control
- **Mobile App**: iOS/Android companion application

### 2. Hardware Expansions
- **Additional Sensors**: CO2, VOC, particulate matter
- **Advanced Actuators**: Servo-controlled spray nozzles
- **Energy Harvesting**: Solar/battery backup
- **Modular Design**: Plug-and-play component expansion

### 3. Software Improvements
- **Performance Optimization**: Reduced resource usage
- **Enhanced UI**: Improved user experience
- **API Expansion**: Additional endpoints and features
- **Plugin System**: Third-party extension support

## Conclusion

The Crusader Combat Refrigerator represents a complete, transparent, and verifiable system for autonomous pest control. Through its modular architecture, comprehensive monitoring, and cryptographic verification, it provides a robust solution that adheres to the highest standards of engineering excellence and Yeshua compliance.

All components are designed for reliability, maintainability, and extensibility, ensuring the system can evolve to meet future requirements while maintaining its core principles of transparency and verifiability.