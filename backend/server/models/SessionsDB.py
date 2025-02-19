from sqlalchemy import Column, Integer, Text, Uuid

from backend.server.config import db


class SessionsDB(db.Model):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    session_id = Column(Uuid, unique=True)
    Oauth1 = Column(Text)
    Oauth2 = Column(Text)

    def __init__(self, session_id, Oauth1, Oauth2):
        self.session_id = session_id
        self.Oauth1 = Oauth1
        self.Oauth2 = Oauth2

    def __repr__(self):
        class_name = type(self).__name__

        return f"{class_name}ID:{self.session_id} Oauth1:{self.Oauth1} Oauth2:{self.Oauth2}"
