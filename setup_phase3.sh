#!/bin/bash

# Phase 3 Setup Script
# Run this after completing the database migration

echo "=========================================="
echo "Phase 3: Setup for New Field Types"
echo "=========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend root directory"
    exit 1
fi

# Step 1: Install Pillow
echo "Step 1: Installing Pillow..."
pip install Pillow==10.2.0
if [ $? -eq 0 ]; then
    echo "✅ Pillow installed successfully"
else
    echo "❌ Failed to install Pillow"
    exit 1
fi
echo ""

# Step 2: Create upload directories
echo "Step 2: Creating upload directories..."
mkdir -p ./uploads/signatures
if [ $? -eq 0 ]; then
    echo "✅ Upload directory created: ./uploads/signatures"
else
    echo "❌ Failed to create upload directory"
    exit 1
fi
echo ""

# Step 3: Set permissions
echo "Step 3: Setting permissions..."
chmod 755 ./uploads/signatures
if [ $? -eq 0 ]; then
    echo "✅ Permissions set: 755"
else
    echo "⚠️  Warning: Failed to set permissions"
fi
echo ""

# Step 4: Verify Pillow installation
echo "Step 4: Verifying Pillow installation..."
python -c "from PIL import Image; print('✅ Pillow import successful')" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Warning: Pillow import test failed"
else
    echo "✅ Pillow is working correctly"
fi
echo ""

# Summary
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. ✅ Install dependencies - DONE"
echo "2. ✅ Create upload directories - DONE"
echo "3. ⏳ Run database migration manually (see PHASE3_INTEGRATION_COMPLETE.md)"
echo "4. ⏳ Restart your backend server"
echo "5. ⏳ Test with the provided curl commands"
echo ""
echo "Upload directory: $(pwd)/uploads/signatures"
echo "Pillow version: $(pip show Pillow 2>/dev/null | grep Version | cut -d' ' -f2)"
echo ""
echo "For database migration SQL, see PHASE3_INTEGRATION_COMPLETE.md"
echo ""
