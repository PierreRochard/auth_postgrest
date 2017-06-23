from models.util import session_scope


def create_api_column_settings():
    with session_scope() as session:
        session.execute("""
        CREATE OR REPLACE VIEW api.table_column_settings AS 
          SELECT c.table_name,
                 c.column_name,
                 c.is_nullable,
                 c.column_default,
                 c.data_type,
                 tcs.id,
                 tcs.user,
                
                 tcs.can_update,
                 tcs.custom_name,
                 tcs.format,
                 tcs.order_index,
                 tcs.is_visible
          FROM admin.columns c
          LEFT OUTER JOIN admin.table_column_settings tcs
              ON c.table_name = tcs.table_name
              AND c.column_name = tcs.column_name
              AND tcs.user = current_user;
        """)

        session.execute("""
          DROP TRIGGER IF EXISTS column_settings_trigger ON api.table_column_settings;
        """)

        session.execute("""
          CREATE TRIGGER column_settings_trigger
          INSTEAD OF INSERT OR UPDATE OR DELETE
          ON api.table_column_settings
          FOR EACH ROW
          EXECUTE PROCEDURE admin.table_column_settings_function();
        """)
