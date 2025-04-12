import logging
import logging.config
from pathlib import Path
import coloredlogs

LOG_FILE = Path("logs/scheduler.log")

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'detailed': {
            'format': '[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        },
    },

    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_FILE,
            'maxBytes': 5_000_000,
            'backupCount': 3,
            'formatter': 'detailed',
        },
    },

    'root': {
        'level': 'INFO',
        'handlers': ['file']
    },
}

def setup_logging():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Configure file handler from dict
    logging.config.dictConfig(LOGGING_CONFIG)

    # Attach coloredlogs to the root logger for console output
    coloredlogs.install(
        level='INFO',
        fmt='[%(asctime)s] %(levelname)s in %(name)s: %(message)s',
        level_styles={
            'debug':    {'color': 'white'},
            'info':     {'color': 'green'},
            'warning':  {'color': 'yellow'},
            'error':    {'color': 'red'},
            'critical': {'color': 'magenta', 'bold': True},
        },
        field_styles={
            'asctime': {'color': 'cyan'},
            'levelname': {'bold': True},
            'name': {'color': 'blue'}
        }
    )
