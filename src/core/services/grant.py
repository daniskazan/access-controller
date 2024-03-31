from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from sqlalchemy.engine import create_engine

from core.models import Grant


class DatabaseCommandExecutor:
    def __init__(self, running_script: str, grant: Grant):
        self.running_script = running_script
        self.grant = grant

    def execute(self):
        engine = create_engine(url=self.grant.resource.url)
        Session = sessionmaker(engine)

        with Session() as session:
            res = session.execute(text(self.running_script))
            return res
