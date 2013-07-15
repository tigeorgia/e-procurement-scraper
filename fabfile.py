from fabric.api import run, env
from db_import import *
env.hosts=['tigeorgia@95.211.171.65']
env.passwords = {'tigeorgia@95.211.171.65': 'e2049ea4'}

def update_db():
    dumpdb()
    compressdb()
    uploaddb()
    importdb()
    cleanup()
    processemailalerts()

def process_mail():
    processemailalerts()
