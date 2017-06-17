from sqlalchemy import Column, DateTime, String, text
from sqlalchemy.dialects.postgresql import UUID

from .util import Base


class Messages(Base):
    __tablename__ = 'messages'
    __table_args__ = {'schema': 'api'}

    id = Column(UUID(as_uuid=True),
                server_default=text('gen_random_uuid()'),
                primary_key=True)
    time = Column(DateTime, nullable=False, server_default=text('now()'))
    from_user = Column(String, nullable=False,
                       server_default=text('current_user'))
    to_user = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String)


def create_api_menubar_views(session):
    session.execute("""
    CREATE OR REPLACE VIEW api.items AS 
      SELECT coalesce(admin.table_settings.custom_name,
                      admin.tables.table_name) AS label,
             admin.table_settings.icon AS icon,
             admin.table_settings.id AS id,
             admin.table_settings.submenu_id AS submenu_id,
             string_to_array('/' || admin.table_settings.table_name, ' ') 
                AS "routerLink"
      FROM admin.tables
      LEFT OUTER JOIN admin.table_settings 
          ON admin.tables.table_name = admin.table_settings.table_name
          AND admin.table_settings.user = current_user
      UNION
      SELECT coalesce(admin.form_settings.custom_name,
      admin.forms.form_name) as label,
      admin.form_settings.icon,
      admin.form_settings.id,
      admin.form_settings.submenu_id AS submenu_id,
             string_to_array('/rpc/' || admin.form_settings.form_name, ' ') 
                AS "routerLink"
      FROM admin.forms
      LEFT OUTER JOIN admin.form_settings
        ON admin.forms.form_name = admin.form_settings.form_name
        AND admin.form_settings.user = current_user;
    GRANT SELECT ON api.items TO anon;
          """)


def create_api_submenus(session):
    session.execute("""
    CREATE OR REPLACE VIEW api.menubar AS
     SELECT admin.submenus.id,
            admin.submenus.submenu_name AS label,
            admin.submenus.icon,
            string_to_array('', '') as "routerLink"
     FROM admin.submenus
     WHERE admin.submenus.user = current_user
     UNION
     SELECT api.items.id,
            api.items.label,
            api.items.icon, 
            api.items."routerLink" 
     FROM api.items
     WHERE api.items.submenu_id IS NULL;
     
     GRANT SELECT, UPDATE, INSERT ON api.menubar TO anon;
    """)


def create_api_datatable_view(session):
    session.execute("""
      CREATE OR REPLACE VIEW api.datatable AS
        SELECT c.table_name, 
               c.column_name as field, 
               coalesce(cs.custom_name, c.column_name) as header
        FROM admin.columns c
          LEFT OUTER JOIN admin.column_settings cs
            ON c.table_name = cs.table_name
               AND c.column_name = cs.column_name
               AND cs.user = current_user;
    """)


def create_api_table_settings(session):
    session.execute("""
    CREATE OR REPLACE VIEW api.table_settings AS 
      SELECT admin.tables.table_name, 
             admin.table_settings.id,
             admin.table_settings.user,
             admin.table_settings.custom_name,
             admin.table_settings.submenu_id,
             admin.table_settings.icon,
             admin.table_settings.is_visible,
             admin.table_settings.can_insert,
             admin.table_settings.can_update,
             admin.table_settings.can_delete
      FROM admin.tables
      LEFT OUTER JOIN admin.table_settings 
          ON admin.tables.table_name = admin.table_settings.table_name
          AND admin.table_settings.user = current_user;
    
    DROP TRIGGER IF EXISTS table_settings_trigger ON api.table_settings;
    CREATE TRIGGER table_settings_trigger
        INSTEAD OF INSERT OR UPDATE OR DELETE
        ON api.table_settings
        FOR EACH ROW
    EXECUTE PROCEDURE admin.table_settings_function();
     GRANT SELECT ON api.table_settings TO anon;
    """)


def create_api_column_settings(session):
    session.execute("""
    CREATE OR REPLACE VIEW api.column_settings AS 
      SELECT admin.columns.table_name,
             admin.columns.column_name,
             admin.columns.is_nullable,
             admin.columns.column_default,
             admin.columns.data_type,
             admin.column_settings.id,
             admin.column_settings.user,
            
             admin.column_settings.can_update,
             admin.column_settings.custom_name,
             admin.column_settings.format,
             admin.column_settings.index,
             admin.column_settings.is_visible
      FROM admin.columns
      LEFT OUTER JOIN admin.column_settings 
          ON admin.columns.table_name = admin.column_settings.table_name
          AND admin.columns.column_name = admin.column_settings.column_name
          AND admin.column_settings.user = current_user;
        
      DROP TRIGGER IF EXISTS column_settings_trigger ON api.column_settings;
      CREATE TRIGGER column_settings_trigger
      INSTEAD OF INSERT OR UPDATE OR DELETE
      ON api.column_settings
      FOR EACH ROW
      EXECUTE PROCEDURE admin.column_settings_function();
    """)


def create_api_form_settings(session):
    session.execute("""
        CREATE OR REPLACE VIEW api.form_settings AS 
          SELECT admin.forms.form_name,
                 admin.forms.form_args,
                 admin.forms.form_arg_types,
                 admin.form_settings.id,
                 admin.form_settings.user,
                
                 admin.form_settings.custom_name,
                 admin.form_settings.submenu_id,
                 admin.form_settings.icon,
                 admin.form_settings.is_visible
          FROM admin.forms
          LEFT OUTER JOIN admin.form_settings 
              ON admin.forms.form_name = admin.form_settings.form_name
              AND admin.form_settings."user" = current_user;
      
      DROP TRIGGER IF EXISTS form_settings_trigger ON api.form_settings;
      CREATE TRIGGER form_settings_trigger
      INSTEAD OF INSERT OR UPDATE OR DELETE
      ON api.form_settings
      FOR EACH ROW
      EXECUTE PROCEDURE admin.form_settings_function();
    """)


def create_api_form_field_settings(session):
    session.execute("""
        CREATE OR REPLACE VIEW api.form_field_settings AS 
          SELECT admin.forms.form_name,
                 unnest(admin.forms.form_args) as form_field_name
          FROM admin.forms;
     GRANT SELECT ON api.form_field_settings TO anon;
    """)
