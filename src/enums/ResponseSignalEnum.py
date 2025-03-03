from enum import Enum

class ResponseSignal(Enum):
    SERVER_IS_UP = "Service is running"

    RESUME_BUILT_SUCCESS = "Resume has been built successfully"
    RESUME_BUILT_FAILURE = "Error while building resume"

    LOGIN_FAILED = "Failed to login"
    LOGIN_SUCCESS = "Login done successfully"
    INCORRECT_CREDENTIALS = "Invalid Email or Password"

    USER_CREATION_FAILED = "User creation failed"
    USER_CREATION_SUCCESS = "User created successfully"

    USER_PROFILE_ERROR = "Error while creating/updating user profile"
    USER_PROFILE_SUCCESS = "User profile created/updated successfully"

    USER_PROFILE_RETRIVE_ERROR = "Error while retrieving User Profile Data"
    USER_PROFILE_RETRIVE_SUCCESS = "User Profile Data retrived successfully"

    EXPERIENCE_CREATE_ERROR = "Error While Adding new Experainces"
