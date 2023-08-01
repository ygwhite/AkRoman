from loguru import logger


def add_named_logger(name: str):
    from settings import (
        LOGGER_PATH,
        LOGGER_LEVELS,
        LOGGER_ROTATION,
        LOGGER_COMPRESSION
    )

    filter_by_name = lambda record: record["extra"].get("name") == name

    for level in LOGGER_LEVELS:
        logger.add(
            LOGGER_PATH / name / f"{level.lower()}.log",
            level=level,
            rotation=LOGGER_ROTATION,
            compression=LOGGER_COMPRESSION,
            enqueue=True,
            filter=filter_by_name
        )

    return logger.bind(name=name)