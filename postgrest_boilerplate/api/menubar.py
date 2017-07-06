"""
    params.set('select', 'label, icon, routerLink, items{label, icon, routerLink}');
    params.set('is_visible', 'is.true');
    return this.restClient.get('/menubar', params);
"""

from postgrest_boilerplate.models.util import session_scope


def create_api_items():
    """
    NB: we can't use the api.table_settings view in the items view as
    this will break our ability to join with submenu
    """
    with session_scope() as session:
        session.execute("""
        CREATE OR REPLACE VIEW api.items AS 
          SELECT coalesce(ts.custom_name, initcap(replace(t.table_name, '_', ' '))) as label,
                 coalesce(ts.icon, 'fa-table') AS icon,
                 coalesce(ts.id, auth.gen_random_uuid()) as id,
                 ts.submenu_id,
                 string_to_array('/' || t.table_name, ' ') AS "routerLink",
                 coalesce(ts.order_index, 0) AS order_index
          FROM admin.tables t
          LEFT OUTER JOIN admin.table_settings ts
              ON t.table_name = ts.table_name
              AND ts.user = current_user
          WHERE current_user != 'anon' AND ts.is_visible
          UNION
          SELECT coalesce(fs.custom_name, f.form_name) as label,
                          fs.icon,
                          fs.id,
                          fs.submenu_id AS submenu_id,
                                 string_to_array('/rpc/' || fs.form_name, ' ') 
                                    AS "routerLink",
                          fs.order_index
          FROM admin.forms f
          LEFT OUTER JOIN admin.form_settings fs
            ON f.form_name = fs.form_name
            AND fs.user = current_user
          WHERE (current_user != 'anon' AND f.form_name != 'login')
             OR (current_user  = 'anon' AND f.form_name  = 'login')
             AND fs.is_visible
          ORDER BY order_index ASC NULLS LAST, label ASC NULLS LAST;
          """)

        session.execute("""
        GRANT SELECT ON api.items TO anon;
        """)


def create_api_submenus():
    with session_scope() as session:
        session.execute("""
        CREATE OR REPLACE VIEW api.menubar AS
         SELECT s.id,
                s.submenu_name AS label,
                s.icon,
                string_to_array('', '') as "routerLink",
                s.order_index
         FROM admin.submenus s
         WHERE s.user = current_user
           AND s.is_visible
           AND current_user != 'anon'
         UNION
         SELECT i.id,
                i.label,
                i.icon, 
                i."routerLink",
                i.order_index
         FROM api.items i
         WHERE i.submenu_id IS NULL
         ORDER BY order_index ASC NULLS LAST, label ASC NULLS LAST;
        """)

        session.execute("""
        GRANT SELECT ON api.menubar TO anon;
        """)
