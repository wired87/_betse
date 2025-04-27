#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Low-level **warning** (i.e., non-fatal errors with associated types emitted by
the standard :mod:`warnings` module) facilities.
'''

# ....................{ IMPORTS                            }....................
import sys, warnings
from beartype.typing import (
    ContextManager,
    Iterator,
)
from betse.util.io.log import logs
from betse.util.type.types import ClassType
from contextlib import contextmanager

# ....................{ INITIALIZERS                       }....................
def init() -> None:
    '''
    Initialize this submodule.

    Specifically, this function conditionally establishes a default warning
    filter as follows:

    * If the end user explicitly passed the ``-W`` option to the external
      command forking the active Python interpreter (e.g., via ``python3 -W -m
      betse``) and hence expressed one or more warning preferences, defer to
      these preferences as is.
    * Else if this application has a Git-based working tree and is thus likely
      to be under active development, unconditionally log *all* warnings
      (including those ignored by default).
    * Else, preserve the default warning filter defined by the standard
      :mod:`warnings` module.
    '''

    # Avoid circular import dependencies.
    from betse.util.app.meta import appmetaone
    from betse.util.test import tsttest

    # Log this initialization.
    logs.log_debug('Initializing warning policy...')

    # If the end user explicitly passed the "-W" option to the external command
    # forking the active Python interpreter (and hence expressed a warning
    # preference), defer to these preferences.
    if sys.warnoptions:
        logs.log_debug(
            'Deferring warning policy to '
            '"-W" option passed to Python interpreter.')
    # Else if the active Python interpreter is currently exercising tests,
    # defer to the test harness supervising these tests. Most harnesses
    # (including pytest) define sane default warnings filters as well as
    # enabling users to externally configure warnings filters from project-wide
    # configuration files. Ergo, the current harness knows better than we do.
    elif tsttest.is_testing():
        logs.log_debug(
            'Deferring warning policy to that of the parent test harness.')
    # Else...
    else:
        # If this application has a Git-based working tree and is thus likely
        # to be under active development...
        if appmetaone.get_app_meta().is_git_worktree:
            # Log this preference.
            logs.log_debug(
                'Setting warning policy to '
                'unconditionally log all warnings '
                '(i.e., due to detecting developer environment).')

            # Discard all previously registered warnings filter *BEFORE*
            # registering a warnings filter.
            warnings.resetwarnings()

            # Registering a warnings filter unconditionally logging *ALL*
            # warnings, including those Python ignores by default.
            warnings.simplefilter('default')
        # Else, preserve Python's default warning filter as is.
        else:
            logs.log_debug('Deferring to default warning policy.')

# ....................{ MANAGERS                           }....................
def ignoring_deprecations() -> ContextManager:
    '''
    Single-shot context manager temporarily ignoring all **deprecation
    warnings** (i.e., instances of the :class:`DeprecationWarning`,
    :class:`PendingDeprecationWarning`, and :class:`FutureWarning` exception
    base classes) emitted by the :mod:`warnings` module for the duration of
    this context.

    See Also
    -----------
    :class:`ignoring_warnings`
        Further details.
    '''

    return ignoring_warnings(
        DeprecationWarning,
        PendingDeprecationWarning,
        FutureWarning,
    )


@contextmanager
def ignoring_warnings(*warning_clses: ClassType) -> Iterator[None]:
    '''
    Single-shot context manager temporarily ignoring *all* warnings of *all*
    passed warning types emitted by the :mod:`warnings` module for the duration
    of this context.

    Caveats
    -----------
    This context manager is single-shot and hence *not* safely reusable across
    multiple ``with`` blocks. Why? Because the low-level
    :class:`warnings.catch_warnings` class to which this context manager defers
    is itself single-shot, explicitly raising exceptions on reuse. While
    lamentable, this overhead appears to be unavoidable.

    Parameters
    -----------
    warning_clses : Tuple[ClassType]
        Tuple of zero or more warning classes to be ignored by this context
        manager. Defaults to a tuple containing only the :class:`Warning`
        superclass of all warning subclasses (both builtin and user-defined),
        in which case this context manager ignores *all* warnings.
    '''

    # If no types were passed, default to the "Warning" superclass.
    if not warning_clses:
        warning_clses = (Warning,)

    # Isolate all side effects produced by the "warnings" module to this block.
    with warnings.catch_warnings():
        # For each class of warning to ignore...
        for warning_cls in warning_clses:
            # Temporarily ignore all instances of this warning class.
            warnings.simplefilter(action='ignore', category=warning_cls)

        # Yield control to the body of the caller's "with" block.
        yield
