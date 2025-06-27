import logging
import sys

def setup_logger():
    """
    Configures and returns a logger.
    """
    logger = logging.getLogger("JSRepoAnalysis")
    logger.setLevel(logging.INFO)

    # Create a handler to write to stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)

    # Create a formatter and add it to the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(handler)

    return logger

logger = setup_logger()
