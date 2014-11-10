#!/usr/bin/python
# -*- coding: utf-8 -*-
from ProcurementCredentials import ProcurementCredentials
import os

class DBImportExport(object):

    def __init__(self):
        '''
        Constructor
        '''
	proc_creds = ProcurementCredentials()
	self.info = proc_creds.load_info()


    def dump_procurement_db():
	print 'dump online procurement db.'

	run('mysqldump -u {user} -p{dbpass} {db} --add-drop-table > {dbfile}'.format(user=info['remote_user'], db=info['remote_db'], dbpass=info['remote_db_pass'], dbfile=info['db_file_online']))


    # compress online db
    def compress_online_db():
	print 'compresses online procurement db.'
	run('tar czf {archivefile}.tar.gz {sqlfile}'.format(archivefile=info['db_file_online'],sqlfile=info['db_file_online']))


    # download to scraper server
    def download_online_db():
	print 'download online procurement db, uncompresses it, then deletes the local compressed file.'
	get(self.db_zip_online, self.db_zip_online)
	local('tar xzf {tarfile}'.format(tarfile=info['db_zip_online']))
	local('rm {tarfile}'.format(tarfile=info['db_zip_online']))


    # import full db to scraper db
    def import_db_scraper():
	print 'import downloaded procurement db into scraper db, then delete it.'
	local('mysql -u {user} -p{dbpass} -D {db} < {dbfile}'.format(user=info['local_user'],db=info['local_db'], dbpass=info['local_db_pass'], dbfile=info['db_file_online']))
	local('rm {sqlfile}'.format(sqlfile=info['db_file_online']))


    def cleanup_online_archive():
	print 'Deletes online files'
	run('rm {sqlfile} {tarfile}.tar.gz'.format(sqlfile=info['db_file_online'],tarfile=info['db_file_online']))


    # Dump the database
    def dumpdb():
	print 'Dump local procurement db.'

	local('mysqldump -u {user} -p{dbpass} {db} --add-drop-table > {dbfile}'.format(user=info['local_user'],db=info['local_db'], dbpass=info['local_db_pass'], dbfile=info['db_file']))


    def compressdb():
	print 'Compresses the dumped db using tar.'
	local('tar czf {tarfile}.tar.gz {sqlfile}'.format(tarfile=info['db_file'],sqlfile=info['db_file']))


    def uploaddb():
	print 'Uploads the compressed db file, uncompresses it remotely, and deletes the remote compressed file.'
	put(db_zip, db_zip)
	run('tar xzf {tarfile}'.format(tarfile=info['db_zip']))
	run('rm {tarfile}'.format(tarfile=info['db_zip']))


    def importdb():
	print 'Remotely imports the db file, then deletes it.'
	run('ionice -c2 -n6 mysql -u {user} -p{dbpass} -D {db} < {dbfile}'.format(user=info['remote_user'],db=info['remote_db'], dbpass=info['remote_db_pass'], dbfile=info['db_file']))
	run('rm {tarfile}'.format(tarfile=info['db_file']))


    def storePreScrapeSearchResults():
	with cd(info['remote_app_dir'] + '/current'):
	    with shell_env(PATH=info['remote_app_dir'] + '/bin:$PATH',GEM_HOME=info['remote_app_dir'] + '/gems',RUBYLIB=info['remote_app_dir'] + '/lib'):
		run('rake procurement:pre_store_search_results')


    def postProcess():
	print 'Generates e-mail alerts and creates the CSV file'
	with cd(info['remote_app_dir'] + '/current'):
	    with shell_env(PATH=info['remote_app_dir'] + '/bin:$PATH',GEM_HOME=info['remote_app_dir'] + '/gems',RUBYLIB=info['remote_app_dir'] + '/lib'):
		run('rake procurement:generate_alerts')
		run('rake procurement:generate_tender_bulk_data')
		run('zip ./public/AllTenders AllTenders.csv')


    def cleanup():
	print 'Cleans up the local dump file and tar file'
	local('rm {sqlfile} {tarfile}.tar.gz'.format(sqlfile=info['db_file'],tarfile=info['db_file']))


