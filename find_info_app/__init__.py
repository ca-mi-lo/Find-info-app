import logging


__version__ = "0.1.2"
__app_name__ = "Find Info App"


def create_logger(mod_name: str = "root", levelname: str = "INFO"):
    """
    Creates a logger for the Streamlit app.

    Args:
        mod_name (str, optional): The name of the module. Defaults to "root".
        levelname (str, optional): Log level name. Defaults to "INFO".

    Returns:
        logging.Logger: The created logger object.
    """
    logger = logging.getLogger(f"{__app_name__}:{mod_name}")
    logger.setLevel(levelname)

    # Fix to not attach new handlers on rerun
    if (
        sum([isinstance(handler, logging.StreamHandler) for handler in logger.handlers])
        == 0
    ):
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger
