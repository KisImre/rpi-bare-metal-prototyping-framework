# Copyright (c) 2020, Kis Imre. All rights reserved.
# SPDX-License-Identifier: MIT

"""
This module defines the interface which is used by the Protocol module for
accessing the target.
"""

import abc

class Connection:
    """ Connection interface for accessing the target. """

    class ConnectionException(Exception):
        """ Exception type for the Connection child classes. """

    def __init__(self):
        pass

    @abc.abstractmethod
    def send(self, data):
        """ Sends data to the target. """

    @abc.abstractmethod
    def recv(self, length):
        """ Receives data from the target for the given length. """
