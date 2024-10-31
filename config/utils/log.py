import logging
import logging.handlers
import os
from config.utils.decorators import singleton


@singleton
class SingletonLogging:
    """
    Singleton Logging Class
    """
    
    def __init__(self, logger_name, logfile_dir):
        """
        initial parameter for logging
        :param looger_name: 
        :param logfile_dir: logfile directory name
        """
        self.logger_name = logger_name
        
        # BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        BASE_DIR = BASE_DIR.replace("\\", "/")
        self.logfile_path = BASE_DIR + logfile_dir
        
        os.makedirs(self.logfile_path, exist_ok=True)
        
    def get_logger(self):
        """
        Config Logger
        :return:
        """
        logger = logging.getLogger(self.logger_name)
        logger.setLevel(logging.DEBUG)
        
        all_handler = logging.handlers.TimedRotatingFileHandler(filename=self.logfile_path + "/all.log",
                                                                encoding="utf-8", when="midnight")
        all_formatter = logging.Formatter('%(asctime)s [%(filename)s:%(lineno)d] %(levelname)s - %(message)s')
        
        all_handler.setFormatter(all_formatter)
        
        logger.addHandler(all_handler)
        
        # Commenting out the stdout streaming for profuction server.
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(fmt=all_formatter)
        logger.addHandler(stream_handler)
        
        
        # Handle logger error
        
        # error_handler = logging.handlers.TimedRotatingFileHandler(filename=self.logfile_path + "/all.log",
        #                                                         encoding="utf-8", when="midnight")
        
        # error_formatter = logging.Formatter("%(levelname)s - %(asctime)s - %(filename)s[:%(lineno)d] -%(message)s")
        
        # error_handler.setFormatter(error_formatter)
        
        # error_handler.setLevel(logging.ERROR)
        
        # logger.addHandler(error_handler)
        
        return logger
    
logger = SingletonLogging(logger_name="monitor", logfile_dir="/logs").get_logger()

if __name__ == '__main__':
    logger.error('Test error log')
    