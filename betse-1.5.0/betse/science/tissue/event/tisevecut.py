#!/usr/bin/env python3
# --------------------( LICENSE                           )--------------------
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
High-level classes aggregating all parameters pertaining to simulation events.
'''

# ....................{ IMPORTS                           }....................
from betse.science.tissue.event.tiseveabc import SimEventSpikeABC
# from betse.util.io.log import logs
from betse.util.type.types import type_check  #, SequenceTypes

# ....................{ SUBCLASSES                        }....................
#FIXME: Refactor the TissueHandler.removeCells() method into a new
#fire() method of this subclass.
class SimEventCut(SimEventSpikeABC):
    '''
    **Cutting event** (i.e., event removing one or more cells of the current
    cell cluster at some time step during the simulation phase).
    '''

    # ..................{ INITIALIZERS                      }..................
    @type_check
    def __init__(self, p: 'betse.science.parameters.Parameters') -> None:
        '''
        Initialize this cutting event for the passed simulation configuration.

        Attributes
        ----------
        p : betse.science.parameters.Parameters
            Current simulation configuration.
        '''

        # Initialize our superclass.
        super().__init__(p=p, time_step=p.event_cut_time)
