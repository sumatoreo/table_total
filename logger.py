from pathlib import Path
import logging
import colorlog


def init_logger(dunder_name, testing_mode) -> logging.Logger:
    Path('logs').mkdir(parents=True, exist_ok=True)

    colorlog_format = (
        '\033[1m '
        '%(log_color)s '
        '%(asctime)s - %(threadName)s - %(funcName)s - %(levelname)s - %(message)s'
    )
    colorlog.basicConfig(format=colorlog_format)
    logger = logging.getLogger(dunder_name)

    if testing_mode:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Output full log
    fh = logging.FileHandler('logs/app.log')
    fh.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(funcName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Output warning log
    fh = logging.FileHandler('logs/app.warning.log')
    fh.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(funcName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Output error log
    fh = logging.FileHandler('logs/app.error.log')
    fh.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(asctime)s - %(threadName)s - %(funcName)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    return logger
