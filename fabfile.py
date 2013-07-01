from fabric.api import run, env
from db_import import *

env.hosts=['tigeorgia@192.168.0.241']

def update_db(password):
    env.password = password
    dumpdb("","")
    compressdb()
    uploaddb()
    importdb("","")
    cleanup()
