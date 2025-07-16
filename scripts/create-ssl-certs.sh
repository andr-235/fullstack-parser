#!/bin/bash

# =============================================================================
# SSL CERTIFICATE GENERATOR FOR IP ADDRESS
# =============================================================================
# Создание self-signed SSL сертификатов для IP адреса 192.168.88.12
# Использование: ./create-ssl-certs.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Variables
SERVER_IP="192.168.88.12"
SSL_DIR="./nginx/ssl"
CERT_FILE="$SSL_DIR/cert.pem"
KEY_FILE="$SSL_DIR/key.pem"
CERT_VALID_DAYS=365

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

# =============================================================================
# MAIN FUNCTIONS
# =============================================================================
create_ssl_directory() {
    log_info "Creating SSL directory..."
    mkdir -p "$SSL_DIR"
    log_success "SSL directory created: $SSL_DIR"
}

generate_ssl_config() {
    log_info "Generating SSL configuration..."

    cat > "$SSL_DIR/openssl.conf" << EOF
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C=RU
ST=Moscow
L=Moscow
O=VK Parser Production
OU=IT Department
CN=$SERVER_IP

[v3_req]
keyUsage = keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
IP.1 = $SERVER_IP
DNS.1 = localhost
EOF

    log_success "SSL configuration created"
}

generate_ssl_certificate() {
    log_info "Generating SSL certificate for $SERVER_IP..."

    # Generate private key
    openssl genrsa -out "$KEY_FILE" 2048

    # Generate certificate signing request and certificate
    openssl req -new -x509 -key "$KEY_FILE" -out "$CERT_FILE" \
        -days $CERT_VALID_DAYS -config "$SSL_DIR/openssl.conf" \
        -extensions v3_req

    log_success "SSL certificate generated successfully"
}

set_permissions() {
    log_info "Setting proper permissions..."

    # Set proper permissions for SSL files
    chmod 600 "$KEY_FILE"
    chmod 644 "$CERT_FILE"

    log_success "Permissions set correctly"
}

verify_certificate() {
    log_info "Verifying certificate..."

    # Verify certificate
    openssl x509 -in "$CERT_FILE" -text -noout | grep -A1 "Subject:"
    openssl x509 -in "$CERT_FILE" -text -noout | grep -A5 "Subject Alternative Name"

    log_success "Certificate verification completed"
}

cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f "$SSL_DIR/openssl.conf"
    log_success "Cleanup completed"
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================
main() {
    log_info "Starting SSL certificate generation for $SERVER_IP"

    # Check if openssl is installed
    if ! command -v openssl &> /dev/null; then
        log_error "OpenSSL is not installed. Please install it first."
        exit 1
    fi

    # Check if certificates already exist
    if [[ -f "$CERT_FILE" ]] && [[ -f "$KEY_FILE" ]]; then
        log_warning "SSL certificates already exist!"
        read -p "Do you want to overwrite them? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Certificate generation cancelled"
            exit 0
        fi
    fi

    # Execute steps
    create_ssl_directory
    generate_ssl_config
    generate_ssl_certificate
    set_permissions
    verify_certificate
    cleanup

    log_success "SSL certificates created successfully!"
    log_info "Certificate: $CERT_FILE"
    log_info "Private Key: $KEY_FILE"
    log_warning "Note: These are self-signed certificates. Browsers will show security warnings."
    log_info "You can add the certificate to your browser's trusted certificates to avoid warnings."
}

# Run main function
main "$@"
