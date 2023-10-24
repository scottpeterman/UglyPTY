from sqlalchemy import text

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


def get_by_dbid(DBObj, session, dbid=None):
    result = None
    if dbid is None:
        try:
            result = session.query(DBObj).all()
        except Exception as e:
            print(e)
    else:
        try:
            result = session.query(DBObj).filter_by(id=dbid).all()
        except Exception as e:
            print(e)
    return result


def get_by_dbquery(DBObj, session, dbquery=None):
    result = None
    if dbquery is None:
        try:
            result = session.query(DBObj).all()
        except Exception as e:
            print(e)
    else:
        try:
            result = session.query(DBObj).from_statement(text(dbquery)).all()
        except Exception as e:
            print(e)
    return result

