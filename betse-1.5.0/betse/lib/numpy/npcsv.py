#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
High-level facilities for serializing and deserializing Numpy arrays to and
from comma-separated value (CSV) files.
'''

# ....................{ IMPORTS                           }....................
import numpy as np
from beartype import beartype
from beartype.typing import (
    Dict,
    Iterable,
    Optional,
)
from betse.exceptions import BetseSequenceException, BetseStrException
from betse.util.io.log import logs
from betse.util.path import dirs
from betse.util.type import types

# ....................{ WRITERS                           }....................
#FIXME: Donate this function back to Numpy as a new np.savecsv() function
#paralleling the existing np.savetxt() function.
@beartype
def write_csv(
    # Mandatory parameters.
    filename: str,
    column_name_to_values: Dict[str, Iterable],

    # Optional parameters.
    column_name_to_format: Optional[Dict[str, str]] = None,
) -> None:
    '''
    Serialize each key-value pair of the passed ordered dictionary into a new
    column in comma-separated value (CSV) format to the plaintext file with the
    passed filename.

    Caveats
    ----------
    To ensure that all columns of this file have the same number of rows, all
    values of this dictionary *must* be one-dimensional sequences of:

    * The same length. If this is not the case, an exception is raised.
    * Any type satisfying the :class:`SequenceTypes` API, including:

      * Numpy arrays.
      * Lists.
      * Tuples.

    Typically, each such value is a one-dimensional Numpy array of floats.

    Parameters
    ----------
    filename : str
        Absolute or relative path of the plaintext file to be written. If this
        file already exists, this file is silently overwritten.
    column_name_to_values: Dict[str, Iterable]
        Dictionary of all columns to be serialized such that:

        * Each key of this dictionary is a **column name** (i.e., terse string
          describing the type of data contained in this column).
        * Each value of this dictionary is **column data** (i.e.,
          one-dimensional sequence of all arbitrary data comprising this
          column).
    column_name_to_format : Optional[Dict[str, str]]
        Dictionary of all format strings formatting each column such that:

        * Each key of this dictionary is a **column name** (i.e., terse string
          describing the type of data contained in this column).
        * Each key of this dictionary is a **format string** (i.e.,
          ``%``-prefixed format string as fully documented by the "list of
          specifiers, one per column" subsection for the ``fmt`` parameter
          accepted by the low-level :func:`numpy.savetxt` function wrapped by
          this high-level writer function).

        This dictionary *must* have the exact same keys as the
        ``column_name_to_values`` dictionary.  Defaults to ``None``, in which
        case NumPy unconditionally defaults to reasonable floating-point format
        strings for *all* columns.

    Raises
    ----------
    BetseSequenceException
        If one or more values of this dictionary are either:

        * *Not* sequences.
        * Sequences whose length differs from that of any preceding value
          sequences of this dictionary.
    BetseStrException
        If this column name contains one or more characters reserved for use by
        the CSV non-standard, including:

        * Double quotes, reserved for use as the CSV quoting character.
        * Newlines, reserved for use as the CSV row delimiting character.
    '''

    # Avoid circular import dependencies.
    from betse.util.type.text.string import strjoin

    # Log this serialization.
    logs.log_debug('Writing CSV file: %s', filename)

    # Tuple of all format strings to be passed to the numpy.savetxt() function
    # below (in column order), defaulting to the same format string as accepted
    # by that function for simplicity.
    columns_format = '%.18e'

    # If passed a dictionary of format strings...
    if column_name_to_format is not None:
        # If the column names listed by this dictionary from those listed by
        # the dictionary of values, raise an exception.
        if column_name_to_format.keys() != column_name_to_values.keys():
            raise BetseSequenceException(
                f'"column_name_to_format" keys '
                f'{repr(column_name_to_format.keys())} != '
                f'"column_name_to_values" keys '
                f'{repr(column_name_to_values.keys())} != '
            )
        # Else, these column names coincide.

        # Tuple of these format strings (in the same order).
        columns_format = tuple(
            column_format
            for column_format in column_name_to_format.values()
        )

    # Create the directory containing this file if needed and hence raise
    # filesystem-related exceptions *BEFORE* performing any subsequent logic.
    dirs.make_parent_unless_dir(filename)

    # Validate the contents of this dictionary. While the np.column_stack()
    # function called below also does, the exceptions raised by the latter are
    # both ambiguous and non-human-readable and hence effectively useless.
    #
    # Length of all prior columns *OR* "None" if no columns have been iterated.
    columns_prior_len = None

    # List of all column names sanitized such that each name containing one or
    # more comma characters is double-quoted.
    column_names = []

    # For each passed column...
    for column_name, column_values in column_name_to_values.items():
        # If this column is *NOT* a sequence, raise a human-readable exception.
        if not types.is_sequence_nonstr(column_values):
            raise BetseSequenceException(
                'Column "{}" type {!r} not a sequence.'.format(
                    column_name, type(column_values)))

        # Length of this column.
        column_len = len(column_values)

        # If this is the first column to be iterated, require all subsequent
        # columns be of the same length.
        if columns_prior_len is None:
            columns_prior_len = column_len
        # Else if this column's length differs from that of all prior columns,
        # raise a human-readable exception.
        elif column_len != columns_prior_len:
            raise BetseSequenceException(
                'Column "{}" length {} differs from '
                'length {} of prior columns.'.format(
                    column_name, column_len, columns_prior_len))

        # If this column name contains one or more reserved characters, raise
        # an exception. This includes:
        #
        # * Double quotes, reserved for use as the CSV quoting character.
        # * Newlines, reserved for use as the CSV row delimiting character.
        if '"' in column_name:
            raise BetseStrException(
                'Column name {} contains '
                "one or more reserved '\"' characters.".format(column_name))
        if '\n' in column_name:
            raise BetseStrException(
                'Column name {} contains '
                'one or more newline characters.'.format(column_name))

        # If this column name contains one or more commas (reserved for use as
        # the CSV delimiter), double-quote this name. Since the prior logic
        # guarantees this name to *NOT* contain double quotes, no further logic
        # is required
        if ',' in column_name:
            column_name = '"{}"'.format(column_name)

        # Append this sanitized column name to this list of such names.
        column_names.append(column_name)

    # Comma-separated string listing all column names.
    columns_name = strjoin.join_on(column_names, delimiter=',')

    # Two-dimensional sequence of all column data, whose:
    #
    # * First dimension indexes each column.
    # * Second dimension indexes each data point in that column.
    columns_values = tuple(column_name_to_values.values())

    # Two-dimensional Numpy array of all row data converted from this column
    # data, whose:
    #
    # * First dimension indexes each sampled time step such that each item is a
    #   one-dimensional Numpy array of length the number of columns (i.e., the
    #   number of key-value pairs in the passed dictionary).
    # * Second dimension indexes each column data point for that time step.
    #
    # Note that passing "column_name_to_values.values()" no longer suffices
    # under NumPy >= 1.16. Because breaking backward compatibility for utterly
    # no good reason is Now A Good Thing, the np.column_stack() function now
    # longer accepts arbitrary iterables but now requires strict sequences:
    #
    #     FutureWarning: arrays to stack must be passed as a "sequence" type
    #     such as list or tuple. Support for non-sequence iterables such as
    #     generators is deprecated as of NumPy 1.16 and will raise an error in
    #     the future.
    #
    # Converting non-sequence iterables to sequences is trivial, ignoring the
    # obvious edge case of infinite generators, which -- much like the
    # legendary Pokemon of yore -- appear not to exist in the wild. Ergo, the
    # NumPy developers yet again chose poorly. *STOP BREAKING EVERYTHING.*
    rows_values = np.column_stack(columns_values)

    # Serialize these sequences to this file in CSV format.
    np.savetxt(
        fname=filename,
        X=rows_values,
        fmt=columns_format,
        header=columns_name,
        delimiter=',',

        # Prevent Numpy from prefixing the above header by "# ". Most popular
        # software importing CSV files implicitly supports a comma-delimited
        # first line listing all column names.
        comments='',
    )
