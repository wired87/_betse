#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
**Tissue profile pickers** (i.e., objects assigning a subset of all cells
matching various criteria to the corresponding tissue profile) classes.
'''

# ....................{ IMPORTS                           }....................
from abc import ABCMeta, abstractmethod
from betse.exceptions import BetseSimConfException
from betse.lib.numpy import nparray
from betse.science.math import toolbox
# from betse.util.io.log import logs
from betse.util.type.types import type_check, NumericSimpleTypes, SequenceTypes
import numpy as np

# ....................{ SUPERCLASS                        }....................
class TissuePickerABC(object, metaclass=ABCMeta):
    '''
    Abstract base class of all **tissue profile picker** (i.e., object
    assigning a subset of all cells matching some criteria to the corresponding
    tissue profile) subclasses.

    Typical criteria for matching cells includes explicit cell indexing,
    randomized cell selection, and image-defined spatial cell location.
    '''

    # ..................{ PICKERS                           }..................
    @abstractmethod
    def pick_cells(
        self,
        cells: 'betse.science.cells.Cells',
        p:     'betse.science.parameters.Parameters',
    ) -> SequenceTypes:
        '''
        One-dimensional Numpy array of the indices of all cells in the passed
        cell cluster selected by this tissue picker, ignoring extracellular
        spaces.

        Parameters
        ----------
        cells : Cells
            Current cell cluster.
        p : Parameters
            Current simulation configuration.

        Returns
        ----------
        SequenceTypes
            One-dimensional Numpy array of the indices of all such cells.
        '''

        pass


    #FIXME: Rather awkward. We actually end up passing the two Numpy arrays
    #embedded in the tuple returned by this method together as separate
    #parameters to other methods throughout the codebase (e.g., the
    #mod_after_cut_event() and remove_cells() methods). Instead:
    #
    #* Define a new simple "TissuePicked" class at the top of this submodule
    #  (e.g., via the betse.util.type.iterable.tuples.make_named_subclass()
    #  class factory function).
    #* This class should provide only the following public fields:
    #  * "cells_index".
    #  * "membs_index".
    #* Refactor this method to create and return an instance of that class.
    #* Refactor all other methods requiring this pair of Numpy arrays to accept
    #  an instance of that class.
    #* Refactor the following pair of instance variables into a single
    #  instance variable whose value is an instance of this class:
    #  * "Simulator.target_inds_cell_o".
    #  * "Simulator.target_inds_mem_o".
    @type_check
    def pick_cells_and_mems(
        self,
        cells: 'betse.science.cells.Cells',
        p:     'betse.science.parameters.Parameters',
    ) -> tuple:
        '''
        2-tuple ``(cells_index, mems_index)`` of one-dimensional Numpy arrays
        of the indices of both all cells *and* cell membranes in the passed
        cell cluster selected by this tissue picker, ignoring extracellular
        spaces.

        By default, this method returns the array returned by the subclass
        implementation of the abstract :meth:`pick_cells` method, mapped from
        cell to cell membrane indices.

        Parameters
        ----------
        cells : Cells
            Current cell cluster.
        p : Parameters
            Current simulation configuration.

        Returns
        ----------
        (ndarray, ndarray)
            2-tuple ``(cells_index, mems_index)``, where:
            * ``cells_index`` is the one-dimensional Numpy array of the indices
              of all subclass-selected cells.
            * ``mems_index`` is the one-dimensional Numpy array of the indices
              of all subclass-selected cell membranes.
        '''

        # One-dimensional Numpy array of the indices of subclass-selected cells.
        cells_index = self.pick_cells(cells, p)

        #FIXME: Ideally, this array would be trivially defined as follows:
        #    mems_index = cells.cell_to_mems[cells_index].flatten()
        #Unfortunately, the two-dimensional Numpy array "cells.cell_to_mems"
        #actually appears to be a one-dimensional array of lists -- which is a
        #bit bizarro-world. To compaund matters, this array's "dtype" is
        #"object" (presumably, because it contains Python lists) rather than
        #the "dtype" of "int" that one might expect. Since this is the case,
        #it's infeasible to even coerce the temporary one-dimensional Numpy
        #array "cells.cell_to_mems[cells_index]" into a two-dimensional array
        #of ints by calling ndarray.astype(int). Frankly, it's all a bit beyond
        #me; until this core issue is resolved, however, the current inelegant
        #and inefficient approach remains.

        # One-dimensional Numpy array of the indices of subclass-selected cell
        # membranes mapped from the array of cell indices.
        # logs.log_debug('cells_index: %r', cells_index)
        mems_index = cells.cell_to_mems[cells_index]
        mems_index, _, _ = toolbox.flatten(mems_index)
        mems_index = nparray.from_iterable(mems_index)

        # Return these arrays.
        return cells_index, mems_index

# ....................{ SUBCLASSES                        }....................
class TissuePickerAll(TissuePickerABC):
    '''
    All-inclusive tissue picker, unconditionally matching *all* cells in the
    current cell cluster.
    '''

    # ..................{ PICKERS                           }..................
    @type_check
    def pick_cells(
        self,
        cells: 'betse.science.cells.Cells',
        p:     'betse.science.parameters.Parameters',
    ) -> SequenceTypes:

        return cells.cell_i


class TissuePickerColor(TissuePickerABC):
    '''
    Vector image-based tissue picker, matching all cells in the current cell
    cluster whose cell centres are simple circles with a given fill color of a
    vector image (defined by the ``cells from svg`` setting in the current
    YAML-formatted simulation configuration file).

    Attributes
    ----------
    cells_color : str
        **Hexadecimal-formatted color** (i.e., string of six hexadecimal digits
        specifying this color's red, green, and blue components) of all circles
        within this vector image to be selected as cell centres.
    '''

    # ..................{ INITIALIZERS                      }..................
    @type_check
    def __init__(self, cells_color: str) -> None:
        '''
        Initialize this tissue picker.

        Parameters
        ----------
        cells_color : str
            **Hexadecimal-formatted color** (i.e., string of six hexadecimal
            digits, specifying this color's red, green, and blue components) of
            all circles within this vector image to be selected as cell
            centres.
        '''

        self.cells_color = cells_color

    # ..................{ PICKERS                           }..................
    @type_check
    def pick_cells(
        self,
        cells: 'betse.science.cells.Cells',
        p:     'betse.science.parameters.Parameters',
    ) -> SequenceTypes:

        # If no cell cluster SVG is enabled, raise an exception.
        if cells.seed_fills is None:
            raise BetseSimConfException(
                'Color-based cell targets type requires '
                'cell cluster SVG to be enabled.')

        # Search for cells matching the tissue profile color.
        selected_cells = []

        for i, fi in enumerate(cells.seed_fills):
            if fi == self.cells_color:
                selected_cells.append(i)

        return selected_cells


class TissuePickerIndices(TissuePickerABC):
    '''
    Cell indices-based tissue picker, matching all cells in the current cell
    cluster whose indices are defined by a given sequence.

    Attributes
    ----------
    cells_index : SequenceTypes
        Sequence of the indices of all cells to match.
    '''

    # ..................{ INITIALIZERS                      }..................
    @type_check
    def __init__(self, cells_index: SequenceTypes) -> None:
        '''
        Initialize this tissue picker.

        Parameters
        ----------
        cells_index : SequenceTypes
            Sequence of the indices of all cells to match.
        '''

        self.cells_index = cells_index

    # ..................{ PICKERS                           }..................
    @type_check
    def pick_cells(
        self,
        cells: 'betse.science.cells.Cells',
        p:     'betse.science.parameters.Parameters',
    ) -> SequenceTypes:

        return self.cells_index


class TissuePickerPercent(TissuePickerABC):
    '''
    Randomized cell picker, randomly matching a given percentage of all cells
    in the current cell cluster.

    Attributes
    ----------
    cells_percent : NumericSimpleTypes
        **Percentage** (i.e., number in the range ``[0.0, 100.0]``) of the
        total cell population to randomly match.
    '''

    # ..................{ INITIALIZERS                      }..................
    @type_check
    def __init__(self, cells_percent: NumericSimpleTypes) -> None:
        '''
        Initialize this tissue picker.

        Parameters
        ----------
        cells_percent : NumericSimpleTypes
            **Percentage** (i.e., number in the range ``[0.0, 100.0]``) of the
            total cell population to randomly match.
        '''

        # If this is not a valid percentage, raise an exception. This is
        # important enough to always test rather than defer to assertions.
        if not 0.0 <= cells_percent <= 100.0:
            raise BetseSimConfException(
                'Percentage {} not in range [0, 100].'.format(cells_percent))

        # Classify this parameter.
        self.cells_percent = cells_percent

    # ..................{ PICKERS                           }..................
    @type_check
    def pick_cells(
        self,
        cells: 'betse.science.cells.Cells',
        p:     'betse.science.parameters.Parameters',
    ) -> SequenceTypes:

        # Total number of cells in this cluster.
        data_length = len(cells.cell_i)

        # Total number of cells to randomly select from this cluster.
        data_fraction = int((self.cells_percent/100)*data_length)

        cell_i_copy = cells.cell_i[:]
        np.random.shuffle(cell_i_copy)

        # For simplicity, non-randomly select the indices of the first
        # "data_fraction"-th cells in this cluster. While technically
        # non-random, this simplistic approach currently suffices.
        return [cell_i_copy[x] for x in range(0, data_fraction)]
