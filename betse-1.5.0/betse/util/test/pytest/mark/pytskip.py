#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Decorators skipping tests.

These decorators conditionally mark their decorated tests as skipped depending
on whether the conditions signified by the passed parameters are satisfied
(e.g., the importability of the passed module name).
'''

# ....................{ IMPORTS                            }....................
import pytest
from betse.util.type.types import (
    type_check,
    CallableTypes,
    ClassType,
    MappingOrNoneTypes,
    SequenceOrNoneTypes,
    StrOrNoneTypes,
)
from betse.util.test.pytest.mark import pytmark

# ....................{ IMPORTS ~ private                  }....................
# Sadly, the following imports require private modules and packages.
from _pytest.runner import Skipped

# ....................{ SKIP                               }....................
skip_if = pytest.mark.skipif
'''
Conditionally skip the decorated test or fixture with the passed human-readable
justification if the passed boolean is ``False``.

Parameters
----------
boolean : bool
    Boolean to be tested.
reason : str
    Human-readable message justifying the skipping of this test or fixture.
'''


@type_check
def skip(reason: str):
    '''
    Unconditionally skip the decorated test with the passed human-readable
    justification.

    This decorator is intended to be called both directly as a function *and*
    indirectly as a decorator, which differs from both:

    * :func:`pytest.skip`, intended to be called only directly as a function.
      Attempting to call this function indirectly as a decorator produces
      extraneous ignorable messages on standard output resembling
      ``"SKIP [1] betse_test/unit/test_import.py:66: could not import
      'xdist'"``, for unknown (and probably uninteresting) reasons.
    * :func:`pytest.mark.skip`, intended to be called only indirectly as a
      decorator. Attempting to call this decorator directly as a function
      reduces to a noop, for unknown (and probably uninteresting) reasons.

    Parameters
    ----------
    reason : str
        Human-readable message justifying the skipping of this test.
    '''

    return skip_if(True, reason=reason)

# ....................{ SKIP ~ command                     }....................
@type_check
def skip_unless_command(pathname: str):
    '''
    Skip the decorated test unless a command with the passed path exists.

    This is the case if this path is neither:

    * The basename of an executable file in the current ``${PATH}``.
    * The relative or absolute path of an executable file.

    This decorator is typically applied to tests requiring optional third-party
    external commands.

    Parameters
    ----------
    pathname : str
        Basename or absolute or relative path of the executable file to
        inspect.

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator successfully reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.util.os.command import cmds

    # If this command exists, reduce this decoration to a noop.
    if cmds.is_command(pathname):
        return pytmark.noop
    # Else, skip this test with a human-readable justification.
    else:
        return skip('Command "{}" not found.'.format(pathname))

# ....................{ SKIP ~ host                        }....................
def skip_if_ci_gitlab():
    '''
    Skip the decorated test if tests are currently running under a remote
    GitLab-CI continuous integration (CI) host.

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator successfully reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.util.test import tstci

    # Skip this test or fixture if tests are remotely running under GitLab-CI.
    return skip_if(tstci.is_ci_gitlab(), reason=(
        'Test or fixture currently incompatible with GitLab-CI.'))

# ....................{ SKIP ~ lib                        }....................
@type_check
def skip_unless_matplotlib_anim_writer(writer_name: str):
    '''
    Skip the decorated test unless the external command underlying the
    matplotlib animation writer with the passed name is in the current
    ``${PATH}`` (e.g., for the ``imagemagick`` writer, if the ``convert``
    command  is found).

    Parameters
    ----------
    writer_name : str
        Name of the matplotlib animation writer to be inspected.

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator successfully reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.lib.matplotlib.writer import mplvideo

    # If this command exists, reduce this decoration to a noop.
    if mplvideo.is_writer(writer_name):
        return pytmark.noop
    # Else, skip this test with a human-readable justification.
    else:
        return skip(
            'Matplotlib animation writer "{}" either '
            'not found or unrecognized.'.format(writer_name))

# ....................{ SKIP ~ lib : optional              }....................
@type_check
def skip_unless_lib_runtime_optional(*lib_names: str):
    '''
    Skip the decorated test if one or more of the optional runtime dependencies
    of this application with the passed :mod:`setuptools`-specific project
    names are **unsatisfiable** (i.e., unimportable *or* of unsatisfactory
    version).

    Parameters
    ----------
    lib_names : str
        Tuple of the names of all :mod:`setuptools`-specific projects
        identifying these dependencies (e.g., ``NetworkX``).

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.exceptions import BetseLibException
    from betse.lib import libs

    # Skip this test if one or more such dependences are unsatisfiable.
    #
    # Note that the lower-level libs.die_unless_requirements_dict_keys()
    # function is intentionally called in lieu of the higher-level
    # libs.die_unless_runtime_optional() function. Why? Because the latter
    # assumes the application metadata singleton to have already been
    # initialized. Due to chicken-and-egg issues during test collection, this
    # initialization cannot be guaranteed prior to such test collection. Ergo,
    # the lower-level approach is preferred.
    return _skip_if_callable_raises_exception(
        exception_type=BetseLibException,
        func=libs.die_unless_runtime_optional,
        args=lib_names,
    )

# ....................{ SKIP ~ lib : requirement           }....................
@type_check
def skip_if_requirement(*requirements_str: str):
    '''
    Skip the decorated test if one or more of the dependencies identified by
    the passed :mod:`setuptools`-formatted requirement strings are
    **satisfiable** (i.e., importable *and* of satisfactory version).

    Parameters
    ----------
    requirements_str : str
        Tuple of all :mod:`setuptools`-formatted requirement strings
        identifying these dependencies (e.g., ``Numpy >= 1.8.0``).

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.exceptions import BetseLibException
    from betse.lib.libs import die_unless_runtime_optional
    # from betse.lib.setuptools import setuptool
    from betse.util.type.text.string import strjoin

    # Human-readable message justifying the skipping of this test or fixture.
    reason = 'Test or fixture currently incompatible with {}.'.format(
        strjoin.join_as_conjunction_double_quoted(*requirements_str))

    # Skip this test if one or more such dependences are satisfiable.
    return _skip_unless_callable_raises_exception(
        exception_type=BetseLibException,
        func=die_unless_runtime_optional,
        # func=setuptool.die_unless_requirements_str,
        args=requirements_str,
        reason=reason,
    )


@type_check
def skip_unless_requirement(*requirements_str: str):
    '''
    Skip the decorated test if one or more of the dependencies identified by
    the passed :mod:`setuptools`-formatted requirement strings are
    **unsatisfiable** (i.e., unimportable *or* of unsatisfactory version).

    Parameters
    ----------
    requirements_str : str
        Tuple of all :mod:`setuptools`-formatted requirement strings
        identifying these dependencies (e.g., ``Numpy >= 1.8.0``).

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.exceptions import BetseLibException
    from betse.lib.libs import die_unless_runtime_optional
    # from betse.lib.setuptools import setuptool

    # Skip this test if one or more such dependences are unsatisfiable.
    return _skip_if_callable_raises_exception(
        exception_type=BetseLibException,
        func=die_unless_runtime_optional,
        # func=setuptool.die_unless_requirements_str,
        args=requirements_str,
    )

# ....................{ SKIP ~ module                      }....................
@type_check
def skip_unless_module(module_name: str, minimum_version: str = None):
    '''
    Skip the decorated test if the module with the passed name is unimportable
    *or* importable but of a version less than the passed minimum version if
    non-``None``.

    Note that tests requiring optional third-party Python dependencies should
    call the higher-level :func:`skip_unless_lib_runtime_optional` decorator
    instead, which implicitly validates the versions of those dependencies
    rather than requiring those versions be explicitly passed.

    Caveats
    ----------
    The higher-level :func:`skip_unless_lib_runtime_optional` and
    :func:`skip_unless_requirement` decorators (which are implemented in terms
    of robust :mod:`setuptools` machinery) should typically be called in lieu
    of this lower-level decorator (which is implemented in terms of fragile
    :mod:`importlib` machinery).

    Parameters
    ----------
    module_name : str
        Fully-qualified name of the module to be tested for.
    minimum_version : Optional[str]
        Optional minimum version of this module as a dot-delimited string
        (e.g., ``0.4.0``) to be tested for if any *or* ``None`` otherwise, in
        which case any version is acceptable. Defaults to ``None``.

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator reducing to a noop otherwise.

    See Also
    ----------
    :func:`skip_unless_lib_runtime_optional`
        Higher-level decorator skipping the decorated test if the passed
        optional runtime dependency is unsatisfiable.
    '''

    return _skip_if_callable_raises_exception(
        exception_type=Skipped,
        func=pytest.importorskip,
        args=(module_name, minimum_version),
    )

# ....................{ SKIP ~ os                          }....................
def skip_if_os_macos():
    '''
    Skip the decorated test if tests are currently running under an operating
    system running the Apple macOS kernel.

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator successfully reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.util.os.brand.macos import is_macos

    # Skip this test or fixture if tests are running under macOS.
    return skip_if(is_macos(), reason=(
        'Test or fixture currently incompatible with Apple macOS.'))


def skip_if_os_windows_vanilla():
    '''
    Skip the decorated test if tests are currently running under an operating
    system running the vanilla (i.e., neither Cygwin nor the Windows Subsystem
    for Linux (WSL)) Microsoft Windows kernel.

    Returns
    ----------
    pytest.skipif
        Decorator describing these requirements if unmet *or* the identity
        decorator successfully reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.util.os.brand.windows import is_windows_vanilla

    # Skip this test or fixture if tests are running under Windows.
    return skip_if(is_windows_vanilla(), reason=(
        'Test or fixture currently incompatible with '
        'vanilla Microsoft Windows.'
    ))

# ....................{ SKIP ~ plugin                      }....................
def skip_unless_plugin_xdist():
    '''
    Skip the decorated test if the ``pytest-xdist`` plugin is *not* installed.

    This decorator is typically applied to tests requiring **process
    isolation** (i.e., isolating tests to dedicated subprocesses of the current
    test session).  While this plugin provides such isolation out-of-the-box,
    vanilla :mod:`pytest` does not. Hence, these tests *must* be skipped in the
    absence of this plugin.

    Examples of tests requiring process isolation include:

    * Unit tests testing importability. Since Python caches imports performed
      by the active Python interpreter (e.g., via :attr:`sys.modules`) *and*
      since the order in which :mod:`pytest` runs tests should be assumed to be
      non-deterministic, importability *cannot* be reliably tested within a
      single Python process.
    '''

    return skip_unless_module('xdist')

# ....................{ PRIVATE ~ skip                     }....................
@type_check
def _skip_if_callable_raises_exception(
    # Mandatory parameters.
    exception_type: ClassType,
    func: CallableTypes,

    # Optional parameters.
    args: SequenceOrNoneTypes = None,
    kwargs: MappingOrNoneTypes = None,
):
    '''
    Skip the decorated test if calling the passed callable with the passed
    positional and keyword arguments raises an exception of the passed type.

    Specifically, if calling this callable raises:

    * The passed type of exception, this test is marked as skipped.
    * Any other type of exception, this test is marked as a failure.
    * No exception, this test continues as expected.

    Parameters
    ----------
    exception_type : ClassType
        Type of exception expected to be raised by this callable.
    func : CallableTypes
        Callable to be called.
    args : SequenceOrNoneTypes
        Sequence of all positional arguments to unconditionally pass to the
        passed callable if any *or* ``None`` otherwise. Defaults to ``None``.
    kwargs : MappingOrNoneTypes
        Dictionary of all keyword arguments to unconditionally pass to the
        passed callable if any *or* ``None`` otherwise. Defaults to ``None``.

    Returns
    ----------
    pytest.skipif
        Decorator skipping this test if this callable raises this exception
        *or* the identity decorator reducing to a noop otherwise.
    '''

    # Default all unpassed arguments to sane values.
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}

    # Attempt to call this callable with these arguments.
    try:
        func(*args, **kwargs)
    # If this callable raises an expected exception, skip this test.
    except exception_type as exception:
        return skip(str(exception))
    # If this callable raises an unexpected exception, fail this test. To
    # preserve this exception's stack trace, reraise this exception as is.
    except Exception:
        raise
        # # Print this exception's stacktrace to stderr.
        # stderrs.output_exception(heading=(
        #     'skip_unless_lib_runtime_optional{} '
        #     'raised unexpected exception:\n'.format(lib_names)))
        #
        # # Skip this test with this exception's message.
        # return skip(str(exception))
    # Else, this callable raised no exception. Silently reduce to a noop.
    else:
        return pytmark.noop


@type_check
def _skip_unless_callable_raises_exception(
    # Mandatory parameters.
    exception_type: ClassType,
    func: CallableTypes,

    # Optional parameters.
    args: SequenceOrNoneTypes = None,
    kwargs: MappingOrNoneTypes = None,
    reason: StrOrNoneTypes = None,
):
    '''
    Skip the decorated test unless calling the passed callable with the passed
    positional and keyword arguments raises an exception of the passed type.

    Specifically, if calling this callable raises:

    * The passed type of exception, this test continues as expected.
    * Any other type of exception, this test is marked as a failure.
    * No exception, this test is marked as skipped.

    Parameters
    ----------
    exception_type : ClassType
        Type of exception expected to be raised by this callable.
    func : CallableTypes
        Callable to be called.
    args : SequenceOrNoneTypes
        Sequence of all positional arguments to unconditionally pass to the
        passed callable if any *or* ``None`` otherwise. Defaults to ``None``.
    kwargs : MappingOrNoneTypes
        Dictionary of all keyword arguments to unconditionally pass to the
        passed callable if any *or* ``None`` otherwise. Defaults to ``None``.
    reason : StrOrNoneTypes
        Human-readable message justifying the skipping of this test or fixture.
        Defaults to ``None``, in which case this function utilizes a
        general-purpose message generically applicable to all tests.

    Returns
    ----------
    pytest.skipif
        Decorator skipping this test if this callable does *not* raise this
        exception *or* the identity decorator reducing to a noop otherwise.
    '''

    # Defer heavyweight imports.
    from betse.util.type.cls import classes

    # Default all unpassed arguments to sane values.
    if args is None:
        args = ()
    if kwargs is None:
        kwargs = {}
    if reason is None:
        reason = 'Test or fixture failed to raise exception "{}".'.format(
            classes.get_name_unqualified(exception_type))

    # Attempt to call this callable with these arguments.
    try:
        func(*args, **kwargs)
    # If this callable raises an expected exception, reduce to a noop.
    except exception_type:
        return pytmark.noop
    # If this callable raises an unexpected exception, fail this test. To
    # preserve this exception's stack trace, reraise this exception as is.
    except Exception:
        raise
    # Else, this callable raised no exception. Skip this test.
    else:
        return skip(reason)
