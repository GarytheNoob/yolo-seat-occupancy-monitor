#!/bin/bash
# Raspberry Pi Installation Script for YOLO Seat Occupancy Monitor
# This script automates the installation of dependencies on Raspberry Pi 5
#
# Usage: bash rpi_install.sh

set -e  # Exit on any error

echo "=========================================="
echo "YOLO Seat Occupancy Monitor"
echo "Raspberry Pi Installation Script"
echo "=========================================="
echo ""

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if running on ARM architecture
ARCH=$(uname -m)
if [[ "$ARCH" != "aarch64" && "$ARCH" != "armv7l" ]]; then
    print_info "Warning: This script is designed for Raspberry Pi (ARM architecture)"
    print_info "Detected architecture: $ARCH"
    echo ""
fi

# Check Python version
print_info "Checking Python version..."
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
print_success "Python $PYTHON_VERSION detected"
echo ""

# Step 1: Upgrade pip, setuptools, and wheel
print_info "Step 1/3: Upgrading pip, setuptools, and wheel..."
python3 -m pip install --upgrade pip setuptools wheel
if [ $? -eq 0 ]; then
    print_success "pip, setuptools, and wheel upgraded successfully"
else
    print_error "Failed to upgrade pip"
    exit 1
fi
echo ""

# Step 2: Install CPU-only PyTorch
print_info "Step 2/3: Installing PyTorch (CPU-only, ~200MB)..."
print_info "Note: This may take a few minutes on Raspberry Pi"
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
if [ $? -eq 0 ]; then
    print_success "PyTorch installed successfully (CPU-only, NO CUDA)"
else
    print_error "Failed to install PyTorch"
    exit 1
fi
echo ""

# Step 3: Install remaining dependencies
print_info "Step 3/3: Installing remaining dependencies from requirements.txt..."
print_info "Using piwheels for pre-built ARM wheels..."
pip install -r requirements.txt --extra-index-url https://www.piwheels.org/simple
if [ $? -eq 0 ]; then
    print_success "All dependencies installed successfully"
else
    print_error "Failed to install dependencies"
    exit 1
fi
echo ""

# Verify installation
print_info "Verifying installation..."
python3 -c "import torch; import cv2; import ultralytics; import numpy" 2>/dev/null
if [ $? -eq 0 ]; then
    print_success "All packages verified successfully!"
else
    print_error "Verification failed - some packages may not have installed correctly"
    exit 1
fi
echo ""

# Print summary
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
print_success "PyTorch (CPU-only) - Installed"
print_success "OpenCV (headless) - Installed"
print_success "Ultralytics YOLO - Installed"
print_success "NumPy - Installed"
echo ""
echo "Next steps:"
echo "1. Configure seats: python3 setup_helper.py"
echo "   (requires a display - see README for headless setup)"
echo ""
echo "2. Run the application:"
echo "   - With display: python3 main.py"
echo "   - Headless mode: python3 main.py --headless"
echo ""
echo "For more information, see README.md"
echo ""
