#!/bin/bash
# ARCON Build Script for Production .exe

echo "=== ARCON Production Build ==="
echo ""

# Check if PyInstaller is installed
if ! python -m pip list | grep -q PyInstaller; then
    echo "📦 Installing PyInstaller..."
    pip install PyInstaller
fi

echo "🔨 Building ARCON.exe..."
echo ""

# Build using the spec file
pyinstaller arcon.spec --onefile --distpath ./dist --buildpath ./build

echo ""
echo "✅ Build complete!"
echo ""
echo "📁 Executable location: ./dist/arcon.exe"
echo ""
echo "Usage:"
echo "  - CLI mode:  arcon.exe --archive /path/in --output /path/out [options]"
echo "  - UI mode:   arcon.exe --ui"
echo ""
