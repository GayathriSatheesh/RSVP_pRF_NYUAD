from __future__ import division, print_function
from psychopy import logging, core, visual, gui, event
from psychopy.core import StaticPeriod, CountdownTimer
from psychopy.iohub.client.connect import launchHubServer
from psychopy.info import RunTimeInfo
from datetime import datetime
from inspect import getsourcefile
from os.path import abspath
import pylink
import os.path
import platform
import glob
import numpy as np
import math
import random
import os
import psy_utility as psyut
import time

from pypixxlib.propixx import PROPixxCTRL
from utilities import decimal_to_binary
from pypixxlib._libdpx import DPxUpdateRegCache, DPxGetDinValue, DPxClose, DPxOpen

DPxOpen()


while True:
    DPxUpdateRegCache()

    value = DPxGetDinValue()
    bits = decimal_to_binary(value)

    # print(f"value={value}, bits={bits}")

    if bits[18] == '1':  # right box red, listen_to = 1
        print('red button')

    time.sleep(0.05)  # 50 ms

DPxClose()