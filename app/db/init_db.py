import logging
from app.db.database import Base, engine
from app.models.user import User
from app.models.research_project import ResearchProject, ResearchMember
from app.models.research_task import ResearchTask

logger = logging.getLogger("app")


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_db() 