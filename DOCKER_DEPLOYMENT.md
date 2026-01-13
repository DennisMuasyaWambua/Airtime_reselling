# Docker Deployment Guide

This guide explains how to deploy the Airtime API using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- `.env` file with required environment variables

## Quick Start

### 1. Configure Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database (automatically set by docker-compose)
ENVIRONMENT=production
DATABASE_PROD_URL=postgresql://airtime_user:airtime_password@db:5432/airtime_db

# M-Pesa API Credentials
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
DEALERNUMBER=your-dealer-number
DEALERPIN=your-dealer-pin
```

### 2. Build and Run with Docker Compose

```bash
# Build and start all services (database + API)
docker-compose up -d --build

# View logs
docker-compose logs -f web

# Check service status
docker-compose ps
```

The API will be available at `http://localhost:8000`

### 3. Run Database Migrations (if needed)

Migrations run automatically on startup, but you can run them manually:

```bash
docker-compose exec web python manage.py migrate
```

### 4. Create a Superuser (optional)

```bash
docker-compose exec web python manage.py createsuperuser
```

## Docker Commands

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes (Database Data)
```bash
docker-compose down -v
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f db
```

### Restart Services
```bash
docker-compose restart web
```

### Access Django Shell
```bash
docker-compose exec web python manage.py shell
```

### Run Management Commands
```bash
docker-compose exec web python manage.py <command>
```

## Building Single Docker Image

If you want to build just the Django application without docker-compose:

```bash
# Build image
docker build -t airtime-api:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  --name airtime-api \
  airtime-api:latest
```

## Production Deployment

### Security Considerations

1. **Update SECRET_KEY**: Generate a new secret key for production
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Set DEBUG=False**: Never run with DEBUG=True in production

3. **Update ALLOWED_HOSTS**: Add your domain names

4. **Use Strong Database Passwords**: Update postgres credentials in docker-compose.yml

5. **SSL/TLS**: Use a reverse proxy (nginx, traefik) with SSL certificates

### Recommended Production Setup

```yaml
# docker-compose.prod.yml example with nginx
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./staticfiles:/app/staticfiles
      - ./certbot/conf:/etc/letsencrypt
    depends_on:
      - web

  db:
    # ... (same as docker-compose.yml)

  web:
    # ... (same as docker-compose.yml)
```

## Monitoring and Maintenance

### View Resource Usage
```bash
docker stats
```

### Backup Database
```bash
docker-compose exec db pg_dump -U airtime_user airtime_db > backup.sql
```

### Restore Database
```bash
docker-compose exec -T db psql -U airtime_user airtime_db < backup.sql
```

## Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
sudo lsof -i :8000
# Or change port in docker-compose.yml
```

### Database Connection Issues
```bash
# Check if database is healthy
docker-compose ps db

# View database logs
docker-compose logs db

# Restart database
docker-compose restart db
```

### Application Errors
```bash
# View application logs
docker-compose logs -f web

# Access container shell
docker-compose exec web /bin/bash

# Check Django configuration
docker-compose exec web python manage.py check
```

### Permission Issues
```bash
# Fix staticfiles permissions
sudo chown -R 1000:1000 staticfiles media
```

## Scaling

To run multiple application instances:

```bash
docker-compose up -d --scale web=3
```

Note: You'll need a load balancer (nginx) to distribute traffic.

## Health Checks

The Dockerfile includes a health check. Monitor container health:

```bash
docker inspect --format='{{.State.Health.Status}}' airtime_api
```

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| SECRET_KEY | Django secret key | Yes |
| DEBUG | Debug mode (True/False) | Yes |
| ALLOWED_HOSTS | Comma-separated hostnames | Yes |
| ENVIRONMENT | production/development | Yes |
| DATABASE_PROD_URL | PostgreSQL connection string | Yes |
| MPESA_CONSUMER_KEY | M-Pesa API consumer key | Yes |
| MPESA_CONSUMER_SECRET | M-Pesa API consumer secret | Yes |
| DEALERNUMBER | M-Pesa dealer number | Yes |
| DEALERPIN | M-Pesa dealer PIN | Yes |
