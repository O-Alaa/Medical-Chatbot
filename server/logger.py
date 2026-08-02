import logging


def setup_logger(
    name: str = "MedicalAssistant",
) -> logging.Logger:
    """
    Create and configure the application's console logger.
    """

    application_logger = logging.getLogger(name)
    application_logger.setLevel(logging.DEBUG)

    # Avoid adding duplicate handlers when modules reload.
    if not application_logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            "[%(asctime)s] "
            "[%(levelname)s] --- "
            "[%(message)s]"
        )

        console_handler.setFormatter(formatter)
        application_logger.addHandler(console_handler)

    # Prevent duplicate output from the root logger.
    application_logger.propagate = False

    return application_logger


logger = setup_logger()
logger.info("Medical Assistant logger initialized")