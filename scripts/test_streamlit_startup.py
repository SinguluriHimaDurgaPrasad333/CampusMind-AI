import subprocess
import time
import requests
import sys

def run_test():
    import subprocess
    import time
    import requests
    import sys

    print("Starting Streamlit on port 8504...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8504", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    connected = False
    for i in range(20):
        time.sleep(1)
        try:
            res = requests.get("http://localhost:8504", timeout=2)
            if res.status_code == 200:
                print(f"SUCCESS: Streamlit responded with HTTP {res.status_code} in {i+1} seconds!")
                connected = True
                break
        except Exception:
            pass

    proc.terminate()
    try:
        proc.wait(timeout=5)
    except Exception:
        proc.kill()

    return connected

if __name__ == "__main__":
    import sys
    success = run_test()
    if not success:
        sys.exit(1)

