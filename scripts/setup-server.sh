#!/bin/bash

# =============================================================================
# DEBIAN 12 SERVER SETUP SCRIPT
# =============================================================================
# Автоматическая настройка сервера для fullstack приложения
# Использование: ./setup-server.sh yourdomain.com your-email@domain.com

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
DOMAIN=${1:-""}
EMAIL=${2:-""}
APP_DIR="/opt/app"
APP_USER="appuser"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

validate_inputs() {
    if [[ -z "$DOMAIN" ]]; then
        log_error "Domain is required. Usage: ./setup-server.sh yourdomain.com your-email@domain.com"
        exit 1
    fi

    if [[ -z "$EMAIL" ]]; then
        log_error "Email is required. Usage: ./setup-server.sh yourdomain.com your-email@domain.com"
        exit 1
    fi
}

# =============================================================================
# SYSTEM UPDATE & BASIC SETUP
# =============================================================================
update_system() {
    log_info "Updating system packages..."
    apt update && apt upgrade -y
    apt install -y curl wget git unzip htop nano vim ufw fail2ban
    log_success "System updated successfully"
}

# =============================================================================
# USER MANAGEMENT
# =============================================================================
create_app_user() {
    log_info "Creating application user..."
    if ! id "$APP_USER" &>/dev/null; then
        useradd -m -s /bin/bash "$APP_USER"
        usermod -aG sudo "$APP_USER"
        log_success "User $APP_USER created"
    else
        log_warning "User $APP_USER already exists"
    fi
}

# =============================================================================
# FIREWALL CONFIGURATION
# =============================================================================
configure_firewall() {
    log_info "Configuring UFW firewall..."

    # Reset UFW to defaults
    ufw --force reset

    # Default policies
    ufw default deny incoming
    ufw default allow outgoing

    # Allow SSH
    ufw allow ssh

    # Allow HTTP and HTTPS
    ufw allow 80/tcp
    ufw allow 443/tcp

    # Enable firewall
    ufw --force enable

    log_success "Firewall configured successfully"
}

# =============================================================================
# FAIL2BAN CONFIGURATION
# =============================================================================
configure_fail2ban() {
    log_info "Configuring Fail2Ban..."

    cat > /etc/fail2ban/jail.local << EOF
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 3

[sshd]
enabled = true
port = ssh
logpath = %(sshd_log)s
backend = %(sshd_backend)s

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 3

[nginx-limit-req]
enabled = true
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
EOF

    systemctl enable fail2ban
    systemctl restart fail2ban

    log_success "Fail2Ban configured successfully"
}

# =============================================================================
# DOCKER INSTALLATION
# =============================================================================
install_docker() {
    log_info "Installing Docker..."

    # Remove old Docker versions
    apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # Install prerequisites
    apt install -y ca-certificates curl gnupg lsb-release

    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Add Docker repository
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Install Docker
    apt update
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Add app user to docker group
    usermod -aG docker "$APP_USER"

    # Enable Docker service
    systemctl enable docker
    systemctl start docker

    log_success "Docker installed successfully"
}

# =============================================================================
# DOCKER COMPOSE INSTALLATION
# =============================================================================
install_docker_compose() {
    log_info "Installing Docker Compose..."

    # Download latest version
    COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d '"' -f 4)
    curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

    # Make executable
    chmod +x /usr/local/bin/docker-compose

    # Create symlink
    ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose

    log_success "Docker Compose installed successfully"
}

# =============================================================================
# SSL CERTIFICATE SETUP
# =============================================================================
install_certbot() {
    log_info "Installing Certbot for SSL certificates..."

    apt install -y snapd
    snap install core; snap refresh core
    snap install --classic certbot
    ln -sf /snap/bin/certbot /usr/bin/certbot

    log_success "Certbot installed successfully"
}

# =============================================================================
# APPLICATION DIRECTORY SETUP
# =============================================================================
setup_app_directory() {
    log_info "Setting up application directory..."

    # Create app directory
    mkdir -p "$APP_DIR"
    chown "$APP_USER:$APP_USER" "$APP_DIR"

    # Create necessary subdirectories
    mkdir -p "$APP_DIR"/{backup,logs,ssl}
    mkdir -p /var/www/{static,media,error}

    # Set permissions
    chown -R "$APP_USER:$APP_USER" "$APP_DIR"
    chown -R www-data:www-data /var/www

    log_success "Application directory setup completed"
}

# =============================================================================
# NGINX CONFIGURATION
# =============================================================================
configure_nginx() {
    log_info "Installing and configuring Nginx..."

    apt install -y nginx

    # Remove default site
    rm -f /etc/nginx/sites-enabled/default

    # Create basic configuration for SSL setup
    cat > /etc/nginx/sites-available/app << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    location /.well-known/acme-challenge/ {
        root /var/www/certbot;
    }

    location / {
        return 301 https://\$host\$request_uri;
    }
}
EOF

    ln -sf /etc/nginx/sites-available/app /etc/nginx/sites-enabled/app

    # Test configuration
    nginx -t

    # Start and enable Nginx
    systemctl enable nginx
    systemctl start nginx

    log_success "Nginx configured successfully"
}

# =============================================================================
# SSL CERTIFICATE GENERATION
# =============================================================================
setup_ssl() {
    log_info "Setting up SSL certificate for $DOMAIN..."

    # Create webroot directory for certbot
    mkdir -p /var/www/certbot

    # Get SSL certificate
    certbot certonly --webroot -w /var/www/certbot -d "$DOMAIN" -d "www.$DOMAIN" --email "$EMAIL" --agree-tos --non-interactive

    # Setup automatic renewal
    echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -

    log_success "SSL certificate setup completed"
}

# =============================================================================
# SYSTEM OPTIMIZATION
# =============================================================================
optimize_system() {
    log_info "Optimizing system settings..."

    # Increase file limits
    cat >> /etc/security/limits.conf << EOF
* soft nofile 65535
* hard nofile 65535
EOF

    # Optimize kernel parameters
    cat >> /etc/sysctl.conf << EOF
# Network optimization
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216
net.ipv4.tcp_rmem = 4096 87380 16777216
net.ipv4.tcp_wmem = 4096 65536 16777216
net.core.netdev_max_backlog = 5000
net.ipv4.tcp_congestion_control = bbr

# File system optimization
fs.file-max = 2097152
vm.swappiness = 10
EOF

    sysctl -p

    log_success "System optimization completed"
}

# =============================================================================
# MONITORING SETUP
# =============================================================================
setup_monitoring() {
    log_info "Setting up basic monitoring..."

    # Create log rotation for application logs
    cat > /etc/logrotate.d/app << EOF
$APP_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $APP_USER $APP_USER
}
EOF

    # Create simple monitoring script
    cat > "$APP_DIR/scripts/monitor.sh" << 'EOF'
#!/bin/bash
# Simple monitoring script

check_service() {
    if systemctl is-active --quiet $1; then
        echo "✓ $1 is running"
    else
        echo "✗ $1 is not running"
        systemctl restart $1
    fi
}

echo "=== System Monitoring $(date) ==="
echo "Disk usage:"
df -h /

echo -e "\nMemory usage:"
free -h

echo -e "\nDocker containers:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo -e "\nService status:"
check_service nginx
check_service docker
check_service fail2ban
EOF

    chmod +x "$APP_DIR/scripts/monitor.sh"
    chown "$APP_USER:$APP_USER" "$APP_DIR/scripts/monitor.sh"

    # Setup monitoring cron job
    echo "*/5 * * * * $APP_DIR/scripts/monitor.sh >> $APP_DIR/logs/monitor.log 2>&1" | crontab -u "$APP_USER" -

    log_success "Basic monitoring setup completed"
}

# =============================================================================
# CLEANUP & FINAL STEPS
# =============================================================================
cleanup() {
    log_info "Performing cleanup..."

    apt autoremove -y
    apt autoclean

    log_success "Cleanup completed"
}

print_summary() {
    log_success "Server setup completed successfully!"
    echo
    echo "=== SETUP SUMMARY ==="
    echo "Domain: $DOMAIN"
    echo "Email: $EMAIL"
    echo "App Directory: $APP_DIR"
    echo "App User: $APP_USER"
    echo
    echo "=== NEXT STEPS ==="
    echo "1. Clone your application to $APP_DIR"
    echo "2. Configure environment variables"
    echo "3. Replace nginx configuration with production config"
    echo "4. Deploy your application with docker-compose"
    echo
    echo "=== IMPORTANT ==="
    echo "- SSH key authentication is recommended"
    echo "- Change default passwords"
    echo "- Review firewall rules"
    echo "- Test SSL certificate"
    echo
    echo "=== USEFUL COMMANDS ==="
    echo "- Check Docker status: systemctl status docker"
    echo "- View logs: journalctl -fu docker"
    echo "- SSL certificate info: certbot certificates"
    echo "- Firewall status: ufw status"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================
main() {
    log_info "Starting Debian 12 server setup..."

    check_root
    validate_inputs

    update_system
    create_app_user
    configure_firewall
    configure_fail2ban
    install_docker
    install_docker_compose
    install_certbot
    setup_app_directory
    configure_nginx
    setup_ssl
    optimize_system
    setup_monitoring
    cleanup

    print_summary
}

# Run main function
main "$@"
