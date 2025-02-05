from core.config import get_settings,Settings
import os
import json
from datetime import datetime, date

class BaseController:
    def __init__(self):
        self.app_settings = get_settings()
    
    def get_json_serializable_object(self, info):
        return json.loads(
            json.dumps(
                info, 
                default=lambda x: x.isoformat() if isinstance(x, (datetime, date)) else x.__dict__
            )
        )