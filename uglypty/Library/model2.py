from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer
from sqlalchemy_serializer import SerializerMixin
Base = declarative_base()

def row2dict(row):
    # needed to convert sqlalchemy model to dict for serialization
    d = {}
    for column in row.__table__.columns:
        d[column.name] = str(getattr(row, column.name))
    return d

class Device_Model(Base):
    __tablename__ = 'devices'
    id = Column(Integer, primary_key=True)
    guid = Column('guid', String(100))
    Hostname = Column('Hostname', String(100))
    MgmtIP = Column('MgmtIP', String(100))
    DeviceType = Column('DeviceType', String(100))
    Vendor = Column('Vendor', String(100))
    Model = Column('Model', String(100))
    Site = Column('Site', String(100))
    site_description = Column('site_description', String(100))
    SoftwareVersion = Column('SoftwareVersion', String(10000))
    SerialNumber = Column('SerialNumber', String(100))
    SnmpRead = Column('SnmpRead', String(100))
    credsid = Column(Integer)
    secretid = Column(Integer)
    decommed = Column(Integer)
    monitored = Column(Integer)
    contexts = Column('contexts', String(200), default=None)
    ssh_reachable = Column('ssh_reachable', String(200), default=None)

    def __repr__(self):
        return f"{self.Hostname}:{self.Vendor}:{self.Model}:{self.MgmtIP}"

    def toDict(self):
        # "name" and "ip" are here for backward compatiblity
        tdict = {}
        tdict["id"] = self.id
        tdict["guid"] = self.guid
        tdict["Hostname"] = self.Hostname
        tdict["name"] = self.Hostname
        tdict["MgmtIP"] = self.MgmtIP
        tdict["ip"] = self.MgmtIP
        tdict["DeviceType"] = self.DeviceType
        tdict["Vendor"] = self.Vendor
        tdict["Model"] = self.Model
        tdict["Site"] = self.Site
        tdict['site_description'] = self.site_description
        tdict["SoftwareVersion"] = self.SoftwareVersion
        tdict["SerialNumber"] = self.SerialNumber
        tdict["SnmpRead"] = self.SnmpRead
        tdict["credsid"] = self.credsid
        tdict["secretid"] = self.secretid
        tdict["decommed"] = self.decommed
        tdict["monitored"] = self.monitored
        tdict["contexts"] = self.contexts
        tdict["ssh_reachable"] = self.ssh_reachable

        return tdict

class Cred(Base):
    __tablename__ = 'creds'
    id = Column(Integer, primary_key=True)
    Username = Column('username', String(100))
    Password = Column('password', String(100))

    def __repr__(self):
        return f"{self.Username}"

    def toDict(self):
        # "name" and "ip" are here for backward compatiblity
        tdict = {
            "id": self.id,
            "Username": self.Username,
            "Password": self.Password
        }
        return tdict


class Secret(Base):
    __tablename__ = 'secrets'
    id = Column(Integer, primary_key=True)
    Secret = Column('secret', String(100))

    def __repr__(self):
        return f"{self.Secret}"

class Capture_Model(Base):
    __tablename__ = "capture"
    id = Column(Integer, primary_key=True)
    Hostname = Column(String)
    content = Column(String)
    ctype = Column(String)
    context = Column(String)
    meta_data = Column(String)

    def __repr__(self):
        return f"{self.Hostname}:{self.ctype}"

    def toDict(self):
        # convert to dictionary
        tdict = {}
        tdict["id"] = self.id
        tdict["Hostname"] = self.Hostname
        tdict["content"] = self.content
        tdict["ctype"] = self.ctype
        tdict["context"] = self.context
        tdict["meta_data"] = self.meta_data
        return tdict

class Capture_View_Model(Base):
    __tablename__ = "vwcapturehosts"
    id = Column(Integer, primary_key=True)
    Hostname = Column(String)
    content = Column(String)
    ctype = Column(String)
    context = Column(String)
    MgmtIP = Column('MgmtIP', String(100))
    DeviceType = Column('DeviceType', String(100))
    Vendor = Column('Vendor', String(100))
    Model = Column('Model', String(100))
    meta_data = Column('meta_data', String(100))

    def __repr__(self):
        return f"{self.Hostname}:{self.ctype}"

    def toDict(self):
        # convert to dictionary

        tdict = {}
        tdict["id"] = self.id
        tdict["Hostname"] = self.Hostname
        tdict["content"] = self.content
        tdict["ctype"] = self.ctype
        tdict["context"] = self.context
        tdict["meta_data"] = self.meta_data
        tdict["Model"] = self.Model
        tdict["MgmtIP"] = self.MgmtIP
        tdict["meta_data"] = self.meta_data
        return tdict

# SQLAlchemy Model
class AuditDBModel(Base, SerializerMixin):
    __tablename__ = "audit"
    id = Column(Integer, primary_key=True)
    guid = Column(String)
    fguid = Column(String)
    scope_level = Column(String)
    result = Column(String)
    content = Column(String)
    summary = Column(String)
    aname = Column(String)
    rundate = Column(String)

class AuditDBModelCSV(Base, SerializerMixin):
    __tablename__ = "audit"
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True)
    guid = Column(String)
    fguid = Column(String)
    scope_level = Column(String)
    result = Column(String)
    content = Column(String)
    summary = Column(String)
    aname = Column(String)
    rundate = Column(String)
    csvdata = Column(String)


class Archive_Model(Base):
    __tablename__ = "archive"
    id = Column(Integer, primary_key=True)
    Hostname = Column(String)
    content = Column(String)
    ctype = Column(String)
    context = Column(String)
    meta_data = Column(String)

    jcontent = Column(String)
    ttp = Column(String)
    bdatetime = Column(String)
    fid = Column(String)

    def __repr__(self):
        return f"{self.Hostname}:{self.ctype}"

    def toDict(self):
        # convert to dictionary
        tdict = {}
        tdict["id"] = self.id
        tdict["Hostname"] = self.Hostname
        tdict["content"] = self.content
        tdict["ctype"] = self.ctype
        tdict["context"] = self.context
        tdict["meta_data"] = self.meta_data

        tdict["jcontent"] = self.jcontent
        tdict["ttp"] = self.ttp
        tdict["bdatetime"] = self.bdatetime
        tdict["fid"] = self.fid
        return tdict

class Archive_View_Model(Base):
    __tablename__ = "vwarchivehosts"
    id = Column(Integer, primary_key=True)
    hostname = Column(String)
    MgmtIP = Column(String)
    DeviceType = Column(String)
    Vendor = Column(String)
    Model = Column(String)
    content = Column(String)
    ctype = Column(String)
    context = Column(String)

    jcontent = Column(String)
    ttp = Column(String)
    bdatetime = Column(String)
    fid = Column(String)

    def __repr__(self):
        return f"{self.Hostname}:{self.ctype}"

    def toDict(self):
        # convert to dictionary
        tdict = {}
        tdict["id"] = self.id
        tdict["Hostname"] = self.Hostname
        tdict["MgmtIP"] = self.MgmtIP
        tdict["DeviceType"] = self.DeviceType
        tdict["Vendor"] = self.Vendor
        tdict["Model"] = self.Model
        tdict["content"] = self.content
        tdict["ctype"] = self.ctype
        tdict["context"] = self.context
        tdict["jcontent"] = self.jcontent
        tdict["ttp"] = self.ttp
        tdict["bdatetime"] = self.bdatetime
        tdict["fid"] = self.fid
        return tdict