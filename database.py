# Modified from:
# http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-iv-database

from migrate.versioning import api
from config import SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_TEST_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app.models import Base
from sys import argv
from sqlalchemy import create_engine
import os
import shutil
import imp

def create():
    create_engine(SQLALCHEMY_DEV_DATABASE_URI, echo=True)
    if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
        api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
        api.version_control(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    else:
        api.version_control(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))

def migrate():
    migration = SQLALCHEMY_MIGRATE_REPO + '/versions/%03d_migration.py' % (api.db_version(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO) + 1)
    tmp_module = imp.new_module('old_model')
    old_model = api.create_model(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    exec old_model in tmp_module.__dict__
    script = api.make_update_script_for_model(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, tmp_module.meta, Base.metadata)
    open(migration, "wt").write(script)
    api.upgrade(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print('New migration saved as ' + migration)
    print('Current database version: ' + str(api.db_version(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)))

def upgrade():
    api.upgrade(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))

def downgrade():
    v = api.db_version(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
    api.downgrade(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, v - 1)
    print 'Current database version: ' + str(api.db_version(SQLALCHEMY_DEV_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO))

def drop():
    os.remove(SQLALCHEMY_DEV_DATABASE_URI.split('///')[-1])
    shutil.rmtree(SQLALCHEMY_MIGRATE_REPO)

def prep_test():
    # Remove old database if it's there
    try:
        os.remove(SQLALCHEMY_TEST_DATABASE_URI.split('///')[-1])
    except OSError:
        pass

    engine = create_engine(SQLALCHEMY_TEST_DATABASE_URI)
    Base.metadata.create_all(engine)

if __name__ == "__main__":

    if argv[1] == "create":
        create()
    elif argv[1] == "migrate":
        migrate()
    elif argv[1] == "upgrade":
        upgrade()
    elif argv[1] == "downgrade":
        downgrade()
    elif argv[1] == "drop":
        drop()
    elif argv[1] == "prep_test":
        prep_test()
    else:
        print(str(argv[1]) + " is not a valid database operation.")