#!/bin/bash

# Crusader Combat Refrigerator - Deployment Script
# Version: 1.0.0
# Schema ID: CRUSADER-1.0
# Author: Orthogonal Engineering Framework
# License: AGAPE (Free Forever)

set -e  # Exit on error
set -u  # Exit on undefined variable

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJECT_ROOT/venv"
REQUIREMENTS_FILE="$PROJECT_ROOT/requirements.txt"
SYSTEMD_SERVICE="crusader.service"
SERVICE_FILE="/etc/systemd/system/$SYSTEMD_SERVICE"
USER="crusader"
GROUP="crusader"
LOG_DIR="/var/log/crusader"
DATA_DIR="/var/lib/crusader"
CONFIG_DIR="/etc/crusader"

# Print colored message
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_error "This script must be run as root"
        exit 1
    fi
}

# Check system requirements
check_system() {
    print_info "Checking system requirements..."

    # Check Python version
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_info "Python version: $PYTHON_VERSION"

        # Check Python 3.9+
        if [[ $(echo "$PYTHON_VERSION 3.9" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
            print_error "Python 3.9 or higher is required"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi

    # Check disk space
    DISK_SPACE=$(df -h / | awk 'NR==2 {print $4}')
    print_info "Available disk space: $DISK_SPACE"

    # Check memory
    MEMORY=$(free -h | awk 'NR==2 {print $2}')
    print_info "Total memory: $MEMORY"

    print_success "System requirements check passed"
}

# Create system user and group
create_user() {
    print_info "Creating system user and group..."

    if ! id -u $USER >/dev/null 2>&1; then
        useradd --system --shell /bin/false --create-home $USER
        print_success "Created user: $USER"
    else
        print_info "User $USER already exists"
    fi

    if ! getent group $GROUP >/dev/null 2>&1; then
        groupadd --system $GROUP
        print_success "Created group: $GROUP"
    else
        print_info "Group $GROUP already exists"
    fi

    # Add user to group
    usermod -a -G $GROUP $USER
    print_success "Added $USER to $GROUP group"
}

# Create directories
create_directories() {
    print_info "Creating directories..."

    # Log directory
    mkdir -p $LOG_DIR
    chown $USER:$GROUP $LOG_DIR
    chmod 755 $LOG_DIR
    print_success "Created log directory: $LOG_DIR"

    # Data directory
    mkdir -p $DATA_DIR
    chown $USER:$GROUP $DATA_DIR
    chmod 755 $DATA_DIR
    print_success "Created data directory: $DATA_DIR"

    # Config directory
    mkdir -p $CONFIG_DIR
    chown $USER:$GROUP $CONFIG_DIR
    chmod 755 $CONFIG_DIR
    print_success "Created config directory: $CONFIG_DIR"

    # Project directories
    mkdir -p $PROJECT_ROOT/logs
    mkdir -p $PROJECT_ROOT/backups
    mkdir -p $PROJECT_ROOT/manifests
    chown -R $USER:$GROUP $PROJECT_ROOT
    chmod -R 755 $PROJECT_ROOT
    print_success "Created project directories"
}

# Setup Python virtual environment
setup_venv() {
    print_info "Setting up Python virtual environment..."

    # Check if venv already exists
    if [[ -d "$VENV_DIR" ]]; then
        print_warning "Virtual environment already exists at $VENV_DIR"
        read -p "Do you want to recreate it? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$VENV_DIR"
            print_info "Removed existing virtual environment"
        else
            print_info "Using existing virtual environment"
            return
        fi
    fi

    # Create virtual environment
    python3 -m venv "$VENV_DIR"
    print_success "Created virtual environment at $VENV_DIR"

    # Activate virtual environment
    source "$VENV_DIR/bin/activate"

    # Upgrade pip
    pip install --upgrade pip
    print_success "Upgraded pip"

    # Install requirements
    if [[ -f "$REQUIREMENTS_FILE" ]]; then
        pip install -r "$REQUIREMENTS_FILE"
        print_success "Installed Python dependencies"
    else
        print_warning "Requirements file not found: $REQUIREMENTS_FILE"
    fi

    # Deactivate virtual environment
    deactivate
}

# Copy configuration files
copy_configs() {
    print_info "Copying configuration files..."

    # Copy main config
    if [[ -f "$PROJECT_ROOT/core/config.yaml" ]]; then
        cp "$PROJECT_ROOT/core/config.yaml" "$CONFIG_DIR/config.yaml"
        chown $USER:$GROUP "$CONFIG_DIR/config.yaml"
        chmod 644 "$CONFIG_DIR/config.yaml"
        print_success "Copied main configuration"
    fi

    # Copy hardware config
    if [[ -f "$PROJECT_ROOT/hardware/pins.yaml" ]]; then
        cp "$PROJECT_ROOT/hardware/pins.yaml" "$CONFIG_DIR/pins.yaml"
        chown $USER:$GROUP "$CONFIG_DIR/pins.yaml"
        chmod 644 "$CONFIG_DIR/pins.yaml"
        print_success "Copied hardware configuration"
    fi

    # Create default config if not exists
    if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
        cat > "$CONFIG_DIR/config.yaml" << EOF
# Crusader Combat Refrigerator - Default Configuration
# Generated on $(date)

system:
  name: "Crusader Combat Refrigerator"
  version: "1.0.0"
  mode: "active"
  debug: false
  log_level: "INFO"

warfare:
  spore_deployment:
    enabled: true
    deployment_interval: 3600
    deployment_duration: 5
    spore_concentration: 0.1

  uv_sterilization:
    enabled: true
    sterilization_interval: 7200
    sterilization_duration: 30

monitoring:
  sensors:
    poll_interval: 60
    health_check_interval: 300

  witness:
    enabled: true
    update_interval: 3600
EOF
        chown $USER:$GROUP "$CONFIG_DIR/config.yaml"
        chmod 644 "$CONFIG_DIR/config.yaml"
        print_success "Created default configuration"
    fi
}

# Create systemd service
create_service() {
    print_info "Creating systemd service..."

    cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Crusader Combat Refrigerator
After=network.target
Wants=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$USER
Group=$GROUP
WorkingDirectory=$PROJECT_ROOT
Environment="PYTHONPATH=$PROJECT_ROOT"
Environment="PATH=$VENV_DIR/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
ExecStart=$VENV_DIR/bin/python $PROJECT_ROOT/core/main.py --config $CONFIG_DIR/config.yaml
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=crusader

# Security hardening
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$LOG_DIR $DATA_DIR $CONFIG_DIR
ProtectHome=true
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true

[Install]
WantedBy=multi-user.target
EOF

    # Set permissions
    chmod 644 "$SERVICE_FILE"
    print_success "Created systemd service: $SERVICE_FILE"

    # Reload systemd
    systemctl daemon-reload
    print_success "Reloaded systemd daemon"
}

# Setup logging
setup_logging() {
    print_info "Setting up logging..."

    # Create rsyslog config
    RSYSLOG_CONFIG="/etc/rsyslog.d/99-crusader.conf"
    cat > "$RSYSLOG_CONFIG" << EOF
# Crusader Combat Refrigerator logging
if \$programname == 'crusader' then {
    action(type="omfile" file="$LOG_DIR/crusader.log")
    stop
}
EOF

    # Restart rsyslog
    systemctl restart rsyslog
    print_success "Configured rsyslog for Crusader"

    # Create logrotate config
    LOGROTATE_CONFIG="/etc/logrotate.d/crusader"
    cat > "$LOGROTATE_CONFIG" << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 640 $USER $GROUP
    sharedscripts
    postrotate
        systemctl kill -s HUP rsyslog.service >/dev/null 2>&1 || true
    endscript
}
EOF

    print_success "Configured log rotation"
}

# Generate initial manifests
generate_manifests() {
    print_info "Generating initial manifests..."

    # Generate SHA256 manifest
    cd "$PROJECT_ROOT"
    find . -type f -name "*.py" -o -name "*.yaml" -o -name "*.md" -o -name "*.sh" | \
        sort | \
        xargs sha256sum > "$PROJECT_ROOT/manifests/sha256_manifest.txt"

    chown $USER:$GROUP "$PROJECT_ROOT/manifests/sha256_manifest.txt"
    chmod 644 "$PROJECT_ROOT/manifests/sha256_manifest.txt"
    print_success "Generated SHA256 manifest"

    # Generate file index
    find . -type f | sort > "$PROJECT_ROOT/manifests/file_index.txt"
    chown $USER:$GROUP "$PROJECT_ROOT/manifests/file_index.txt"
    chmod 644 "$PROJECT_ROOT/manifests/file_index.txt"
    print_success "Generated file index"
}

# Enable and start service
enable_service() {
    print_info "Enabling and starting service..."

    # Enable service
    systemctl enable "$SYSTEMD_SERVICE"
    print_success "Enabled $SYSTEMD_SERVICE"

    # Start service
    systemctl start "$SYSTEMD_SERVICE"
    print_success "Started $SYSTEMD_SERVICE"

    # Check service status
    sleep 2
    systemctl status "$SYSTEMD_SERVICE" --no-pager
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."

    # Check if service is running
    if systemctl is-active --quiet "$SYSTEMD_SERVICE"; then
        print_success "Service is running"
    else
        print_error "Service is not running"
        journalctl -u "$SYSTEMD_SERVICE" --no-pager -n 20
        exit 1
    fi

    # Check logs
    if [[ -f "$LOG_DIR/crusader.log" ]]; then
        print_success "Log file created: $LOG_DIR/crusader.log"
        # Show last few lines of log
        tail -n 5 "$LOG_DIR/crusader.log"
    else
        print_warning "Log file not found yet"
    fi

    # Check directories
    for dir in "$LOG_DIR" "$DATA_DIR" "$CONFIG_DIR"; do
        if [[ -d "$dir" ]]; then
            print_success "Directory exists: $dir"
        else
            print_error "Directory missing: $dir"
        fi
    done

    print_success "Installation verification complete"
}

# Display completion message
display_completion() {
    echo ""
    echo "================================================"
    echo "   CRUSADER COMBAT REFRIGERATOR INSTALLED"
    echo "================================================"
    echo ""
    echo "Service: $SYSTEMD_SERVICE"
    echo "User: $USER"
    echo "Group: $GROUP"
    echo "Logs: $LOG_DIR/crusader.log"
    echo "Data: $DATA_DIR"
    echo "Config: $CONFIG_DIR"
    echo ""
    echo "Commands:"
    echo "  systemctl status $SYSTEMD_SERVICE"
    echo "  journalctl -u $SYSTEMD_SERVICE -f"
    echo "  systemctl restart $SYSTEMD_SERVICE"
    echo "  systemctl stop $SYSTEMD_SERVICE"
    echo ""
    echo "Next steps:"
    echo "  1. Review configuration at $CONFIG_DIR/config.yaml"
    echo "  2. Check logs: tail -f $LOG_DIR/crusader.log"
    echo "  3. Test the system with: systemctl restart $SYSTEMD_SERVICE"
    echo ""
    echo "Documentation: $PROJECT_ROOT/docs/"
    echo "================================================"
}

# Main deployment function
deploy() {
    print_info "Starting Crusader Combat Refrigerator deployment..."
    echo ""

    # Run deployment steps
    check_root
    check_system
    create_user
    create_directories
    setup_venv
    copy_configs
    create_service
    setup_logging
    generate_manifests
    enable_service
    verify_installation

    print_success "Deployment completed successfully!"
    display_completion
}

# Uninstall function
uninstall() {
    print_warning "Starting uninstallation..."
    echo ""

    read -p "Are you sure you want to uninstall Crusader? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "Uninstallation cancelled"
        exit 0
    fi

    # Stop and disable service
    if systemctl is-active --quiet "$SYSTEMD_SERVICE"; then
        systemctl stop "$SYSTEMD_SERVICE"
        print_success "Stopped $SYSTEMD_SERVICE"
    fi

    if systemctl is-enabled --quiet "$SYSTEMD_SERVICE"; then
        systemctl disable "$SYSTEMD_SERVICE"
        print_success "Disabled $SYSTEMD_SERVICE"
    fi

    # Remove service file
    if [[ -f "$SERVICE_FILE" ]]; then
        rm -f "$SERVICE_FILE"
        print_success "Removed service file: $SERVICE_FILE"
    fi

    # Remove rsyslog config
    RSYSLOG_CONFIG="/etc/rsyslog.d/99-crusader.conf"
    if [[ -f "$RSYSLOG_CONFIG" ]]; then
        rm -f "$RSYSLOG_CONFIG"
        print_success "Removed rsyslog config"
    fi

    # Remove logrotate config
    LOGROTATE_CONFIG="/etc/logrotate.d/crusader"
    if [[ -f "$LOGROTATE_CONFIG" ]]; then
        rm -f "$LOGROTATE_CONFIG"
        print_success "Removed logrotate config"
    fi

    # Remove directories (optional)
    read -p "Remove log and data directories? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$LOG_DIR" "$DATA_DIR" "$CONFIG_DIR"
        print_success "Removed log, data, and config directories"
    fi

    # Remove user and group (optional)
    read -p "Remove system user and group? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if id -u $USER >/dev/null 2>&1; then
            userdel "$USER"
            print_success "Removed user: $USER"
        fi

        if getent group $GROUP >/dev/null 2>&1; then
            groupdel "$GROUP"
            print_success "Removed group: $GROUP"
        fi
    fi

    # Reload systemd
    systemctl daemon-reload
    systemctl restart rsyslog

    print_success "Uninstallation completed"
    echo ""
    echo "Note: Project files at $PROJECT_ROOT were not removed."
    echo "      Remove manually if desired."
}

# Show usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  deploy     Install and configure Crusader (default)"
    echo "  uninstall  Remove Crusader from system"
    echo "  help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy      # Install Crusader"
    echo "  $0 uninstall   # Remove Crusader"
    echo ""
}

# Main script logic
main() {
    COMMAND=${1:-deploy}

    case "$COMMAND" in
        deploy)
            deploy
            ;;
        uninstall
