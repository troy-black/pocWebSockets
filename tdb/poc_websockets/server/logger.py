import logging.handlers
import sys
from logging import LogRecord
from queue import Queue

FORMAT = '%(asctime)s | %(levelname)8s | %(name)20s | %(message)s | %(filename)s:%(lineno)d (%(funcName)s)'

LOG_LEVELS = {
    'python_multipart.multipart': logging.WARNING,
    'uvicorn.error': logging.INFO,
}


def setup_logging(level: str, file_name: str) -> None:
    basic_formatter = logging.Formatter(FORMAT)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Create a queue
    queue: Queue[LogRecord] = Queue(-1)

    # Create a QueueHandler and attach it to the logger
    queue_handler = logging.handlers.QueueHandler(queue)
    queue_handler.setLevel(level)

    root_logger.addHandler(queue_handler)

    # Create a QueueListener with RotatingFileHandler and StreamHandler
    file_handler = logging.handlers.RotatingFileHandler(file_name, maxBytes=1024 * 1024, backupCount=5)
    file_handler.setFormatter(basic_formatter)
    file_handler.setLevel(level)

    stream_handler = logging.StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(basic_formatter)
    stream_handler.setLevel(level)

    queue_listener = logging.handlers.QueueListener(queue, file_handler, stream_handler)
    queue_listener.start()


def force_logging() -> None:
    root_logger = logging.getLogger()

    # remove every other logger's handlers
    # and propagate to root logger
    for name in logging.root.manager.loggerDict:
        logger = logging.getLogger(name)
        logger.handlers = root_logger.handlers
        logger.propagate = False

    # set specific log levels for modules
    for name, level in LOG_LEVELS.items():
        logger = logging.getLogger(name)
        logger.setLevel(level)
