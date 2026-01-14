import ssl
import sys
import os

# Bypass SSL verification
ssl._create_default_https_context = ssl._create_unverified_context

# Add current directory to path just in case
sys.path.append(os.getcwd())

# Import pygbag (it must be installed)
try:
    import pygbag.app
except ImportError:
    print("pygbag not installed")
    sys.exit(1)

# Mock command line arguments
# we want: pygbag --build static/games/stywar_wars/main.py
sys.argv = ["pygbag", "--build", "static/games/stywar_wars/main.py"]

print("Starting pygbag build/download with SSL bypass...")
try:
    pygbag.app.main()
except SystemExit as e:
    print(f"pygbag finished with code {e}")
except Exception as e:
    print(f"pygbag failed with {e}")
