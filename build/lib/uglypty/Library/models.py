from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer


Base = declarative_base()

def row2dict(row):
    # needed to convert sqlalchemy model to dict for serialization
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d

class Cred(Base):
    __tablename__ = 'creds'
    id = Column(Integer, primary_key=True)
    Username = Column('username', String(100))
    Password = Column('password', String(100))
    DisplayName = Column('displayname', String(100))

    def __repr__(self):
        return f"{self.Username}"

    def toDict(self):
        # "name" and "ip" are here for backward compatiblity
        tdict = {
            "id": self.id,
            "Username": self.Username,
            "Password": self.Password,
            "DisplayName": self.DisplayName
        }
        return tdict

