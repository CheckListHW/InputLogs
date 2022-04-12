from typing import Any


def is_number(val: Any) -> bool:
    try:
        float(val)
        return True
    except:
        return False