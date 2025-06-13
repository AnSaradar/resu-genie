from datetime import datetime
from typing import List
import os

def remove_file(file_path: str) -> None:
    """Remove a file from the file system"""
    if os.path.exists(file_path):
        os.remove(file_path)

#education
def convert_dates_for_storage(data_dict: dict) -> dict:
    """Convert date objects to datetime objects for MongoDB storage"""
    # Handle start_date (required field)
    if 'start_date' in data_dict and data_dict['start_date'] is not None:
        data_dict["start_date"] = datetime.combine(data_dict["start_date"], datetime.min.time())
    
    # Handle end_date (optional field - can be None)
    if 'end_date' in data_dict and data_dict['end_date'] is not None:
        data_dict["end_date"] = datetime.combine(data_dict["end_date"], datetime.min.time())
    
    return data_dict

def prepare_education_for_response(edu_dict: dict) -> dict:
    """Convert datetime back to date and add computed fields for response DTOs"""
    # Convert ObjectId to string for response DTO
    if '_id' in edu_dict and edu_dict['_id'] is not None:
        edu_dict['_id'] = str(edu_dict['_id'])
    
    # Convert datetime back to date for response
    if 'start_date' in edu_dict and isinstance(edu_dict['start_date'], datetime):
        edu_dict['start_date'] = edu_dict['start_date'].date()
    if 'end_date' in edu_dict and edu_dict['end_date'] is not None and isinstance(edu_dict['end_date'], datetime):
        edu_dict['end_date'] = edu_dict['end_date'].date()
    
    # Add computed duration field that EducationResponse expects
    if edu_dict.get('currently_studying', False):
        edu_dict['duration'] = f"From {edu_dict['start_date']} to Present"
    elif edu_dict.get('end_date'):
        edu_dict['duration'] = f"From {edu_dict['start_date']} to {edu_dict['end_date']}"
    else:
        edu_dict['duration'] = f"Started on {edu_dict['start_date']}"
    
    return edu_dict

def prepare_educations_for_response(educations: List[dict]) -> List[dict]:
    """Prepare multiple educations for response DTOs"""
    return [prepare_education_for_response(edu) for edu in educations]

#experience

def convert_dates_for_storage_experience(data_dict: dict) -> dict:
    """Convert date objects to datetime objects for MongoDB storage"""
    # Handle start_date (required field)
    if 'start_date' in data_dict and data_dict['start_date'] is not None:
        data_dict["start_date"] = datetime.combine(data_dict["start_date"], datetime.min.time())
    
    # Handle end_date (optional field - can be None)
    if 'end_date' in data_dict and data_dict['end_date'] is not None:
        data_dict["end_date"] = datetime.combine(data_dict["end_date"], datetime.min.time())
    
    return data_dict

def prepare_experience_for_response(exp_dict: dict) -> dict:
    """Convert datetime back to date and add computed fields for response DTOs"""
    # Convert ObjectId to string for response DTO (if needed)
    if '_id' in exp_dict and exp_dict['_id'] is not None:
        exp_dict['_id'] = str(exp_dict['_id'])
    
    # Convert datetime back to date for response
    if 'start_date' in exp_dict and isinstance(exp_dict['start_date'], datetime):
        exp_dict['start_date'] = exp_dict['start_date'].date()
    if 'end_date' in exp_dict and exp_dict['end_date'] is not None and isinstance(exp_dict['end_date'], datetime):
        exp_dict['end_date'] = exp_dict['end_date'].date()
    
    # Add computed fields that ExperienceResponse expects
    exp_dict['is_active'] = exp_dict.get('currently_working', False)
    
    # Calculate duration
    if exp_dict.get('currently_working', False):
        exp_dict['duration'] = f"From {exp_dict['start_date']} to Present"
    elif exp_dict.get('end_date'):
        exp_dict['duration'] = f"From {exp_dict['start_date']} to {exp_dict['end_date']}"
    else:
        exp_dict['duration'] = f"Started on {exp_dict['start_date']}"
    
    return exp_dict

def prepare_experiences_for_response(experiences: List[dict]) -> List[dict]:
    """Prepare multiple experiences for response DTOs"""
    return [prepare_experience_for_response(exp) for exp in experiences]


#skill
def prepare_skill_for_response(skill_dict: dict) -> dict:
    """Convert ObjectId to string for response DTOs"""
    # Convert ObjectId to string for response DTO
    if '_id' in skill_dict and skill_dict['_id'] is not None:
        skill_dict['_id'] = str(skill_dict['_id'])
    
    return skill_dict

def prepare_skills_for_response(skills: List[dict]) -> List[dict]:
    """Prepare multiple skills for response DTOs"""
    return [prepare_skill_for_response(skill) for skill in skills]

#language
def prepare_language_for_response(language_dict: dict) -> dict:
    """Convert ObjectId to string for response DTOs"""
    # Convert ObjectId to string for response DTO
    if '_id' in language_dict and language_dict['_id'] is not None:
        language_dict['_id'] = str(language_dict['_id'])
    
    return language_dict

def prepare_languages_for_response(languages: List[dict]) -> List[dict]:
    """Prepare multiple languages for response DTOs"""
    return [prepare_language_for_response(language) for language in languages]


#certification
def prepare_certification_for_response(certification_dict: dict) -> dict:
    """Convert ObjectId to string for response DTOs"""
    # Convert ObjectId to string for response DTO
    if '_id' in certification_dict and certification_dict['_id'] is not None:
        certification_dict['_id'] = str(certification_dict['_id'])
     
    return certification_dict    

def convert_dates_for_storage_certification(data_dict: dict) -> dict:
    """Convert date objects to datetime objects for MongoDB storage"""
    if 'issue_date' in data_dict and data_dict['issue_date'] is not None:
        data_dict["issue_date"] = datetime.combine(data_dict["issue_date"], datetime.min.time())
    
    return data_dict

def prepare_certifications_for_response(certifications: List[dict]) -> List[dict]:
    """Prepare multiple certifications for response DTOs"""
    return [prepare_certification_for_response(certification) for certification in certifications]


#link
def prepare_link_for_response(link_dict: dict) -> dict:
    """Convert ObjectId to string for response DTOs"""
    # Convert ObjectId to string for response DTO
    if '_id' in link_dict and link_dict['_id'] is not None:
        link_dict['_id'] = str(link_dict['_id'])
    
    return link_dict

def prepare_links_for_response(links: List[dict]) -> List[dict]:
    """Prepare multiple links for response DTOs"""
    return [prepare_link_for_response(link) for link in links]


#personal_project
def convert_dates_for_storage_personal_project(data_dict: dict) -> dict:
    """Convert date objects to datetime objects for MongoDB storage"""
    # Handle start_date (optional field)
    if 'start_date' in data_dict and data_dict['start_date'] is not None:
        data_dict["start_date"] = datetime.combine(data_dict["start_date"], datetime.min.time())
    
    # Handle end_date (optional field - can be None)
    if 'end_date' in data_dict and data_dict['end_date'] is not None:
        data_dict["end_date"] = datetime.combine(data_dict["end_date"], datetime.min.time())
    
    return data_dict

def prepare_personal_project_for_response(project_dict: dict) -> dict:
    """Convert datetime back to date and add computed fields for response DTOs"""
    # Convert ObjectId to string for response DTO
    if '_id' in project_dict and project_dict['_id'] is not None:
        project_dict['_id'] = str(project_dict['_id'])
    
    # Convert datetime back to date for response
    if 'start_date' in project_dict and project_dict['start_date'] is not None and isinstance(project_dict['start_date'], datetime):
        project_dict['start_date'] = project_dict['start_date'].date()
    if 'end_date' in project_dict and project_dict['end_date'] is not None and isinstance(project_dict['end_date'], datetime):
        project_dict['end_date'] = project_dict['end_date'].date()
    
    # Add computed duration field that PersonalProjectResponse expects
    if project_dict.get('start_date') and project_dict.get('end_date'):
        if project_dict.get('is_ongoing', False):
            project_dict['duration'] = f"From {project_dict['start_date']} to Present"
        else:
            project_dict['duration'] = f"From {project_dict['start_date']} to {project_dict['end_date']}"
    elif project_dict.get('start_date'):
        if project_dict.get('is_ongoing', False):
            project_dict['duration'] = f"From {project_dict['start_date']} to Present"
        else:
            project_dict['duration'] = f"Started on {project_dict['start_date']}"
    else:
        project_dict['duration'] = None
    
    return project_dict

def prepare_personal_projects_for_response(projects: List[dict]) -> List[dict]:
    """Prepare multiple personal projects for response DTOs"""
    return [prepare_personal_project_for_response(project) for project in projects]