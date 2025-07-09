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

# Custom rate limiter logger

rate_logger = logging.getLogger('rate_limit')
rate_file_handler = logging.FileHandler('./logs/rate_limit.log', mode='a')
rate_formatter = logging.Formatter(
    fmt='Time created : {asctime}\n\n {message}',
    style='{'
)
rate_logger.addHandler(rate_file_handler)
file_handler.setFormatter(rate_formatter)
rate_logger.setLevel(logging.INFO)

# Custom load balancer log

load_logger = logging.Logger('load_balance')
load_file_hander = logging.FileHandler('./logs/load_balance.log', mode='a')
load_formatter = logging.Formatter(
    '{asctime} : {levelname} : {message}',
    style='{'
)
load_logger.addHandler(load_file_hander)
load_file_hander.formatter(load_formatter)
load_logger.setLevel(logging.INFO)