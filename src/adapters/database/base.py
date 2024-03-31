from abc import ABC


class DatabaseAdapter(ABC):
    def __init__(
            self,
            *,
            db_url: str
    ):
        self.db_url = db_url

    def grant_read_access(self):
        ...

    def grant_write_access(self):
        ...

    def revoke_access(self):
        ...
