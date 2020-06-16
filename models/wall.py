from sqlalchemy import Unicode, Column

from models.base_model import db, SQLMixin


class Wall(SQLMixin, db.Model):
    title = Column(Unicode(50), nullable=False)
