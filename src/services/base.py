from core.config import get_settings, Settings

class BaseService:
    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_settings = get_settings()
