import numpy as np
from matplotlib import pyplot as plt
import pandas as pd


def mass_from_xlsx(path: str) -> dict:
    logs = {}
    xl = pd.ExcelFile(path)
    df = xl.parse(xl.sheet_names[0])
    for name in df.keys():
        logs[name] = list(df[name].values)
    return logs


if __name__ == '__main__':
    # mass_from_xlsx('C:/Users/KosachevIV/PycharmProjects/InputLogs/data_files/test.xlsx')
    a = [1, 2, 3, 4, 5]
    b = []
    for latter in 'abcdef':
        b.append([])
        for i in range(5):
            b[-1].append(' '+latter+str(i))
    print(b)
    for x, y in [(x1, y1) for x1 in a for y1 in b[x1]]:
        print(x, y)
