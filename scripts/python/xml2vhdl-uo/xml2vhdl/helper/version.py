# -*- coding: utf8 -*-
"""

*********************
``helper/version.py``
*********************

`BSD`_ © 2018-2019 Science and Technology Facilities Council  & contributors

.. _BSD: _static/LICENSE

``version.py`` is a helper module provided to handle public version numbering which follows the
PEP440 guidelines.

.. note::

   The ``__version__`` uses the :mod:`version.Version` (defined in this module), therefore is used
   towards the end of this module.

"""
import customlogging as log
logger = log.config_logger(name=__name__)


def about(modname, ver, revision):
    """Method to Create an About String, to display Method Name and Version/Rev

    Args:
        modname (str): Module Name
        ver (str):  Version Number, in the form: ``MAJOR.MINOR.MICRO``
        revision (str): ``SVN`` Revision Number

    Returns:
        str:

    """
    return "{modname} {ver} {revision}".format(modname=modname, ver=ver, revision=revision)


class Version:
    """Creates a Class with methods to construct and fetch PEP440 Public Version Numbering

    Creates an initial PEP440 Public Version Identifier from the supplied parameters after validating the
    prerelease parameter,

    Args:
        major (int): Representing the Major Version Number (changes affecting execution method)
        minor (int): Representing the Minor Version Number (bugfixes)
        micro (int): Representing the Micro Version Number (correction of typos/release notes)
        prerelease (int, optional): Addition Pre-Release Indicator. Valid values: ``a``, ``b``, ``rc``,
            where: ``a`` = alpha; ``b`` = beta; and ``rc`` = release candidate
        svn_rev (str, optional): ``SVN`` Revision Number
        disable_svn_logging (bool): Do not include ``SVN`` output in logs. Default value: ``False``

    """
    def __init__(self, major, minor, micro, prerelease='', svn_rev='', disable_svn_logging=False):
        self.logger = log.config_logger(name=__name__, class_name=self.__class__.__name__)
        self._svn_rev = svn_rev
        self.revision = self._validate_svn_rev(self._svn_rev, disable_logging=disable_svn_logging)
        self._major = major
        self._minor = minor
        self._micro = micro
        self._pre = prerelease
        self.version = self.set_version(self._major, self._minor, self._micro, self._pre)

    def __repr__(self):
        return "{self.__class__.__name__}({self._major}, {self._minor}, " \
               "{self._micro}, prerelease='{self._pre}', svn_rev='{self._svn_rev}')".format(self=self)

    def __str__(self):
        return "{self.version} {self.revision}".format(self=self)

    def _validate_svn_rev(self, svn_rev, disable_logging=True):
        """
        Method which checks the SVN Revision Number (normally derived from parsing ``SVN`` ``REV`` Keyword
        Substitution and returns a string. Invalid and empty values return an empty str with a critical
        logger level message.

        If an empty str is passed to this method it usually means keyword substitution has not been enabled
        on the file calling this method, or the file calling this method has not been committed yet.

        :param svn_rev:
        :return: str
        """
        if svn_rev == '':
            if not disable_logging:
                self.logger.critical("Not a Valid SVN Revision No: {}"
                                     .format(svn_rev))
            rev_str = ''
        else:
            rev_str = "(r{})".format(svn_rev)

        return rev_str

    def _validate_prerelease(self, prerelease):
        """
        Method which checks the Pre-Release value is valid. Valid Pre-Release Indicators Are:
        * ``a`` = alpha
        * ``b`` = beta
        * ``rc`` = release candidate

        This checking is not case sensitive, but lower case values are returned. Invalid types and values
        return an empty str with a critical logger level message.

        :param prerelease:
        :return: str
        """
        try:
            if prerelease == '':
                self.logger.debug("Not a Pre-Release")
                pre = ''
            elif prerelease.lower() == 'a':
                self.logger.debug("An Alpha Release")
                pre = 'a'
            elif prerelease.lower() == 'b':
                self.logger.debug("A Beta Release")
                pre = 'b'
            elif prerelease.lower() == 'rc':
                self.logger.debug("A Release Candidate")
                pre = 'rc'
            else:
                self.logger.critical("Invalid prerelease Value: {}"
                                     .format(prerelease))
                pre = ''
        except AttributeError:
            self.logger.critical("prerelease Doesn't Appear to be a Str: {}"
                                 .format(prerelease))
            pre = ''

        return pre

    def set_version(self, major, minor, micro, pre):
        """

        Method to set the string representation of a Version Number.

        :param major: Integer Value Representing the Major Version Number (changes affecting execution method)
        :param minor: Integer Value Representing the Minor Version Number (bugfixes)
        :param micro: Integer Value Representing the Micro Version Number (correction of typos/release notes)

        :param pre: Optional Addition Pre-Release Indicator...
            a = alpha
            b = beta
            rc = release candidate

        :return: string
        """
        return "{}.{}.{}{}".format(major, minor, micro, self._validate_prerelease(pre))

    def get_version(self):
        """
        Method to get the string representation of the version number.

        :return: String of Version Number
        """
        return self.version


rev = filter(str.isdigit, "$Rev$")  # Do Not Modify this Line
version = Version(1, 1, 0, prerelease='rc', svn_rev=rev, disable_svn_logging=True)

__version__ = version.get_version()
__str__ = about(__name__, __version__, version.revision)
