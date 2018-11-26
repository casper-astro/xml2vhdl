import colorlog
import logging
import logging.config


def config_logger(name=__name__):
    """

    Use this logging configurator at the top of each file which uses logging

    :param name: name: __name__
    :return: logger
    """
    logger = logging.getLogger('helper_logging.{}'
                               .format(name))
    logging.config.fileConfig('./logging.conf', disable_existing_loggers=False)
    return logger


def config_class_logger(class_name, name=__name__):
    """

    Use this logging configurator at the top of the def __init__(self):
    \NOTE A call to config_logger must have already been made before the class.
    :param class_name: self.__class__.__name__
    :param name: __name__
    :return: logger
    """
    logger = logging.getLogger('helper_logging.{}.{}'
                               .format(name, class_name))
    return logger

