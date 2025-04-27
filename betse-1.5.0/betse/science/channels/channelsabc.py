#!/usr/bin/env python3
# Copyright 2014-2025 by Alexis Pietak & Cecil Curry.
# See "LICENSE" for further details.

'''
Abstract base classes of all channel classes.
'''

# ....................{ IMPORTS                            }....................
from abc import ABCMeta, abstractmethod
import numpy as np
from betse.science import sim_toolbox as stb
from betse.science.math import toolbox as tb

# ....................{ BASE                               }....................
class ChannelsABC(object, metaclass=ABCMeta):
    '''
    Abstract base class of all channel classes.

    Attributes
    ----------
    '''
    @abstractmethod
    def init(self, vm, cells, p, targets = None):
        '''
        Runs the initialization sequence for a voltage gated ion channel.
        '''

        pass



    @abstractmethod
    def run(self, vm, p):
        '''
        Runs the voltage gated ion channel.
        '''
        pass

    def update_mh(self, p, time_unit = 1e3):
        """
        Updates the 'm' and 'h' gating functions of the channel model for
        standard Hodgkin-Huxley formalism channel models.

        """

        # Update channel state using RK4:------------------------------------
        # dm = tb.RK4(lambda m: (self._mInf - self.m) / (self._mTau))
        # dh = tb.RK4(lambda h: (self._hInf - self.h) / (self._hTau))
        #
        # self.m += dm(self.m, p.dt)
        # self.h += dh(self.h, p.dt)

        # Update channel state using semi-Implicit Euler method:-------------------
        dt = p.dt*self.time_unit

        self.m = (self._mTau*self.m + dt*self._mInf)/(self._mTau + dt)
        self.h = (self._hTau*self.h + dt*self._hInf)/(self._hTau + dt)

    def update_ml(self, p, time_unit = 1e3):
        """
        An iterative time-step updating method for the
        time-dependent Morris-Lecar formalism of voltage-gated
        ion channels (a variant of Hodgkin-Huxley)
        :param p: Parameters
        :param time_unit:
        :return:
        """

        dt = p.dt * self.time_unit
        self.m = (self.m + (dt * self.Phi * self._mInf / self._mTau)) / (1 + ((dt * self.Phi) / self._mTau))
