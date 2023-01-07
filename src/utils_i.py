import logging
import logging.config
from functools import wraps


def wrap_into_list(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        return list(func(*args, **kwargs))

    return wrapped


def merge_recursively(default, override):
    both_dicts = isinstance(default, dict) and isinstance(override, dict)
    if not both_dicts:
        return override
    result = dict(override)
    for key, default_value in default.items():
        if key in override:
            value_override = override[key]
            value = merge_recursively(default_value, value_override)
        else:
            value = default_value
        result[key] = value
    return result


def setup_logger():
    _logger_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': '%(asctime)s %(levelname)-7s %(processName)-20s   %(filename)s:%(lineno)s.%(funcName)-20s  %(message)s',
            },
            'short': {
                'format': '%(asctime)s %(levelname)-7s %(message)s',
                'datefmt': '%d %b %H:%M:%S'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'DEBUG',
                'formatter': 'short',
                'stream': 'ext://sys.stdout'
            },
            'console_error': {
                'class': 'logging.StreamHandler',
                'level': 'ERROR',
                'formatter': 'short',
                'stream': 'ext://sys.stderr'
            },
            # 'info_file_handler': {
            #     'level': 'INFO',
            #     'class': 'logging.handlers.RotatingFileHandler',
            #     'formatter': 'detailed',
            #     'encoding': 'utf8',
            #     'backupCount': 20,
            #     'maxBytes': 10485760,
            #     'filename': os.path.join(
            #         LOGS_DIR, FILENAME_TEMPLATES['info'] % (service_name, log_name_postfix)
            #     ),
            # },
            # 'short_file_handler': {
            #     'level': 'INFO',
            #     'class': 'logging.handlers.RotatingFileHandler',
            #     'formatter': 'short',
            #     'encoding': 'utf8',
            #     'backupCount': 20,
            #     'maxBytes': 10485760,
            #     'filename': os.path.join(
            #         LOGS_DIR, FILENAME_TEMPLATES['short'] % (service_name, log_name_postfix)
            #     ),
            # },
        },
        'loggers': {
            'root': {
                'handlers': [
                    'console',
                    # 'console_error',
                    # 'debug_file_handler',
                    # 'info_file_handler',
                    # 'errors_file_handler',
                    # 'short_file_handler'
                ],
                'level': 'INFO',
                'propagate': True
            },
            'console_only': {
                'handlers': ['console'],
                'level': 'INFO',
                'propagate': True
            },
        },
    }
    logging.config.dictConfig(_logger_config)