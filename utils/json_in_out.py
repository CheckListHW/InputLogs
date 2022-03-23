from typing import Any

from numpy import int64


def recursive_extraction(obj: [Any]) -> Any:
    if type(obj) in [str]:
        return obj
    elif type(obj) is dict:
        d = {}
        for val, key in zip(obj.values(), obj.keys()):
            d[key] = recursive_extraction(val)
        return d
    try:
        obj_list = iter(obj)
        return [recursive_extraction(i) for i in obj_list]
    except TypeError:
        if hasattr(obj, 'get_as_dict'):
            return obj.get_as_dict()
        else:
            if type(obj) in [float]:
                return round(obj, 5)
            if type(obj) in [int64]:
                return int(obj)
            return obj


class JsonInOut:
    def get_as_dict(self) -> dict:
        my_dict = {}
        this_class = self.__class__
        for slot in this_class.__slots__:
            if hasattr(self, slot):
                my_dict[slot] = recursive_extraction(getattr(self, slot))
        return my_dict

    def load_from_dict(self, load_dict: dict):
        for name_property in load_dict:
            if hasattr(self, name_property):

                if hasattr(getattr(self, name_property), 'load_from_dict'):
                    getattr(self, name_property).load_from_dict(load_dict[name_property])
                else:
                    self.__setattr__(name_property, load_dict[name_property])
