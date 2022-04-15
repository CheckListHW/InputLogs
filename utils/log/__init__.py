import os
from datetime import datetime

from utils.log.clear_logs import clear_logs

if not os.environ.get('project'):
    os.environ['project'] = os.getcwd()

if not os.path.exists(os.environ['project'] + '/logs'):
    os.mkdir(os.environ['project'] + '/logs')

logs_dir = os.environ['project'] + '/logs'

clear_logs(logs_dir)
file_name = str(datetime.now()).replace(" ", "_").replace(":", "-")[:-7]
os.environ['logs_file_path'] = f'{logs_dir}/{file_name}.txt'

f = open(os.environ['logs_file_path'], 'x')
f.write('')
f.close()
