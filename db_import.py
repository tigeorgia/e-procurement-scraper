from fabric.api import local, cd, run, env
from fabric.operations import put

USER='root'
DB='procurement'
DBFILE = 'dump.sql'
DBZIP = 'dump.sql.tar.gz'
LOCALDBPW = 'root'
REMOTEDBPW = 'root'
TABLES=['--ignore-table='+DB+'.cpv_groups',
        '--ignore-table='+DB+'.cpv_groups_tender_cpv_classifiers',
        '--ignore-table='+DB+'.procurer_watches',
        '--ignore-table='+DB+'.searches',
        '--ignore-table='+DB+'.supplier_watches',
        '--ignore-table='+DB+'.users',
        '--ignore-table='+DB+'.watch_tenders']
# Something along these lines
# Dump the database
def dumpdb():
  print "dump db"

  local('mysqldump -u {user} -p{dbpass} {db} {tables} > {dbfile}'.format(
    user=USER,
    db=DB,
    dbpass=LOCALDBPW,
    tables=' '.join(TABLES),
    dbfile=DBFILE))
def compressdb():
    """ Compresses the dumped db using tar."""
    local("tar czf {}.tar.gz {}".format(DBFILE,DBFILE))

def uploaddb():
    """ Uploads the compressed db file, uncompresses it remotely, and deletes
    the remote compressed file."""
    put(DBZIP,DBZIP)
    run("tar xzf {}".format(DBZIP))
    run("rm {}".format(DBZIP))

def importdb():
    """ Remotely imports the db file, then deletes it."""
    run("ionice -c2 -n6 mysql -u {user} -p{dbpass} -D {db} < {dbfile}".format(user=USER,db=DB,dbpass=REMOTEDBPW,dbfile=DBFILE))
    run("rm {}".format(DBFILE))

def cleanup():
    local("rm {} {}.tar.gz".format(DBFILE,DBFILE))
