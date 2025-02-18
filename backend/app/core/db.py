from sqlmodel import create_engine

from app.core.config import settings

# import to initialize tables
import app.models

def get_engine(echo=False):
    return create_engine(url=str(settings.SQLALCHEMY_DATABASE_URI), echo=echo)
