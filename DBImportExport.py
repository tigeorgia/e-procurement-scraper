#!/usr/bin/python
# -*- coding: utf-8 -*-
from ProcurementCredentials import ProcurementCredentials
from fabric.api import local, cd, run, env, shell_env
from fabric.operations import put, get
import os

class DBImportExport(object):

    def __init__(self):
        '''
        Constructor
        '''
	proc_creds = ProcurementCredentials()
	self.info = proc_creds.load_info()
	
	host = '{0}@{1}'.format(self.info['remote_user'],self.info['remote_host'])
	password = self.info['remote_password']

	env.host_string=host
	env.passwords={host: password}


    def dump_procurement_db(self):
	print 'dump online procurement db.'

	run('mysqldump -u {user} -p{dbpass} {db} --add-drop-table > {dbfile}'.format(user=self.info['remote_db_user'], db=self.info['remote_db'], dbpass=self.info['remote_db_pass'], dbfile=self.info['db_file_online']))


    # compress online db
    def compress_online_db(self):
	print 'compresses online procurement db.'
	run('tar czf {archivefile}.tar.gz {sqlfile}'.format(archivefile=self.info['db_file_online'],sqlfile=self.info['db_file_online']))


    # download to scraper server
    def download_online_db(self):
	print 'download online procurement db, uncompresses it, then deletes the local compressed file.'
	get(self.db_zip_online, self.db_zip_online)
	local('tar xzf {tarfile}'.format(tarfile=self.info['db_zip_online']))
	local('rm {tarfile}'.format(tarfile=self.info['db_zip_online']))


    # import full db to scraper db
    def import_db_scraper(self):
	print 'import downloaded procurement db into scraper db, then delete it.'
	local('mysql -u {user} -p{dbpass} -D {db} < {dbfile}'.format(user=self.info['local_db_user'],db=self.info['local_db'], dbpass=self.info['local_db_pass'], dbfile=self.info['db_file_online']))
	local('rm {sqlfile}'.format(sqlfile=self.info['db_file_online']))


    def cleanup_online_archive(self):
	print 'Deletes online files'
	run('rm {sqlfile} {tarfile}.tar.gz'.format(sqlfile=self.info['db_file_online'],tarfile=self.info['db_file_online']))


    # Dump the database
    def dumpdb(self):
	print 'Dump local procurement db.'

	local('mysqldump -u {user} -p{dbpass} {db} --add-drop-table > {dbfile}'.format(user=self.info['local_db_user'],db=self.info['local_db'], dbpass=self.info['local_db_pass'], dbfile=self.info['db_file']))


    def compressdb(self):
	print 'Compresses the dumped db using tar.'
	local('tar czf {tarfile}.tar.gz {sqlfile}'.format(tarfile=self.info['db_file'],sqlfile=self.info['db_file']))


    def uploaddb(self):
	print 'Uploads the compressed db file, uncompresses it remotely, and deletes the remote compressed file.'
	put(db_zip, db_zip)
	run('tar xzf {tarfile}'.format(tarfile=self.info['db_zip']))
	run('rm {tarfile}'.format(tarfile=self.info['db_zip']))


    def importdb(self):
	print 'Remotely imports the db file, then deletes it.'
	run('ionice -c2 -n6 mysql -u {user} -p{dbpass} -D {db} < {dbfile}'.format(user=self.info['remote_db_user'],db=self.info['remote_db'], dbpass=self.info['remote_db_pass'], dbfile=self.info['db_file']))
	run('rm {tarfile}'.format(tarfile=self.info['db_file']))


    def storePreScrapeSearchResults(self):
	with cd(self.info['remote_app_dir'] + '/current'):
	    with shell_env(PATH=self.info['remote_app_dir'] + '/bin:$PATH',GEM_HOME=self.info['remote_app_dir'] + '/gems',RUBYLIB=self.info['remote_app_dir'] + '/lib'):
		run('rake procurement:pre_store_search_results')


    def postProcess(self):
	print 'Generates e-mail alerts and creates the CSV file'
	with cd(self.info['remote_app_dir'] + '/current'):
	    with shell_env(PATH=self.info['remote_app_dir'] + '/bin:$PATH',GEM_HOME=self.info['remote_app_dir'] + '/gems',RUBYLIB=self.info['remote_app_dir'] + '/lib'):
		run('rake procurement:generate_alerts')
		run('rake procurement:generate_tender_bulk_data')
		run('zip ./public/AllTenders AllTenders.csv')


    def cleanup(self):
	print 'Cleans up the local dump file and tar file'
	local('rm {sqlfile} {tarfile}.tar.gz'.format(sqlfile=self.info['db_file'],tarfile=self.info['db_file']))


