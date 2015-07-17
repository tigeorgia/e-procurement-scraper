import ConfigParser
import os

class ProcurementCredentials(object):
    '''
    classdocs
    '''

    credFileInfo = \
        '''
     The credentials have to be stored in file $HOME/.procurement_creds.
     The format of the file:
     
     [proc]
     localuser=
     localdb=
     localpass=
     remoteuser=
     remotedb=
     remotepass=     
     remoteuser=
     remotepass=
     remotehost=

     '''


    def __init__(self):
        '''
        Constructor
        '''

        self.creds_filename = '%s/.procurement_creds' % os.getenv('HOME')

        self.local_user = None
        self.local_db = None
        self.local_db_pass = None

        self.remote_db_user = None
        self.remote_db = None
        self.remote_db_pass = None

        self.remote_user = None
        self.remote_pass = None
        self.remote_host = None

        self.remote_app_dir = '$HOME/www/tendermonitor'
        self.db_file = 'dump.sql'
	self.db_file_online = 'dump_online.sql'
        self.db_zip = 'dump.sql.tar.gz'
	self.db_zip_online = 'dump_online.sql.tar.gz'

    # the credentials will be loaded from home folder from .cmrcreds file ($HOME/.cmrcreds)
    def load_info(self):
        config = ConfigParser.RawConfigParser(allow_no_value=False)

        if not os.path.isfile(self.creds_filename):
            print self.credFileInfo
            raise Exception

        config.read(self.creds_filename)
        self.local_user = config.get('proc', 'localuser')
        self.local_db = config.get('proc', 'localdb')
        self.local_db_pass = config.get('proc', 'localpass')

        self.remote_db_user = config.get('proc', 'remotedbuser')
        self.remote_db = config.get('proc', 'remotedb')
        self.remote_db_pass = config.get('proc', 'remotedbpass')

        self.remote_user = config.get('proc', 'remoteuser')
        self.remote_pass = config.get('proc', 'remotepass')
        self.remote_host = config.get('proc', 'remotehost')

        return {'local_user': self.local_user,
                'local_db': self.local_db,
                'local_db_pass': self.local_db_pass,
                'remote_db_user': self.remote_db_user,
                'remote_db': self.remote_db,
                'remote_db_pass': self.remote_db_pass,
                'remote_user': self.remote_user,
                'remote_password': self.remote_pass,
                'remote_host': self.remote_host,
		'remote_app_dir': self.remote_app_dir,
		'db_file': self.db_file,
		'db_file_online': self.db_file_online,
		'db_zip': self.db_zip,
		'db_zip_online': self.db_zip_online}


if __name__ == '__main__':
    creds = ProcurementCredentials()
    info = creds.load_info()
    print info


