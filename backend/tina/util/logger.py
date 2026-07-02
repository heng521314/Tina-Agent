import logging


class Logger:
    def __init__(self, name):
        self._name = name

    def info(self, detail: str):
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        logger = logging.getLogger(self._name)
        logger.info(msg=detail)
