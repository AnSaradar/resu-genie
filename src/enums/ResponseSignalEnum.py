from enum import Enum

class ResponseSignal(Enum):
    SERVER_IS_UP = "Service is running"

    RESUME_BUILT_SUCCESS = "Resume has been built successfully"
    RESUME_BUILT_FAILURE = "Error while building resume"