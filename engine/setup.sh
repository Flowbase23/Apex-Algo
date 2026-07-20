#!/usr/bin/env bash
# ==========================================================================
# Apex Algo Trading Engine — One-Command Setup
# ==========================================================================
# Usage:
#   chmod +x setup.sh && ./setup.sh
#
# What this does:
#   1. Checks Python 3.10+ is installed
#   2. Creates a Python virtual environment (venv/)
#   3. Installs all dependencies from requirements.txt
#   4. Copies .env.example → .env (if no .env exists)
#   5. Runs the import verification tests to confirm everything works
# ==========================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

ENGINE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ENGINE_DIR/venv"

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║        Apex Algo Trading Engine — Setup                     ║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# ────────────────────────────────────────────────────────────────
# Step 1: Check Python version
# ────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[1/5]${NC} Checking Python installation ..."

PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" &>/dev/null; then
        version=$("$candidate" --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    echo -e "${RED}✗ Python 3.10+ is required but was not found.${NC}"
    echo "  Install it from https://www.python.org/downloads/"
    echo "  Or via your package manager (apt, brew, etc.)"
    exit 1
fi

echo -e "  ${GREEN}✓${NC} Found $($PYTHON --version)"

# ────────────────────────────────────────────────────────────────
# Step 2: Create virtual environment
# ────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[2/5]${NC} Creating virtual environment ..."

if [ -d "$VENV_DIR" ]; then
    echo -e "  ${YELLOW}⚠${NC}  venv/ already exists — removing and recreating"
    rm -rf "$VENV_DIR"
fi

$PYTHON -m venv "$VENV_DIR"
echo -e "  ${GREEN}✓${NC} Virtual environment created at venv/"

# ────────────────────────────────────────────────────────────────
# Step 3: Install dependencies
# ────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[3/5]${NC} Installing Python dependencies ..."

PIP="$VENV_DIR/bin/pip"
$PIP install --upgrade pip -q
$PIP install -r "$ENGINE_DIR/requirements.txt"

echo -e "  ${GREEN}✓${NC} Dependencies installed"

# ────────────────────────────────────────────────────────────────
# Step 4: Set up environment file
# ────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[4/5]${NC} Setting up environment ..."

if [ ! -f "$ENGINE_DIR/.env" ]; then
    cp "$ENGINE_DIR/.env.example" "$ENGINE_DIR/.env"
    echo -e "  ${GREEN}✓${NC} Created .env from .env.example"
    echo -e "  ${YELLOW}  → Edit .env to add your Alpha Vantage / Polygon.io API keys${NC}"
else
    echo -e "  ${GREEN}✓${NC} .env already exists — skipping"
fi

# Create runtime directories
mkdir -p "$ENGINE_DIR/data_cache" "$ENGINE_DIR/logs"
echo -e "  ${GREEN}✓${NC} Runtime directories created (data_cache/, logs/)"

# ────────────────────────────────────────────────────────────────
# Step 5: Verify installation
# ────────────────────────────────────────────────────────────────
echo -e "${YELLOW}[5/5]${NC} Verifying installation (import tests) ..."

cd "$ENGINE_DIR"
if $VENV_DIR/bin/python -m pytest tests/test_imports.py -v --tb=short 2>&1; then
    echo ""
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  ✓  Setup complete! The engine is ready.                    ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
else
    echo ""
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║  ✗  Some tests failed. Check the output above.              ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi

echo ""
echo -e "  Quick start:"
echo -e "    ${CYAN}source venv/bin/activate${NC}"
echo -e "    ${CYAN}python demo.py${NC}                 # Full pipeline demo"
echo -e ""
echo -e "  Run tests:"
echo -e "    ${CYAN}python -m pytest tests/ -v${NC}"
echo -e ""
echo -e "  Configure:"
echo -e "    ${CYAN}Edit config/settings.py${NC} to customize symbols, risk limits, etc."
echo -e "    ${CYAN}Edit .env${NC} to add premium data API keys"
echo ""
