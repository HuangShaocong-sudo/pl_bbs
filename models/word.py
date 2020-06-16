from sqlalchemy import Column, Integer, UnicodeText

from models.base_model import db, SQLMixin
from models.user import User


class Word(SQLMixin, db.Model):
    __tablename__ = 'Word'
    content = Column(UnicodeText, nullable=False)
    wall_id = Column(Integer, nullable=False)
    user_id = Column(Integer, nullable=False)

    def user(self):
        u = User.one(id=self.user_id)
        return u