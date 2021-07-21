import os
basedir = os.path.abspath(os.path.dirname(__file__))

class RunConfig(object):
    DEBUG = True
    pguser = os.environ.get('PGUSER', 'postgres')
    pgpass = os.environ.get('PGPASSWORD', 'postgres')
    pghost = os.environ.get('PGHOST', 'db')
    pgport = os.environ.get('PGPORT', '5432')
    pgdb = os.environ.get('PGDATABASE', 'vessels_db')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{pguser}:{pgpass}@{pghost}:{pgport}/{pgdb}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class TestConfig(object):
    DEBUG = True
    pguser = os.environ.get('PGUSER', 'postgres')
    pgpass = os.environ.get('PGPASSWORD', 'postgres')
    pghost = os.environ.get('PGHOST', 'db')
    pgport = os.environ.get('PGPORT', '5432')
    pgdb = os.environ.get('PGDATABASETEST', 'vessels_db_test')
    SQLALCHEMY_DATABASE_URI = f'postgresql://{pguser}:{pgpass}@{pghost}:{pgport}/{pgdb}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

