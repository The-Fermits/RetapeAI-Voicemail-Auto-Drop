from datetime import datetime

def ts_log(msg):
    """Timestamped logging for terminal output"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")