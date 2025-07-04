import logging
import os

os.makedirs('./logs', exist_ok=True) # Make the directory

# Custom logger logging to 'app.log'
logger = logging.getLogger(__name__)
file_handler = logging.FileHandler(filename='./logs/app.log', mode='a')
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    fmt='{asctime} - {levelname} - {message}',
    style='{'
)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
logger.setLevel(logging.INFO)