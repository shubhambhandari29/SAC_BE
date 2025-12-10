import logging
import logging.handlers
import os
import sys

def configure_logging():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s - %(message)s')

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Log directory: use Azure LogFiles path if available, otherwise "logs" locally
    # log_dir = "/home/LogFiles" if os.getenv("WEBSITE_INSTANCE_ID") else "logs"
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    # File handler (rotates daily, keeps 7 backups)
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when="midnight", interval=1, backupCount=7, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Avoid adding duplicate handlers
    if not root.handlers:
        root.addHandler(console_handler)
        root.addHandler(file_handler)

