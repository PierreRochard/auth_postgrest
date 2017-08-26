from general.database.schema import Schema
from general.database.util import session_scope
from general.domains.auth.models import Users

from .api_functions import create_login_api_trigger, create_logout_api_trigger


class AuthApiSchema(Schema):

    def __init__(self):
        super(AuthApiSchema, self).__init__(name='auth_api')

    def create_functions(self):
        create_login_api_trigger(self.name)
        create_logout_api_trigger(self.name)

    def grant_auth_privileges(self):
        with session_scope() as session:
            privileges = {
                'SCHEMA': {
                    'auth_api': {
                        'USAGE': [u.role for u in session.query(Users).all()]
                                     .append('anon')
                    }
                },
                'FUNCTION': {
                    'login(TEXT, TEXT)': {
                        'EXECUTE': ['anon']
                    }
                }
            }
        self.grant_privileges(self.name, privileges)