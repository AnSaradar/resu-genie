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