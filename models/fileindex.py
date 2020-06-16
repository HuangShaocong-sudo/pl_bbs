from sqlalchemy import Column, Integer, String

from models.base_model import db, SQLMixin


class FileIndex(SQLMixin, db.Model):
    filename = Column(String(50), nullable=False)
    localname = Column(String(50), nullable=False)
    user_id = Column(Integer, nullable=False)
    download_times = Column(Integer, nullable=False, default=0)
    college_id = Column(Integer, nullable=False)