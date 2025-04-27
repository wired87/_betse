#!/usr/bin/env python3
# --------------------( LICENSE                            )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Matplotlib-specific **colormap** (i.e., objects mapping from low-level
scientific data values to high-level RGBA colour values displaying that data)
facilities.

See Also
----------
https://matplotlib.org/examples/color/colormaps_reference.html
    Canonical colormap example visually depicting all default colormaps bundled
    with matplotlib.
'''

# ....................{ IMPORTS                            }....................
import numpy as np
from betse.exceptions import BetseSequenceException
from betse.util.io.log import logs
from betse.util.type.iterable import sequences
from betse.util.type.numeric import ints
from betse.util.type.types import type_check, SequenceTypes
from matplotlib import colormaps
from matplotlib.colors import (
    Colormap,
    LinearSegmentedColormap,
)

# ....................{ GETTERS                            }....................
@type_check
def get_colormap(name: str) -> Colormap:
    '''
    Matplotlib colormap with the passed name, including both standard colormaps
    bundled with matplotlib *and* application-specific colormaps registered by
    this submodule.

    This function is a convenience wrapper for the
    :meth:`matplotlib.colormaps.__getindex__` dunder method, provided only as a
    human-readable utility to assist readability and maintainability.

    Parameters
    ----------
    name : str
        Name of the colormap to be retrieved. If this is:

        * A standard colormap bundled with matplotlib, this should be the name
          of the attribute in the :mod:`matplotlib.cm` module corresponding to
          the desired colormap (e.g., ``Blues``, ``jet``, ``rainbow``).
        * An application-specific colormap registered by this submodule, this
          should be the ``name`` parameter initializing an
          :class:`_MplColormapScheme` instance contained in the
          ``COLORMAP_SCHEMES`` tuple defined within the :func:`init` function.

    Returns
    ----------
    Colormap
        Matplotlib colormap with this name.

    See Also
    ----------
    http://matplotlib.org/examples/color/colormaps_reference.html
        List of supported colormaps.
    '''

    return colormaps[name]

# ....................{ ITERATORS                          }....................
def iter_colormap_names() -> SequenceTypes:
    '''
    Sequence of the names of all colormaps currently registered with matplotlib
    (in sorted lexicographic order).

    Caveats
    -----------
    **This function should be called only after this submodule has been
    initialized** (i.e., after the :func:`init` function has been called).
    While this function *is* safely callable beforehand, doing so prevents this
    function from returning the names of all application-specific colormaps
    registered by that function.

    **This function does not memoize this sequence** (e.g., by decorating this
    function with :func:`betse.util.type.decorator.decmemo.func_cached`). This
    sequence may change over the lifetime of this application and hence
    *cannot* be implicitly cached on the first call to this function. Instead,
    callers may prefer to manually cache this sequence for efficiency.
    '''

    # In theory, this implementation would simply defer to the existing
    # matplotlib.pyplot.colormaps() function returning the exact same sequence.
    # In practice, doing so is infeasible in the general case. Why? Because
    # merely importing the "matplotlib.pyplot" submodule incurs non-trivial,
    # non-deterministic, and irreversible side effects -- notably, the
    # selection of a default backend.
    #
    # Inevitably, some external caller will call this function *BEFORE*
    # selecting a default backend, implying that this function *CANNOT* import
    # from the "matplotlib.pyplot" submodule. Instead, this function inlines the
    # body of the matplotlib.pyplot.colormaps() function here. Fortunately, the
    # body of this function reduces to a trivial one-liner.
    return sorted(colormaps)

# ....................{ INITIALIZERS                       }....................
def init() -> None:
    '''
    Initialize this module by registering all application-specific colormaps
    with matplotlib, enabling these colormaps to be trivially retrieved with
    the standard :func:`matplotlib.cm.get_cmap` function.

    This function is intended to be called at matplotlib initialization time.
    '''

    # Enable these globals to be locally assigned to below.
    global _is_initted

    # ..................{ INITTED                            }..................
    # If this submodule has already been initialized, reduce to a noop.
    if _is_initted:
        logs.log_debug(
            'Ignoring attempt to reregister custom matplotlib colormaps...')
        return
    # Else, this submodule has *NOT* yet been initialized.

    # Note this submodule has now been initialized.
    _is_initted = True

    # Log this initialization attempt.
    logs.log_debug('Registering custom matplotlib colormaps...')

    # ..................{ COLOURS                            }..................
    # Primary colours.
    BLACK = (  0,   0,   0)
    GREEN = (  0, 255,   0)
    RED   = (255,   0,   0)
    BLUE  = (  0,   0, 255)

    # Secondary colours.
    CYAN    = (  9, 232, 239)
    MAGENTA = (239,  52, 236)
    # ORANGE  = (255, 164,  61)

    GREY_DARK = (51, 51, 51)

    GREEN_LIGHT  = (184, 255, 104)
    PURPLE_LIGHT = (219, 104, 255)

    BLUE_PALE = ( 56, 132, 255)
    RED_PALE  = (244,  66,  66)

    AQUA =  (53, 255, 211)
    AQUA2 = (71, 255, 218)

    GOLD   = (255, 231,  55)
    YELLOW = (255, 246, 130)

    # Salmon orange and/or red.
    SALMON  = (255, 111, 54)
    SALMON2 = (255, 117, 71)

    # ..................{ COLORMAPS                          }..................
    # Tuple of all application-specific colormaps iteratively registered below.
    COLORMAP_SCHEMES = (
        # Black-based colormaps.
        _MplColormapScheme(name='betse_electric_cyan',    colors=(BLACK, CYAN)),
        _MplColormapScheme(name='betse_electric_gold',    colors=(BLACK, YELLOW)),
        _MplColormapScheme(name='betse_electric_green',   colors=(BLACK, GREEN)),
        _MplColormapScheme(name='betse_electric_magenta', colors=(BLACK, MAGENTA)),
        _MplColormapScheme(name='betse_electric_orange',  colors=(BLACK, SALMON2)),
        _MplColormapScheme(name='betse_electric_blue',    colors=(BLACK, BLUE_PALE)),

        # Grey-based colormaps.
        _MplColormapScheme(name='betse_blue_chalkboard',    colors=(GREY_DARK, BLUE_PALE)),
        _MplColormapScheme(name='betse_cyan_chalkboard',    colors=(GREY_DARK, CYAN)),
        _MplColormapScheme(name='betse_gold_chalkboard',    colors=(GREY_DARK, GOLD)),
        _MplColormapScheme(name='betse_green_chalkboard',   colors=(GREY_DARK, GREEN)),
        _MplColormapScheme(name='betse_magenta_chalkboard', colors=(GREY_DARK, MAGENTA)),
        _MplColormapScheme(name='betse_orange_chalkboard',  colors=(GREY_DARK, SALMON)),

        # Salmon-based colormaps.
        _MplColormapScheme(name='betse_alien_chalkboard', colors=(SALMON2, GREY_DARK, AQUA2)),
        _MplColormapScheme(name='betse_alien_pale',       colors=(SALMON2, BLACK, AQUA2)),
        _MplColormapScheme(name='betse_alien_solid',      colors=(SALMON, BLACK, AQUA)),

        # Purple-based colormaps.
        _MplColormapScheme(name='betse_purple_green_chalkboard', colors=(MAGENTA, GREY_DARK, GREEN)),
        _MplColormapScheme(name='betse_purple_green_pale',       colors=(PURPLE_LIGHT, BLACK, GREEN_LIGHT)),
        _MplColormapScheme(name='betse_purple_green_solid',      colors=(MAGENTA, BLACK, GREEN)),

        # Blue-based colormaps.
        _MplColormapScheme(name='betse_red_blue_chalkboard', colors=(BLUE, GREY_DARK, RED)),
        _MplColormapScheme(name='betse_red_blue_pale',       colors=(BLUE_PALE, BLACK, RED_PALE)),
        _MplColormapScheme(name='betse_red_blue_solid',      colors=(BLUE, BLACK, RED)),
    )

    # ..................{ REGISTRATION                       }..................
    # Register each such colormap with matplotlib.
    for colormap_scheme in COLORMAP_SCHEMES:
        colormap_scheme.register()

# ....................{ PRIVATE ~ globals                  }....................
_is_initted = False
'''
``True`` only if the :func:`init` function has already been called under the
active Python interpreter.
'''

# ....................{ PRIVATE ~ classes                  }....................
class _MplColormapScheme(object):
    '''
    Matplotlib-specific **colormap scheme** (i.e., collection of parameters
    sufficient to subsequently define a standard linear-segmented colormap).

    Instances of this class are typically passed to the :func:`add_colormap`
    function, which both creates and registers a new colormap from the passed
    colormap scheme.

    Attributes
    -----------
    colormap_name : str
        Name of the colormap to be created.
    colors : SequenceTypes
        Two-dimensional sequence whose:

        * First dimension indexes each color defining this colormap's gradient.
          This dimension *must* be a sequence containing two or more colors.
        * Second dimension is a 3-sequence indexing the red, green, and blue
          (RGB) values defining this color.
    gamma : float
        Gamma curve value, adjusting the brightness of this colormap's
        **endpoint colors** (i.e., the colors at the bottom and top of this
        colormap). Specifically, matplotlib documentation internally states:

            colormap values are modified as c^gamma, where gamma is (1-beta)
            for beta>0 and 1/(1+beta) for beta<=0
    '''

    # ..................{ INITIALIZERS                      }..................
    def __init__(
        self,

        # Mandatory parameters.
        name: str,
        colors: SequenceTypes,

        # Optional parameters. All default values defined below should ideally
        # be identical to the same default values defined by matplotlib.
        gamma: float = 1.0,
    ) -> None:
        '''
        Initialize this colormap scheme.

        Parameters
        -----------
        name : str
            Name of the colormap to be created.
        colors : SequenceTypes
            Two-dimensional sequence whose:
            * First dimension indexes each color defining this colormap's
              gradient. This dimension *must* be a sequence containing two or
              more colors.
            * Second dimension is a 3-sequence indexing the red, green, and blue
              (RGB) values defining this color.
        gamma : float
            Gamma curve value, adjusting the brightness of this colormap's
            **endpoint colors** (i.e., the colors at the bottom and top of this
            colormap). Specifically, matplotlib documentation internally states:

                colormap values are modified as c^gamma, where gamma is (1-beta)
                for beta>0 and 1/(1+beta) for beta<=0

        Raises
        -----------
        BetseSequenceException
            If either:

            * The first dimension of ``colors`` contains less than two colors
              (i.e., is either empty *or* contains only one color).
            * Any second dimension of ``colors`` does *not* contain exactly
              three color values.
        BetseIntException
            If any color value in any second dimension of ``colors`` is *not*
            a valid color value in the range ``[0, 255]``.
        '''

        #FIXME: Raise an exception if this colormap name conflicts with that
        #of an existing colormap -- probably by defining a new
        #die_if_colormap() utility function in this submodule.

        # If this colormap defines less than two colors, raise an exception.
        if len(colors) < 2:
            #FIXME: Raise a less ambiguous "BetseMplColormapException" instead.
            raise BetseSequenceException(
                'Colormap scheme defines less than two colors: {!r}'.format(
                    colors))

        # For each color defining this colormap...
        for color in colors:
            # If this color is *NOT* a 3-sequence, raise an exception.
            sequences.die_unless_length(sequence=color, length=3)

            # If any of this color's values is *NOT* a valid RGB colour (i.e.,
            # integer in the range [0, 255]), raise an exception.
            ints.die_unless_byte(*color)

        # Classify all passed parameters.
        self._name = name
        self._colors = colors
        self._gamma = gamma

    # ..................{ REGISTERERS                        }..................
    @type_check
    def register(self) -> Colormap:
        '''
        Create a linear-segmented colormap from the current scheme, register
        this colormap with matplotlib, and return this colormap.
        '''

        # Log this registration attempt.
        # logs.log_debug(
        #     'Registering colormap "%s": %s',
        #     self.colormap_name, self.colors_normalized)

        # Two-dimensional Numpy array, normalizing each of each color's values
        # from [0, 255] to [0.0, 1.0] (while preserving the order of colors).
        colors_normalized = np.array(self._colors) / 255

        # Colormap synthesized from this colormap name and colors.
        #
        # Unfortunately, as the names of the first two parameters accepted by
        # this function have changed across matplotlib versions, these
        # parameters *MUST* be passed positionally for safety.
        colormap = LinearSegmentedColormap.from_list(
            self._name, colors_normalized, N=256, gamma=self._gamma)

        # Register this colormap with matplotlib.
        colormaps.register(colormap)

        # Return this colormap.
        return colormap

