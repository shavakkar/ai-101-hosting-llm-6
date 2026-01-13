import os
from datetime import datetime

LOG_DIR = "logs"

def get_log_file():
    """Return the path to today's log file, rotated daily."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    date_str = datetime.now().strftime("%Y-%m-%d")
    return os.path.join(LOG_DIR, f"mcp_logs_{date_str}.txt")

def log_output(user_input, decoded, tool_call=None):
    """Append a log entry with user input, raw model output, and parsed JSON."""
    log_file = get_log_file()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write("\n" + "="*80 + "\n")
        f.write(f"Timestamp: {datetime.now().isoformat()}\n")
        f.write(f"User Input: {user_input}\n\n")
        f.write("Raw Model Output:\n")
        f.write(decoded + "\n\n")
        if tool_call:
            f.write("Extracted JSON:\n")
            f.write(str(tool_call) + "\n")
        f.write("="*80 + "\n")
