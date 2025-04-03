from enum import Enum

# Define Enum for Seniority Levels
class SeniorityLevel(str, Enum):
    INTERN = "Intern"
    JUNIOR = "Junior"
    MID = "Mid-level"
    SENIOR = "Senior"
    LEAD = "Lead"
    MANAGER = "Manager"
    DIRECTOR = "Director"
    EXECUTIVE = "Executive"


class Degree(str, Enum):
    BACHELOR = "Bachelor"
    MASTER = "Master"
    PHD = "PhD"
    ASSOCIATE = "Associate"
    DIPLOMA = "Diploma"
    OTHER = "Other"
    

class SkillProficiency(str, Enum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"
    MASTER = "Master"


class LanguageProficiency(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

class WorkField(str, Enum):
    SOFTWARE_DEVELOPMENT = "Software Development"
    DATA_SCIENCE = "Data Science"
    WEB_DEVELOPMENT = "Web Development"
    MOBILE_DEVELOPMENT = "Mobile Development"
    CLOUD_COMPUTING = "Cloud Computing"
    DEVOPS = "DevOps"
    CYBERSECURITY = "Cybersecurity"
    UI_UX_DESIGN = "UI/UX Design"
    PRODUCT_MANAGEMENT = "Product Management"
    PROJECT_MANAGEMENT = "Project Management"
    DIGITAL_MARKETING = "Digital Marketing"
    CONTENT_CREATION = "Content Creation"
    CUSTOMER_SERVICE = "Customer Service"
    SALES = "Sales"
    FINANCE = "Finance"
    HR = "Human Resources"
    HEALTHCARE = "Healthcare"
    EDUCATION = "Education"
    RESEARCH = "Research"
    LEGAL = "Legal"
    OTHER = "Other"

    
