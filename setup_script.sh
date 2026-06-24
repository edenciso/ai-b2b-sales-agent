#!/bin/bash

# AI B2B Sales Agent - Automated Setup Script
# This script sets up your development environment

set -e  # Exit on error

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     AI B2B Sales Agent - Automated Setup                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Python version
echo "🐍 Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11 or higher.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo -e "${RED}❌ Python $REQUIRED_VERSION or higher is required. You have $PYTHON_VERSION${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment already exists. Skipping...${NC}"
else
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo -e "${GREEN}✅ pip upgraded${NC}"
echo ""

# Install dependencies
echo "📚 Installing dependencies..."
echo "   Choose installation type:"
echo "   1) Minimal (Quick Start only)"
echo "   2) Full (All features + MCP servers)"
read -p "   Enter choice [1-2]: " choice

case $choice in
    1)
        if [ -f "requirements-minimal.txt" ]; then
            pip install -r requirements-minimal.txt
            echo -e "${GREEN}✅ Minimal dependencies installed${NC}"
        else
            echo -e "${YELLOW}⚠️  requirements-minimal.txt not found. Installing core packages...${NC}"
            pip install anthropic python-dotenv aiohttp rich
        fi
        ;;
    2)
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
            echo -e "${GREEN}✅ Full dependencies installed${NC}"
        else
            echo -e "${RED}❌ requirements.txt not found${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac
echo ""

# Create .env file
echo "🔐 Setting up environment variables..."
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists. Skipping...${NC}"
else
    cat > .env << 'EOF'
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_api_key_here

# CRM Integration (Optional - for production)
CRM_API_KEY=
CRM_INSTANCE_URL=https://your-instance.salesforce.com

# Email Configuration (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=your_app_password

# Data Enrichment (Optional)
CLEARBIT_API_KEY=
ZOOMINFO_API_KEY=

# Logging Level
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env and add your ANTHROPIC_API_KEY${NC}"
fi
echo ""

# Create directory structure
echo "📁 Creating directory structure..."
mkdir -p logs
mkdir -p data
mkdir -p results
echo -e "${GREEN}✅ Directories created${NC}"
echo ""

# Verify installation
echo "🧪 Verifying installation..."
python3 -c "import anthropic; print('✅ Anthropic SDK OK')" 2>/dev/null || echo "❌ Anthropic SDK failed"
python3 -c "import dotenv; print('✅ python-dotenv OK')" 2>/dev/null || echo "❌ python-dotenv failed"
echo ""

# Print next steps
echo "╔══════════════════════════════════════════════════════════╗"
echo "║                 Setup Complete! 🎉                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Next Steps:"
echo ""
echo "   1. Add your Anthropic API key to .env:"
echo "      ${YELLOW}nano .env${NC}"
echo ""
echo "   2. Activate the virtual environment:"
echo "      ${YELLOW}source venv/bin/activate${NC}"
echo ""
echo "   3. Run the quick start demo:"
echo "      ${YELLOW}python quickstart_example.py${NC}"
echo ""
echo "   4. Or run the full agentic workflow:"
echo "      ${YELLOW}python integrated_agent.py${NC}"
echo ""
echo "📖 Documentation: See deployment_guide.md for detailed instructions"
echo ""
echo "🆘 Need help? Check the troubleshooting section in the guide"
echo ""
