from sqlalchemy import Column, Unicode, UnicodeText, Integer

from models.base_model import SQLMixin, db
from models.user import User
from models.topic import Topic


class Message(SQLMixin, db.Model):
    topic_id = Column(Integer, nullable=False)
    replier_id = Column(Integer, nullable=False)
    receiver_id = Column(Integer, nullable=False)
    read = Column(Integer, nullable=False, default=0)
    content = Column(UnicodeText, nullable=False)

    def topic(self):
        u = Topic.one(id=self.topic_id)
        return u

    def replier(self):
        u = User.one(id=self.replier_id)
        # return u
        return u.username
