import random

import numpy as np


def get_random_logs(names: [str]) -> [str]:
    names_struct = {}
    for name in names:
        main_name = name[:name.index('.')] if name.__contains__('.') else name
        names_struct[main_name] = [] if names_struct.get(main_name) is None else names_struct[main_name]
        names_struct[main_name].append(name)

    return [random.choice(sub_names) for sub_names in names_struct.values()]


if __name__ == '__main__':
    names = ['x', 'y', 'z', 'z.1', 'z.3', 'x.1']
    print(get_random_logs(names))
