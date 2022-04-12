from os import remove, scandir


def clear_logs(logs_dir: str):
    for p in list(scandir(logs_dir)):
        file = open(p, 'r')
        values = file.read()
        file.close()
        if len(values) < 1:
            remove(p)
