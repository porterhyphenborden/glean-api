import logging


logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler()
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)
