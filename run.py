import subprocess
import sys
import os

if __name__ == "__main__":
    main_path = os.path.join(os.path.dirname(__file__), "ai_companion_system", "main.py")
    subprocess.run([sys.executable, main_path])
