#!/bin/bash
# Simple script to run tests with virtual environment activated

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Activating virtual environment...${NC}"

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo -e "${RED}Error: .venv directory not found!${NC}"
    echo "Please create a virtual environment first:"
    echo "  python3 -m venv .venv"
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}pytest not found. Installing...${NC}"
    pip install pytest pytest-cov
fi

echo -e "${GREEN}Running tests...${NC}"
echo ""

# Run tests (unit tests only by default)
pytest src/support_agent/tests/ -m "not integration" -v

# Capture exit code
EXIT_CODE=$?

echo ""
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
else
    echo -e "${RED}✗ Some tests failed${NC}"
fi

exit $EXIT_CODE
