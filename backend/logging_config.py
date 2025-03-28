import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(app):
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        os.path.join(log_dir, 'flask.log'),
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3
    )
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] %(name)s: %(message)s"
    )
    file_handler.setFormatter(formatter)

    # Clear default handlers and set up file + console
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)

    app.logger.info("Logging is set up.")
    return app.logger