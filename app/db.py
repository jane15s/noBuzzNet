from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///./nobuzznet.db', connect_args={"check_same_thread": False})
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    from app import models
    Base.metadata.create_all(bind=engine)

    from app.models import Link
    with Session(engine) as session:
        if not session.query(Link).first():
            default_links = [
                models.Link(
                    link="https://www.google.com",
                    description="Пошук в інтернеті",
                    icon = "https://www.google.com/favicon.ico"
                ),
                models.Link(
                    link="https://www.dtek.com",
                    description="DTEK",
                    icon="https://www.dtek.com/favicon.ico"
                ),
                models.Link(
                    link="https://www.facebook.com",
                    description="Facebook",
                    icon="https://www.facebook.com/favicon.ico"
                )
            ]
            session.add_all(default_links)
            session.commit()