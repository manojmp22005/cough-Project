"""
Single command to run the entire Cough Monitor system.
Usage: python run.py
"""
import subprocess
import sys
import os
import time
import signal

def main():
    print("=" * 50)
    print("  Starting Smart AI Cough Monitor")
    print("=" * 50)
    print()

    project_dir = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.join(project_dir, "web_app")

    # Start Python Gateway (audio recorder)
    print("[1/2] Starting Audio Recorder...")
    gateway = subprocess.Popen(
        [sys.executable, "-u", "python_gateway/pc_audio_analysis.py"],
        cwd=project_dir,
        env=env
    )
    time.sleep(2)

    # Start Streamlit Web App
    print("[2/2] Starting Web App...")
    webapp = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "web_app/app.py"],
        cwd=project_dir,
        env=env
    )

    print()
    print("=" * 50)
    print("  System is RUNNING!")
    print("  Web App: http://localhost:8501")
    print("  Press Ctrl+C to stop everything")
    print("=" * 50)

    try:
        gateway.wait()
        webapp.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        gateway.terminate()
        webapp.terminate()
        gateway.wait()
        webapp.wait()
        print("All services stopped.")

if __name__ == "__main__":
    main()
