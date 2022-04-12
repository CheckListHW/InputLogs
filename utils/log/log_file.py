from os import environ


def print_log(message: str):
    file = open(environ['logs_file_path'], 'a')
    file.write(str(message) + '\n')
    file.close()
    print(message)


def read_log() -> str:
    file = open(environ['logs_file_path'], 'r')
    values = file.read()
    file.close()
    return values
