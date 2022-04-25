import datetime, logging, os
import yaml

from global_var import global_vars as gl
from meeter import Meeter

gl['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

if 'logs' not in os.listdir():
    os.mkdir('logs')
if 'driver' not in os.listdir('logs'):
    os.mkdir('logs\\driver')

with open('config.yml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    gl['config'] = config

logging.basicConfig(
    filename=os.path.join('logs', gl['start_time']+'.log'),
    filemode='w',
    format='[%(asctime)s %(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO,
    encoding='utf-8')

logging.info('Hello world')

meeter = Meeter(**config['account'])