#!/usr/bin/env python
#-*- coding:utf-8 -*-
##
## formula.py
##
##  Created on: Dec 7, 2016
##      Author: Alexey S. Ignatiev
##      E-mail: aignatiev@ciencias.ulisboa.pt
##

"""
    ===============
    List of classes
    ===============

    .. autosummary::
        :nosignatures:

        IDPool

    ==================
    Module description
    ==================

    placeholder

    ==============
    Module details
    ==============
"""

#
#==============================================================================
from __future__ import print_function
import collections

#
#==============================================================================
class IDPool(object):
    """
        A simple manager of variable IDs. It can be used as a pool of integers
        assigning an ID to any object. Identifiers are to start from ``1`` by
        default. The list of occupied intervals is empty be default. If
        necessary the top variable ID can be accessed directly using the
        ``top`` variable.

        :param start_from: the smallest ID to assign.
        :param occupied: a list of occupied intervals.

        :type start_from: int
        :type occupied: list(list(int))
    """

    def __init__(self, start_from=1, occupied=[]):
        """
            Constructor.
        """

        self.restart(start_from=start_from, occupied=occupied)

    def restart(self, start_from=1, occupied=[]):
        """
            Restart the manager from scratch. The arguments replicate those of
            the constructor of :class:`IDPool`.
        """

        # initial ID
        self.top = start_from - 1

        # occupied IDs
        self._occupied = sorted(occupied, key=lambda x: x[0])

        # main dictionary storing the mapping from objects to variable IDs
        self.obj2id = collections.defaultdict(lambda: self._next())

        # mapping back from variable IDs to objects
        # (if for whatever reason necessary)
        self.id2obj = {}

    def id(self, obj=None):
        """
            The method is to be used to assign an integer variable ID for a
            given new object. If the object already has an ID, no new ID is
            created and the old one is returned instead.

            An object can be anything. In some cases it is convenient to use
            string variable names. Note that if the object is not provided,
            the method will return a new id unassigned to any object.

            :param obj: an object to assign an ID to.

            :rtype: int.

            Example:

            .. code-block:: python

                >>> from pysat.formula import IDPool
                >>> vpool = IDPool(occupied=[[12, 18], [3, 10]])
                >>>
                >>> # creating 5 unique variables for the following strings
                >>> for i in range(5):
                ...    print(vpool.id('v{0}'.format(i + 1)))
                1
                2
                11
                19
                20

            In some cases, it makes sense to create an external function for
            accessing IDPool, e.g.:

            .. code-block:: python

                >>> # continuing the previous example
                >>> var = lambda i: vpool.id('var{0}'.format(i))
                >>> var(5)
                20
                >>> var('hello_world!')
                21
        """

        if obj is not None:
            vid = self.obj2id[obj]

            if vid not in self.id2obj:
                self.id2obj[vid] = obj
        else:
            # no object is provided => simply return a new ID
            vid = self._next()

        return vid

    def obj(self, vid):
        """
            The method can be used to map back a given variable identifier to
            the original object labeled by the identifier.

            :param vid: variable identifier.
            :type vid: int

            :return: an object corresponding to the given identifier.

            Example:

            .. code-block:: python

                >>> vpool.obj(21)
                'hello_world!'
        """

        if vid in self.id2obj:
            return self.id2obj[vid]

        return None

    def occupy(self, start, stop):
        """
            Mark a given interval as occupied so that the manager could skip
            the values from ``start`` to ``stop`` (**inclusive**).

            :param start: beginning of the interval.
            :param stop: end of the interval.

            :type start: int
            :type stop: int
        """

        if stop >= start:
            self._occupied.append([start, stop])
            self._occupied.sort(key=lambda x: x[0])

    def _next(self):
        """
            Get next variable ID. Skip occupied intervals if any.
        """

        self.top += 1

        while self._occupied and self.top >= self._occupied[0][0]:
            if self.top <= self._occupied[0][1]:
                self.top = self._occupied[0][1] + 1

            self._occupied.pop(0)

        return self.top
