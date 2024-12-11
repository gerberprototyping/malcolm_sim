"""Contains IEC_Int class"""

import re


class IEC_Int(int):
    """Extends the int class to support instantiation using IEC formatting"""

    def __init__(self, value) -> None:
        if isinstance(value, str):
            match = re.match(r"^(\d+)\s?([KMGT]?)$", value.strip())
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
            self = int(match.group(1)) * mult
        else:
            self = int(value)
