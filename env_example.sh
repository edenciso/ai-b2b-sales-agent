# ==============================================================================
# AI B2B Sales Agent - Environment Configuration
# ==============================================================================
# Copy this file to .env and fill in your actual values
# NEVER commit .env to version control!

# ------------------------------------------------------------------------------
# REQUIRED: Anthropic API Configuration
# ------------------------------------------------------------------------------
# Get your API key from: https://console.anthropic.com/
ANTHROPIC_API_KEY=your_api_key_here

# ------------------------------------------------------------------------------
# OPTIONAL: CRM Integration (Salesforce, HubSpot, etc.)
# ------------------------------------------------------------------------------
# Salesforce Example
CRM_TYPE=salesforce
CRM_API_KEY=your_salesforce_api_key
CRM_INSTANCE_URL=https://your-instance.salesforce.com
CRM_USERNAME=your_salesforce_username
CRM_PASSWORD=your_salesforce_password

# HubSpot Example (alternative)
# CRM_TYPE=hubspot
# HUBSPOT_API_KEY=your_hubspot_api_key
# HUBSPOT_PORTAL_ID=your_portal_id

# ------------------------------------------------------------------------------
# OPTIONAL: Email Configuration
# ------------------------------------------------------------------------------
# SMTP Settings (Gmail example)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Use app-specific password for Gmail
SMTP_USE_TLS=true

# SendGrid (alternative)
# SENDGRID_API_KEY=your_sendgrid_api_key
# SENDGRID_FROM_EMAIL=sales@yourcompany.com

# ------------------------------------------------------------------------------
# OPTIONAL: Data Enrichment Services
# ------------------------------------------------------------------------------
# Clearbit (company data)
CLEARBIT_API_KEY=your_clearbit_api_key

# ZoomInfo (contact discovery)
ZOOMINFO_API_KEY=your_zoominfo_api_key
ZOOMINFO_USERNAME=your_zoominfo_username
ZOOMINFO_PASSWORD=your_zoominfo_password

# LinkedIn Sales Navigator (optional)
LINKEDIN_ACCESS_TOKEN=your_linkedin_token

# ------------------------------------------------------------------------------
# OPTIONAL: Database Configuration (for production)
# ------------------------------------------------------------------------------
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/sales_agent
DATABASE_POOL_SIZE=10

# Redis (for caching and queues)
REDIS_URL=redis://localhost:6379/0

# ------------------------------------------------------------------------------
# Application Configuration
# ------------------------------------------------------------------------------
# Logging
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=logs/sales_agent.log

# Rate Limiting
MAX_CONCURRENT_LEADS=5
API_RATE_LIMIT_PER_MINUTE=50

# Qualification Thresholds
QUALIFICATION_SCORE_THRESHOLD=60
NURTURE_SCORE_THRESHOLD=40

# Email Configuration
EMAIL_SEND_DELAY_SECONDS=2
FOLLOW_UP_DELAY_DAYS=3
MAX_FOLLOW_UPS=3

# Feature Flags
ENABLE_WEB_SEARCH=true
ENABLE_CRM_INTEGRATION=false
ENABLE_EMAIL_SENDING=false
ENABLE_DATA_ENRICHMENT=false

# ------------------------------------------------------------------------------
# Security
# ------------------------------------------------------------------------------
# API Security
API_SECRET_KEY=your_secret_key_here  # Generate with: openssl rand -hex 32
API_ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Encryption (for sensitive data storage)
ENCRYPTION_KEY=your_encryption_key  # Generate with: openssl rand -base64 32

# ------------------------------------------------------------------------------
# Monitoring & Analytics (Optional)
# ------------------------------------------------------------------------------
# Sentry (error tracking)
SENTRY_DSN=your_sentry_dsn

# Datadog (metrics and logging)
DATADOG_API_KEY=your_datadog_api_key

# Segment (product analytics)
SEGMENT_WRITE_KEY=your_segment_key

# ------------------------------------------------------------------------------
# Development vs Production
# ------------------------------------------------------------------------------
ENVIRONMENT=development  # development, staging, production
DEBUG=true
