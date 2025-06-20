import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

file_handler = logging.FileHandler('logging.log')
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s'))

console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

logger.addHandler(file_handler)
logger.addHandler(console_handler)


def log(text: str) -> None:
    logger.info('\t\t' + text.replace('\n', ''))
    while '\n' in text:
        logger.info('')
        text = text.replace('\n', '')
