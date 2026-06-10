from __future__ import print_function

from collections import defaultdict

from pypixxlib._libdpx import (
    DPxOpen,
    DPxClose,
    DPxWriteRegCache,
    DPxUpdateRegCache,
    DPxGetTime,
    DPxStopDinLog,
    DPxGetDinValue,
)


trigger_channels_dictionary = {
    224: 4,
    225: 16,
    226: 64,
    227: 256,
    228: 1024,
    229: 4096,
    230: 16384,
    231: 65536
}


black = [0, 0, 0]


def RGB2Trigger(color):
    """
    Determines expected trigger from a given RGB 255 colour value.
    """
    return int((color[2] << 16) + (color[1] << 8) + color[0])


def decimal_to_binary(decimal_number):
    """
    Converts a non-negative decimal number to its binary representation.
    """
    if decimal_number < 0:
        raise ValueError("The number should be non-negative.")
    return bin(decimal_number)[2:]


button_mapping = {
    "right box": {
        "white": {"response": 6, "listen_to": 5},
        "red": {"response": 10, "listen_to": 1},
        "yellow": {"response": 9, "listen_to": 2},
        "green": {"response": 8, "listen_to": 3},
        "blue": {"response": 7, "listen_to": 4},
    },
    "left box": {
        "white": {"response": 1, "listen_to": 10},
        "red": {"response": 5, "listen_to": 6},
        "yellow": {"response": 4, "listen_to": 7},
        "green": {"response": 3, "listen_to": 8},
        "blue": {"response": 2, "listen_to": 9},
    }
}


_PAIR_TO_LISTEN = {}
for box, colors in button_mapping.items():
    for color, info in colors.items():
        _PAIR_TO_LISTEN[(box, color)] = info["listen_to"]


_RESP_TO_PAIRS_TEMP = defaultdict(list)
for box, colors in button_mapping.items():
    for color, info in colors.items():
        _RESP_TO_PAIRS_TEMP[info["response"]].append((box, color))

_RESP_TO_PAIRS = dict(_RESP_TO_PAIRS_TEMP)


_ALL_RESPONSE_CODES = sorted(_RESP_TO_PAIRS.keys())
_ALL_LISTEN_CODES = sorted(set(_PAIR_TO_LISTEN[p] for p in _PAIR_TO_LISTEN))

_VPIXX_REGISTER_SIZE = 24
_BUTTON_BITS_TO_READ = 10


def _norm_box(s):
    """
    Normalize and validate a box name.
    """
    s = s.strip().lower()
    if s not in button_mapping:
        raise ValueError("Unknown box: {!r}. Use 'right box' or 'left box'.".format(s))
    return s


def _norm_color(box, c):
    """
    Normalize and validate a color for a given box.
    """
    c = c.strip().lower()
    if c not in button_mapping[box]:
        raise ValueError("Unknown color for {}: {!r}.".format(box, c))
    return c


def _normalize_selection(selection):
    """
    Normalize grouped selection into a list of (box, color) pairs.

    selection example:
        {
            "right box": ["green", "blue"],
            "left box": ["white", "red"]
        }

    If selection is None, listens to all defined buttons.
    """
    if selection is None:
        listen_pairs = list(_PAIR_TO_LISTEN.keys())
    else:
        listen_pairs = []
        for raw_box, colors in selection.items():
            box = _norm_box(raw_box)

            if not colors:
                continue

            for c in colors:
                color = _norm_color(box, c)
                listen_pairs.append((box, color))

    # Deduplicate while preserving order.
    seen = set()
    deduped = []
    for pair in listen_pairs:
        if pair not in seen:
            deduped.append(pair)
            seen.add(pair)

    return deduped


def _read_button_bits():
    """
    Reads VPixx digital input and returns the last 10 bits as integers.

    Index 0 corresponds to response code 1.
    Index 1 corresponds to response code 2.
    ...
    Index 9 corresponds to response code 10.
    """
    DPxUpdateRegCache()
    raw = DPxGetDinValue()

    bits = decimal_to_binary(raw)

    # Make sure indexing the last 10 bits is always safe.
    bits = bits.zfill(_VPIXX_REGISTER_SIZE)

    button_box = [int(bit) for bit in bits[-_BUTTON_BITS_TO_READ:]]

    return button_box


def getbuttonColor(selection=None, blocking=True):
    """
    Polls hardware inputs and returns the semantic pressed button.

    Returns:
        (box, color)

    Example:
        ("right box", "green")
    """
    listen_pairs = _normalize_selection(selection)

    while True:
        button_box = _read_button_bits()

        resp_codes = [
            i + 1
            for i, state in enumerate(button_box)
            if state == 1 and (i + 1) in _ALL_RESPONSE_CODES
        ]

        if len(resp_codes) == 1:
            resp = resp_codes[0]
            candidates = _RESP_TO_PAIRS.get(resp, [])

            if selection is not None:
                candidates = [p for p in candidates if p in listen_pairs]

            if len(candidates) == 1:
                return candidates[0]

            elif len(candidates) > 1:
                print(
                    "Ambiguous press: multiple (box,color) share this hardware line: "
                    + ", ".join("{}/{}".format(b, c) for b, c in candidates)
                )

        if not blocking:
            return None


def getbutton(buttons=None):
    """
    Polls hardware inputs and returns the numeric response code.

    If buttons is None, listens to all defined response codes.
    If buttons is a list, listens only to those response codes.
    """
    while True:
        button_box = _read_button_bits()

        resp = [
            i + 1
            for i, state in enumerate(button_box)
            if state == 1
        ]

        if len(resp) == 1:
            response_code = resp[0]

            if buttons is None:
                if response_code in _ALL_RESPONSE_CODES:
                    return response_code
            else:
                if response_code in buttons:
                    return response_code


def listenbutton(keycode):
    """
    Blocks until the requested keycode is detected.

    Example:
        listenbutton(5)
    """
    while True:
        button_box = _read_button_bits()

        resp = [
            i + 1
            for i, state in enumerate(button_box)
            if state == 1
        ]

        if len(resp) == 1 and resp[0] == keycode:
            return resp[0]