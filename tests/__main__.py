import subprocess
import sys

if __name__ == "__main__":
    if "c4dpy" in sys.executable:
        exe = sys.executable
    else:
        exe = "c4dpy"

    subprocess.run(
        [
            exe,
            "-m",
            "unittest",
            "discover",
            "-v",
            "-s",
            "tests",
        ]
    )
