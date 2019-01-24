# -*- coding: utf8 -*-
"""

***************************
``helper/customlogging.py``
***************************

`LICENSE`_ © 2018-2019 Science and Technology Facilities Council & contributors

.. _LICENSE: _static/LICENSE_STFC

``customlogging.py`` is a helper module provided to define and configure consistent logging. The logging
configuration is handled via ``../logging.yml`` YAML file and uses ``colorlog`` for console output.
A rolling system is used for outputting to files.

"""
import os
import sys
import yaml
import logging
import logging.config


def setup_logging(default_path='logging.yml', default_level=logging.INFO):
    """Setup logging configuration from a YAML file

    Args:
        default_path (str, optional): Defines the relative location of the logging configuration file,
        from the root module. Default value: ``logging.yml``
        default_level (logging attr, optional): Sets the default logging level. Default value: logging.INFO

    Returns:
        None

    """
    if os.path.exists(default_path):
        with open(default_path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


logger = logging.getLogger(__name__)
setup_logging(default_path='logging.yml', default_level=logging.INFO)


def constant(f):
    """setters and getters for constants used throughout

    Prevents setting of existing objects. Raises a TypeError.

    Return:
        property

    Raises:
        TypeError: On setter.

    """

    def fset(value):
        raise TypeError

    def fget():
        return f()

    return property(fget, fset)


class LogLevelsConsts(object):
    """Logger level equivalent strings as constants, used to pass log level to helper functions.

    Attributes:
        DEBUG (str): String matching DEBUG logger level.
        INFO (str): String matching INFO logger level.
        WARNING (str): String matching WARNING logger level.
        CRITICAL (str): String matching CRITICAL logger level.
        ERROR (str): String matching ERROR logger level.

    """
    @constant
    def DEBUG(self):
        return 'DEBUG'

    @constant
    def INFO(self):
        return 'INFO'

    @constant
    def WARNING(self):
        return 'WARNING'

    @constant
    def CRITICAL(self):
        return 'CRITICAL'

    @constant
    def ERROR(self):
        return 'ERROR'


def config_logger(name, class_name=None):
    """Allows a logger to be set up and/or configured in all modules/module classes

    Args:
        name (str): Name of the logger.
        class_name (str, optional): Name of the class to which the logger is associated. Default value: None

    Returns:
        logging (obj): A configured logger object.

    """

    if class_name is None:
        logr = logging.getLogger('{}'
                                 .format(name))
        setup_logging(default_path='logging.yml', default_level=logging.INFO)
    else:
        logr = logging.getLogger('{}.{}'
                                 .format(name, class_name))

    return logr


def sect_break(logr, level=LogLevelsConsts.INFO):
    """Inserts a section break in the logger output.

    Args:
        logr (obj): A logger object to pass the section break to.
        level (attr of LogLevelsConsts obj, optional): Logger level of the section break.
            Default value: LogLevelsConsts.INFO

    Returns:
        None

    """
    delimit = '*' * 80
    try:
        if level == LogLevelsConsts.DEBUG:
            logr.debug(delimit)
        elif level == LogLevelsConsts.INFO:
            logr.info(delimit)
        elif level == LogLevelsConsts.WARNING:
            logr.warning(delimit)
        elif level == LogLevelsConsts.CRITICAL:
            logr.critical(delimit)
        elif level == LogLevelsConsts.ERROR:
            logr.error(delimit)
        else:
            logr.info(delimit)
    except AttributeError as e:
        logr.error('{}'
                   .format(__name__))
        logr.error('\t{}'
                   .format(e))


def errorexit(logr):
    """Inserts a exit on error message in the logger output and performs a ``sys.exit(-1)``

    Args:
        logr (obj): A logger object to pass the exit on error message to.

    Returns:
        None

    """
    logr.error('')
    logr.error('Exiting...')
    sys.exit(-1)


def mand_missing(obj, field):
    """Inserts a mandatory field missing error message in the logger output and calls ``errorexit()``

    Args:
        logr (obj): A logger object to pass the error message to.
        field (str): field to report in the error message.

    Returns:
        None

    """
    obj.logger.error('Missing Mandatory Field in: {obj.settings_file}'
                     .format(obj=obj))
    obj.logger.error('{obj.category}'
                     .format(obj=obj))
    obj.logger.error('  {field}: <VALUE>'
                     .format(field=field))
    errorexit(obj.logger)


def path_missing(obj, name, path):
    """Inserts a path missing error message in the logger output and calls ``errorexit()``

    Args:
        logr (obj): A logger object to pass the error message to.
        name (str): Name of processing element which caused the error message.
        path (str): Missing Path which caused the error message.

    Returns:
        None

    """
    obj.logger.error('Processing: {name}'
                     .format(name=name))
    obj.logger.error('Path Missing on File-System: {path}'
                     .format(path=path))
    errorexit(obj.logger)


# Logging is required to be setup and configured prior to loading version modules
import version as my_version
rev = filter(str.isdigit, "$Rev$")  # Do Not Modify this Line
version = my_version.Version(0, 4, 0, svn_rev=rev, disable_svn_logging=True)
__version__ = version.get_version()
__str__ = my_version.about(__name__, __version__, version.revision)
