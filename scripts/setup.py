import sys
sys.path.insert(0, '../')

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from models import Base
from scripts import get_pg_url
from scripts.setup_login import install_login_function
from scripts.setup_users_table import install_user_table_functions
from scripts.setup_notifications import setup_table_notifications


def setup_database():
    engine = create_engine(get_pg_url(), echo=True)
    session = scoped_session(sessionmaker(bind=engine, autocommit=True))()
    session.connection().connection.set_isolation_level(0)

    Base.metadata.create_all(bind=engine)

    install_user_table_functions(session)

    install_login_function(session)

    for schema, table in [('api', 'messages')]:
        setup_table_notifications(session, schema, table)


if __name__ == '__main__':
    setup_database()
