import logging
import os

def setup_logging():
    log_file_path = os.path.join(os.path.dirname(__file__), 'logs/app.log')
    if os.path.exists(log_file_path):
        logging.basicConfig(
            filename=log_file_path, 
            level=logging.INFO, 
            filemode='a', 
            format='%(asctime)s [%(process)d %(name)s] %(levelname)s: %(message)s'
        )