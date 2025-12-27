# ARCON Production Build Guide

## Building for Production

### Prerequisites
- Python 3.8+
- pip package manager

### Installation & Build

#### Option 1: Build on Your Target Platform (Recommended)

**On Windows (for .exe):**
```bash
# Clone/download the project
cd arcon

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install PyInstaller

# Run build script
.\build.bat
```

**On Linux/macOS (for binary):**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install PyInstaller

# Run build script
chmod +x build.sh
./build.sh
```

#### Option 2: Manual Build

```bash
# With virtual environment activated
pyinstaller arcon.spec
```

The executable will be in the `dist/` directory.

## Running the Executable

### CLI Mode
```bash
# Windows
arcon.exe --archive C:\path\to\input --output C:\path\to\output

# Linux/macOS
./arcon --archive /path/to/input --output /path/to/output
```

**Full CLI options:**
```bash
arcon --archive <path> --output <path> [--logs <path>] [--quality 1-100] [--rotate <degrees>] [--license-only] [--creator <name>] [--credit <line>] [--copyright <holder>] [--usage-terms <terms>] [--license-url <url>]
```

### UI Mode
```bash
# Windows
arcon.exe --ui

# Linux/macOS
./arcon --ui
```

Then open your browser to: **http://localhost:3932**

## Building for Different Platforms

The spec file (`arcon.spec`) creates platform-specific executables:
- Build on **Windows** → Windows .exe
- Build on **Linux** → Linux binary  
- Build on **macOS** → macOS binary

For cross-platform building, tools like `PyInstaller` require the target OS.

## Requirements File

Create `requirements.txt` if not present:
```
Flask==3.0.0
Werkzeug==3.0.1
```

These will be bundled into the executable automatically.

## Distribution

The executable in `dist/` is fully standalone and includes:
- Python runtime
- Flask web framework
- All dependencies
- HTML templates
- CSS stylesheets

Simply distribute the single executable file.

## Troubleshooting

**"Missing dependencies" error:**
- Ensure `dcraw`, `convert`, `exiftool` are installed on the target system
- These are system-level tools, not Python packages

**Port 3932 already in use:**
- Edit `src/app.py` line `app.run(..., port=3932)` to use a different port

**Templates/CSS not loading:**
- Ensure the spec file correctly includes the datas paths
- Check that `src/templates/` and `src/static/` directories exist
