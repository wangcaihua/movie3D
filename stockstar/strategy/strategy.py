#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
from abc import ABCMeta, abstractmethod

from stockstar.portfolio import Portfolio

__all__ = ["Strategy"]

logger = logging.getLogger(__name__)


class Strategy(object):
    __metaclass__ = ABCMeta

    def __init__(self, portfolio: Portfolio):
        self.bars = portfolio.bars
        self.events = portfolio.events
        self.portfolio = portfolio

    @abstractmethod
    def send_signals(self, event):
        raise NotImplementedError("Should implement send_signals()")

    @abstractmethod
    def place_order(self, event):
        raise NotImplementedError("Should implement place_order()")
