#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Low-level logging facilities.

Logging Hierarchy
----------
Loggers are hierarchically structured according to their ``.``-delimited names.
Since the name of the root logger is *always* the empty string, this logger is
*always* the parent of all user-defined loggers. This hierarchy is an implicit
consequence of logger names and hence requires no manual intervention (e.g.,
the root logger "" is implicitly the parent of a user-defined logger ``A`` is
implicitly the parent of a user-defined logger ``A.B``).

By default, logger messages are implicitly propagated up the logger hierarchy
(e.g., messages to logger ``A.B`` are implicitly progagated to logger ``A`` are
are implicitly progagated to the root logger). This is a good thing,
effectively reducing child loggers to symbolic names; assuming all loggers
except the root logger to be unconfigured, messages will be logged *only* by
the root logger.
'''

#FIXME: Error messages should be prefixed by strings uniquely identifying the
#sources of those messages. Specifically:
#
#* Warnings should be prefixed by "<Warning> {source_module_basename}".
#* Errors should be prefixed by "<Error> {source_module_basename}".
#
#See the following stackoveflow question for details on how to implement this:
#    https://stackoverflow.com/questions/14844970/modifying-logging-message-format-based-on-message-logging-level-in-python3

#FIXME: The following blog post provides useful instructions on deserializing
#logging settings from a YAML-formatted configuration file. Leveraging such
#instructions, we could permit users to setup logging as they see fit (e.g.,
#configuring the logging file and level). This is probably the preferable means
#of doing so, rather than providing a gamut of CLI options:
#
#    http://victorlin.me/posts/2012/08/26/good-logging-practice-in-python

# ....................{ IMPORTS                            }....................
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# WARNING: To avoid circular import dependencies, avoid importing from *ANY*
# application-specific modules at the top-level -- excluding those explicitly
# known *NOT* to import from this module. Since all application-specific
# modules must *ALWAYS* be able to safely import from this module at any level,
# these circularities are best avoided here rather than elsewhere.
#!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

import logging, sys, traceback
from betse.util.io.log.logenum import LogLevel
from betse.util.type import types
from betse.util.type.types import type_check, StrOrNoneTypes
from logging import Logger

# ....................{ GETTERS                            }....................
@type_check
def get_logger(logger_name: StrOrNoneTypes = None) -> Logger:
    '''
    Logger with the passed ``.``-delimited name, defaulting to the basename of
    the current process (e.g., ``betse``) implying the **global logger** (i.e.,
    the default application-wide logger).

    This function expects the :class:`LogConf` class to have been previously
    instantiated, which globally configures logging.

    Parameters
    ----------
    logger_name : StrOrNoneTypes
        ``.``-delimited name of the logger to retrieve. By convention, logger
        names are typically that of the calling module (e.g., ``__name__``).
        However, since our default logger configuration already dynamically
        embeds the name of the calling module but *not* this logger into log
        records, an explicit logger name need *not* be passed in most cases.
        The exception to this heuristic is third-party dependencies whose
        package-specific loggers require configuration (e.g., to reduce the
        verbosity of messages logged by those loggers), in which case those
        loggers' names should be explicitly passed. Defaults to ``None``, in
        which case the global logger is retrieved.

    Returns
    ----------
    Logger
        Logger with the passed ``.``-delimited name.
    '''

    # Default the name of this logger to the name of the root logger.
    if logger_name is None:
        logger_name = logging.root.name

    # If this name is the empty string, this function would get the root logger.
    # Since this name being empty typically constitutes an implicit error
    # rather than an attempt to get the root logger, prevent this via an
    # assertion.
    assert types.is_str_nonempty(logger_name), (
        types.assert_not_str_nonempty(logger_name, 'Logger name'))

    # Return this logger.
    return logging.getLogger(logger_name)

# ....................{ LOGGERS ~ banner                   }....................
@type_check
def log_banner(*args, **kwargs) -> None:
    '''
    Log a single-line banner described by the passed arguments as an
    informational message with the root logger.

    Since formatting this banner requires this banner's embedded title to be
    preformatted, this function *does* not accept the ``%``-style positional
    and keyword arguments accepted by most other logging functions (e.g.,
    :func:`log_info`).

    This function expects the :class:`LogConf` class globally configuring
    logging to be instantiated as a singleton.

    Parameters
    ----------
    All passed arguments are passed as is to the
    :func:`betse.util.os.shell.shellstr.get_banner` function.
    '''

    # Avoid circular import dependencies.
    from betse.util.os.shell import shellstr

    # Single-line banner embedding the passed human-readable title.
    banner = shellstr.get_banner(*args, **kwargs)

    # Log this banner with level "INFO".
    log_info(banner)

# ....................{ LOGGERS ~ level                    }....................
@type_check
def log_levelled(message: str, level: LogLevel, *args, **kwargs) -> None:
    '''
    Log the passed message of the passed logging level (e.g.,
    :attr:`LogLevel.INFO`) with the root logger, formatted with the passed
    ``%``-style positional and keyword arguments.

    This function expects the :class:`LogConf` class globally configuring
    logging to be instantiated as a singleton.

    Parameters
    ----------
    message : str
        Message to log containing zero or more ``%``-style format specifiers.
    level : LogLevel
        Logging level to log this message with (e.g., :attr:`LogLevel.INFO`).

    ALl remaining parameters are interpolated into the message according to the
    ``%``-style format specifiers embedded in this message.
    '''

    # The Logger.log() method accepts these parameters in the opposite order.
    logging.log(level, message, *args, **kwargs)


@type_check
def log_debug(message: str, *args, **kwargs) -> None:
    '''
    Log the passed debug message with the root logger, formatted with the
    passed ``%``-style positional and keyword arguments.

    This function expects the :class:`LogConf` class globally configuring
    logging to be instantiated as a singleton.
    '''

    logging.debug(message, *args, **kwargs)


@type_check
def log_info(message: str, *args, **kwargs) -> None:
    '''
    Log the passed informational message with the root logger, formatted with
    the passed ``%``-style positional and keyword arguments.

    This function expects the :class:`LogConf` class globally configuring
    logging to be instantiated as a singleton.
    '''

    logging.info(message, *args, **kwargs)


@type_check
def log_warning(message: str, *args, **kwargs) -> None:
    '''
    Log the passed warning message with the root logger, formatted with the
    passed ``%``-style positional and keyword arguments.

    This function expects the :class:`LogConf` class globally configuring
    logging to be instantiated as a singleton.
    '''

    logging.warning(message, *args, **kwargs)


@type_check
def log_error(message: str, *args, **kwargs) -> None:
    '''
    Log the passed error message with the root logger, formatted with the
    passed ``%``-style positional and keyword arguments.

    This function expects the :class:`LogConf` class globally configuring
    logging to be instantiated as a singleton.
    '''

    logging.error(message, *args, **kwargs)

# ....................{ LOGGERS ~ exception                }....................
@type_check
def log_exception(exception: Exception) -> None:
    '''
    Log the passed exception with the root logger.
    '''

    # Attempt to...
    try:
        # Avoid circular import dependencies.
        from betse.util.io import stderrs
        from betse.util.io.error import errexception
        from betse.util.io.log.conf import logconf

        # Terse synopsis and verbose traceback for this exception.
        _, exc_traceback = errexception.get_metadata(exception)

        # Singleton logging configuration for the current Python process.
        log_config = logconf.get_log_conf()

        # Previous minimum level of messages to log to disk.
        log_config_file_level = log_config.file_level

        # Temporarily coerce this to the debug level, ensuring tracebacks are
        # *ALWAYS* at least logged to disk rather than possibly discarded.
        log_config.file_level = LogLevel.DEBUG

        # Attempt to log tracebacks to the error level and hence stderr. Note
        # that we avoid re-printing the synopsis embedded in these tracebacks.
        try:
            log_error(exc_traceback)
        # Revert to the previous level even if an exception is raised.
        finally:
            log_config.file_level = log_config_file_level
    # If this handling raises an exception, catch and print this exception
    # via the standard Python library, guaranteed not to raise exceptions.
    except Exception:
        # Header preceding the exception to be printed.
        exc_heading = 'log_exception() recursively raised exception:\n'

        # If the stderrs.output_exception() function exists, call that
        # function.
        if 'stderrs' in locals():
            stderrs.output_exception(heading=exc_heading)
        # Else, something has gone horribly wrong. Defer to stock functionality
        # in the standard "traceback" module.
        else:
            print(exc_heading, file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
