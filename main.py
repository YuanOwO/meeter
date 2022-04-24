import datetime, sys
import logging
import yaml, json
import os
from dotenv import dotenv_values
from flask import Flask

from globalvar import global_vars as gl
from meeter import Meeter, Meet


gl['start_time'] = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

with open('config.yml', 'r', encoding='utf-8') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
    gl['config'] = config


try:
    os.mkdir('logs')
except FileExistsError:
    pass
try:
    os.mkdir('logs\\driver')
except FileExistsError:
    pass

logging.basicConfig(
    filename=os.path.join('logs', gl['start_time']+'.log'),
    filemode='w',
    format='[%(asctime)s %(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    level=logging.INFO)

logging.info('Hello world')


env = dotenv_values('.env')

meeter = Meeter(env['MAIL'], env['PASS'])

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World!'

print(12)