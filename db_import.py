from fabric.api import local, cd, run, env
from fabric.operations import put

USER='root'
DB='procurement'
TABLES=['cpv_groups',
        'cpv_groups_tender_cpv_classifiers',
        'procurer_watches',
        'searches',
        'supplier_watches',
        'users',
        'watch_tenders',]
# Something along these lines
# Dump the database
def dump_tables
  local('mysqldump --add-drop-table -u {user} -p {db} {tables} > dump.sql'.format(
    user=USER,
    db=DB,
    tables=' '.join(TABLES))

def compressdb(dbfile="dump.sql"):
    """ Compresses the dumped db using tar."""
    local("tar czf {}.tar.gz {}".format(dbfile,dbfile))

def uploaddb(dbfile="dump.sql.tar.gz"):
    """ Uploads the compressed db file, uncompresses it remotely, and deletes
    the remote compressed file."""
    put(dbfile,dbfile)
    run("tar xzf {}".format(dbfile))
    run("rm {}".format(dbfile))

def importdb(user,db,dbfile="dump.sql"):
    """ Remotely imports the db file, then deletes it."""
    run("ionice -c2 -n6 mysql -u {} -p -D {} < {}".format(user,db,dbfile))
    run("rm {}".format(dbfile))

def cleanup(dbfile="dump.sql"):
    local("rm {} {}.tar.gz".format(dbfile,dbfile))
