import os

from mvc.Model.map import Map

os.environ['project'] = os.getcwd()

if __name__ == '__main__':
    print('start')
    data_map = Map()
    data_map.load_map('base.json')
    data_map.attach_logs.values()
    data_map.export()
    print('finish_main')
