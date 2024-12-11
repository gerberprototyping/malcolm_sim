"""Contains IEC_Int class"""

import re


class IEC_Int(int): # pylint: disable=invalid-name
    """Extends the int class to support instantiation using IEC formatting"""

    def __new__(cls, value) -> int:
        if isinstance(value, str):
            match = re.match(r"^(\d+)\s?([KMGT]?)$", value.strip().upper())
            if not match:
                raise ValueError("Invalid string format for IEC int")
            x = match.group(2)
            if "K" == x:
                mult = 1024
            elif "M" == x:
                mult = 1024 * 1024
            elif "G" == x:
                mult = 1024 * 1024 * 1024
            elif "T" == x:
                mult = 1024 * 1024 * 1024 * 1024
            else:
                mult = 1
            return int.__new__(cls, int(match.group(1)) * mult)
        else:
            return int.__new__(cls, int(value))
