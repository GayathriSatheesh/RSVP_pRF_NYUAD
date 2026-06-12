import time
from pypixxlib._libdpx import DPxOpen, DPxClose, DPxWriteRegCache, DPxUpdateRegCache, DPxGetTime, DPxStopDinLog, DPxGetDinValue
from utilities import getbuttonColor

selection1 = {
    "right box": ["green", "blue", "yellow", "red", "white"],
    "left box": ["green", "blue", "yellow", "red", "white"]
}


selection2 = {
"left box": ["green", "blue", "yellow", "red", "white"]
}

selection3 = {
"right box": ["red"]
}


DPxOpen()

while True:


    candidates = getbuttonColor(selection1)


    time.sleep(0.5)  # 500 milliseconds


    print("candidates", candidates)

DPxClose()