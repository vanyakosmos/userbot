import logging.config

from config.settings import LOGS_FILE_PATH, LOGGING_LEVEL, LOGGING_LEVEL_ROOT


def add_color(string: str, color, just=0):
    string = string.rjust(just)
    return f'\033[{color}m{string}\033[0m'


def configure_logging(level=None, root_level=None):
    level = level or LOGGING_LEVEL
    root_level = root_level or LOGGING_LEVEL_ROOT

    # setup logging level display
    levels = [
        (logging.DEBUG, add_color('DEBUG', '36', 5)),
        (logging.INFO, add_color('INFO', '32', 5)),
        (logging.WARNING, add_color('WARN', '33', 5)),
        (logging.ERROR, add_color('ERROR', '31', 5)),
        (logging.CRITICAL, add_color('CRIT', '7;31;31', 5)),
    ]
    for lvl, name in levels:
        logging.addLevelName(lvl, name)

    m = add_color(">", '36')

    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': f'[%(asctime)s] %(levelname)s %(name)20s:%(lineno)-3d {m} %(message)s',
                'datefmt': "%Y/%m/%d %H:%M:%S"
            },
            'simple': {
                'format': f'[%(asctime)s] %(name)s:%(lineno)d > %(message)s',
                'datefmt': "%Y/%m/%d %H:%M:%S"
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose'
            },
            'file': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': LOGS_FILE_PATH,
                'formatter': 'simple',
                'maxBytes': 1024 * 1024,
                'backupCount': 1,
            },
        },
        'loggers': {
            'handlers': {
                'handlers': ['console', 'file'],
                'level': level,
                'propagate': False,
            },
            'manager': {
                'handlers': ['console', 'file'],
                'level': level,
                'propagate': False,
            },
            'persistence': {
                'handlers': ['console', 'file'],
                'level': level,
                'propagate': False,
            },
            '__main__': {
                'handlers': ['console', 'file'],
                'level': level,
                'propagate': False,
            },
            '': {
                'handlers': ['console', 'file'],
                'level': root_level,
                'propagate': False,
            },
        }
    })
