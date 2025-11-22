# Python Version Compatibility

## Issue

Some packages (`tiktoken`, `pydantic-core`) may have issues with Python 3.13 due to Rust bindings compatibility.

## Solutions

### Option 1: Use Python 3.12 (Recommended)

Create a new virtual environment with Python 3.12:

```bash
# Check if you have Python 3.12
python3.12 --version

# If not installed, install via pyenv or homebrew
# Using pyenv:
pyenv install 3.12.7
pyenv local 3.12.7

# Create new venv with Python 3.12
cd backend
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Option 2: Use Latest Package Versions

The requirements.txt has been updated to use newer versions that may have better Python 3.13 support. Try installing:

```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

### Option 3: Set Compatibility Flag (Workaround)

If you must use Python 3.13, you can try setting the compatibility flag:

```bash
export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
pip install -r requirements.txt
```

However, this may cause runtime issues. **Option 1 (Python 3.12) is strongly recommended.**

