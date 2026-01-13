#!/bin/bash

# Airtime API Deployment Script
# Usage: ./deploy.sh [dev|prod|stop|logs|backup]

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_env_file() {
    if [ ! -f .env ]; then
        print_error ".env file not found!"
        print_info "Creating .env from .env.example..."
        cp .env.example .env
        print_warning "Please update .env file with your configuration before deploying!"
        exit 1
    fi
}

deploy_dev() {
    print_info "Starting development deployment..."
    check_env_file
    docker-compose down
    docker-compose up -d --build
    print_info "Development environment started!"
    print_info "API available at: http://localhost:8000"
    docker-compose logs -f
}

deploy_prod() {
    print_info "Starting production deployment..."
    check_env_file

    # Check for required production settings
    if grep -q "django-insecure" .env; then
        print_error "Please update SECRET_KEY in .env file for production!"
        exit 1
    fi

    if grep -q "DEBUG=True" .env; then
        print_warning "DEBUG=True detected. Setting to False for production..."
        sed -i 's/DEBUG=True/DEBUG=False/' .env
    fi

    docker-compose -f docker-compose.prod.yml down
    docker-compose -f docker-compose.prod.yml up -d --build
    print_info "Production environment started!"
    print_info "Checking container health..."
    sleep 5
    docker-compose -f docker-compose.prod.yml ps
}

stop_services() {
    print_info "Stopping services..."
    docker-compose down
    docker-compose -f docker-compose.prod.yml down
    print_info "Services stopped!"
}

show_logs() {
    print_info "Showing logs (Ctrl+C to exit)..."
    if docker ps | grep -q "airtime_api_prod"; then
        docker-compose -f docker-compose.prod.yml logs -f
    else
        docker-compose logs -f
    fi
}

backup_database() {
    print_info "Creating database backup..."
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="backup_${TIMESTAMP}.sql"

    if docker ps | grep -q "airtime_postgres_prod"; then
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U airtime_user airtime_db > "$BACKUP_FILE"
    else
        docker-compose exec -T db pg_dump -U airtime_user airtime_db > "$BACKUP_FILE"
    fi

    print_info "Database backup created: $BACKUP_FILE"
}

run_migrations() {
    print_info "Running database migrations..."
    if docker ps | grep -q "airtime_api_prod"; then
        docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
    else
        docker-compose exec web python manage.py migrate
    fi
    print_info "Migrations completed!"
}

show_status() {
    print_info "Service status:"
    echo ""
    docker-compose ps
    echo ""
    docker-compose -f docker-compose.prod.yml ps 2>/dev/null || true
}

# Main script
case "$1" in
    dev)
        deploy_dev
        ;;
    prod)
        deploy_prod
        ;;
    stop)
        stop_services
        ;;
    logs)
        show_logs
        ;;
    backup)
        backup_database
        ;;
    migrate)
        run_migrations
        ;;
    status)
        show_status
        ;;
    *)
        echo "Airtime API Deployment Script"
        echo ""
        echo "Usage: $0 {dev|prod|stop|logs|backup|migrate|status}"
        echo ""
        echo "Commands:"
        echo "  dev      - Deploy development environment"
        echo "  prod     - Deploy production environment"
        echo "  stop     - Stop all services"
        echo "  logs     - Show container logs"
        echo "  backup   - Backup database"
        echo "  migrate  - Run database migrations"
        echo "  status   - Show service status"
        echo ""
        exit 1
        ;;
esac
