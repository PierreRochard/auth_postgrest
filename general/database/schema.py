from general.database.util import session_scope


class Schema(object):

    def __init__(self, name):
        self.name = name

    def create_schema(self):
        with session_scope(raise_programming_error=True) as session:
            session.execute(f"""
            CREATE SCHEMA IF NOT EXISTS {self.name};
                """)

    def create_extension(self, extension_name):
        with session_scope(raise_programming_error=True) as session:
            session.execute(f"""
             CREATE EXTENSION IF NOT EXISTS {extension_name} SCHEMA {self.name};
                """)

    @staticmethod
    def drop_extension(extension_name):
        with session_scope(raise_programming_error=True) as session:
            session.execute(f"""
                    DROP EXTENSION IF EXISTS {extension_name} CASCADE;
                """)

    @staticmethod
    def grant_privileges(schema_name: str, privilege_definitions: dict):
        for db_object_type, objects in privilege_definitions.items():
            for object_name, privileges in objects.items():
                for privilege_name, users in privileges.items():
                    for user in users:
                        if object_name in ('FUNCTION', 'TABLE', 'VIEW'):
                            path = f'{schema_name}.{object_name}'
                        else:
                            path = f'{object_name}'
                        with session_scope(raise_programming_error=True) as session:
                            session.execute(f'GRANT {privilege_name} '
                                            f'ON {db_object_type} '
                                            f'{path}'
                                            f' TO "{user}";')