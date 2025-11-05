import logging

class Server_logger:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.file_handler = logging.FileHandler('server.log', mode='a', encoding='utf-8')
        self.formatter = logging.Formatter(
            '%(asctime)s (%(levelname)s) - %(message)s'
        )
        self.file_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.file_handler)
