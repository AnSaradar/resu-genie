from enum import Enum

class ResponseSignal(Enum):
    SERVER_IS_UP = "Service is running"

    RESUME_BUILT_SUCCESS = "Resume has been built successfully"
    RESUME_BUILT_FAILURE = "Error while building resume"

    # Authentication signals
    LOGIN_FAILED = "Failed to login"
    LOGIN_SUCCESS = "Login successful"
    INCORRECT_CREDENTIALS = "Invalid email or password"
    
    # Registration signals
    USER_CREATION_FAILED = "User registration failed"
    USER_CREATION_SUCCESS = "User registered successfully"
    EMAIL_ALREADY_REGISTERED = "Email address is already registered"
    PHONE_ALREADY_REGISTERED = "Phone number is already registered"
    REGISTRATION_SERVER_ERROR = "Server error during registration"

    # User profile signals
    USER_PROFILE_ERROR = "Error while creating/updating user profile"
    USER_PROFILE_SUCCESS = "User profile created/updated successfully"
    USER_PROFILE_RETRIVE_ERROR = "Error while retrieving User Profile Data"
    USER_PROFILE_RETRIVE_SUCCESS = "User Profile Data retrived successfully"

    EXPERIENCE_CREATE_ERROR = "Error While Adding new Experainces"
    
    # Education related signals
    EDUCATION_CREATE_ERROR = "Error while adding new education entries"
    EDUCATION_RETRIEVE_ERROR = "Error while retrieving education data"
    EDUCATION_UPDATE_ERROR = "Error while updating education entry"
    EDUCATION_DELETE_ERROR = "Error while deleting education entry"
    EDUCATION_NOT_FOUND = "Education entry not found"
    
    # Skill related signals
    SKILL_CREATE_ERROR = "Error while adding new skill entries"
    SKILL_RETRIEVE_ERROR = "Error while retrieving skill data"
    SKILL_UPDATE_ERROR = "Error while updating skill entry"
    SKILL_DELETE_ERROR = "Error while deleting skill entry"
    SKILL_NOT_FOUND = "Skill entry not found"
    
    # Language related signals
    LANGUAGE_CREATE_ERROR = "Error while adding new language entries"
    LANGUAGE_RETRIEVE_ERROR = "Error while retrieving language data"
    LANGUAGE_UPDATE_ERROR = "Error while updating language entry"
    LANGUAGE_DELETE_ERROR = "Error while deleting language entry"
    LANGUAGE_NOT_FOUND = "Language entry not found"
    
    # Link related signals
    LINK_CREATE_ERROR = "Error while adding new link entries"
    LINK_RETRIEVE_ERROR = "Error while retrieving link data"
    LINK_UPDATE_ERROR = "Error while updating link entry"
    LINK_DELETE_ERROR = "Error while deleting link entry"
    LINK_NOT_FOUND = "Link entry not found"
    
    # Certification related signals
    CERTIFICATION_CREATE_ERROR = "Error while adding new certification entries"
    CERTIFICATION_RETRIEVE_ERROR = "Error while retrieving certification data"
    CERTIFICATION_UPDATE_ERROR = "Error while updating certification entry"
    CERTIFICATION_DELETE_ERROR = "Error while deleting certification entry"
    CERTIFICATION_NOT_FOUND = "Certification entry not found"
