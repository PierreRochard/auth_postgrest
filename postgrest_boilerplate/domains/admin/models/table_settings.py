from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String,
                        UniqueConstraint, text)
from sqlalchemy.dialects.postgresql import UUID

from postgrest_boilerplate.database.util import Base


class TableSettings(Base):
    __tablename__ = 'table_settings'
    __table_args__ = (UniqueConstraint('user',
                                       'table_name',
                                       name='table_settings_unique_constraint'),
                      {'schema': 'admin'},
                      )

    id = Column(UUID(as_uuid=True),
                server_default=text('auth.gen_random_uuid()'),
                primary_key=True)
    user = Column(String,
                  nullable=False,
                  server_default=text('current_user'))
    table_name = Column(String, nullable=False)

    can_delete = Column(Boolean, default=True)
    can_insert = Column(Boolean, default=True)
    can_update = Column(Boolean, default=True)
    custom_name = Column(String)
    submenu_id = Column(UUID, ForeignKey('admin.submenus.id'))
    icon = Column(String)
    is_visible = Column(Boolean, default=True)
    order_index = Column(Integer)
    row_limit = Column(Integer, default=10)
    row_offset = Column(Integer, default=0)
    sort_column = Column(String)
    sort_order = Column(Integer)