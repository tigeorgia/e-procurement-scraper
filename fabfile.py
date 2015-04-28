from fabric.api import run, env
from DBImportExport import DBImportExport

def update_db():
    jobs = DBImportExport()
    jobs.dumpdb()
    jobs.compressdb()
    jobs.uploaddb()
    jobs.importdb()
    jobs.cleanup()
    jobs.postProcess()

def import_online_db():
    jobs = DBImportExport()
    jobs.dump_procurement_db()
    jobs.compress_online_db()
    jobs.download_online_db()
    jobs.import_db_scraper()
    jobs.cleanup_online_archive()

def post_scrape_process():
    jobs = DBImportExport()
    jobs.postProcess()

def pre_scrape_process():
    jobs = DBImportExport()
    jobs.storePreScrapeSearchResults()

def generate_files():
    jobs = DBImportExport()
    jobs.generateFiles()
