from schemas.resume import Resume
from typing import Dict, List, Any, Optional
import logging
from datetime import date

class ResumeController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def format_date(self, date_obj: Optional[date]) -> str:
        """Format date object to YYYY-MM format."""
        if not date_obj:
            return ""
        return date_obj.strftime("%Y-%m")

    def format_date_range(self, start_date: Optional[date], end_date: Optional[date] = None, is_current: bool = False) -> str:
        """Format date range with consistent YYYY-MM format."""
        if not start_date:
            return ""
        
        start = self.format_date(start_date)
        if is_current:
            return f"{start} - Present"
        return f"{start} - {self.format_date(end_date)}" if end_date else start

    def validate_resume_data(self, resume: Resume) -> List[str]:
        """Validate resume data and return list of missing required fields."""
        missing_fields = []
        
        # Check personal info requirements
        if not resume.personal_info:
            missing_fields.append("personal_info")
        
        # Check if user has any experiences or education
        if not resume.career_experiences and not resume.education:
            missing_fields.append("Either career_experiences or education is required")
            
        return missing_fields

    def extract_personal_info(self, resume: Resume, current_user: Optional[dict] = None) -> Dict[str, str]:
        """Extract and prepare personal information from various sources."""
        personal_info = resume.personal_info
        
        # Get basic info from current_user if available, otherwise try fallback
        if current_user:
            full_name = f"{current_user.get('first_name', '')} {current_user.get('last_name', '')}".strip()
            email = current_user.get("email", "")
            phone = current_user.get("phone", "")
        else:
            full_name = email = phone = ""
        
        # Extract location info from address
        location_info = {"city": "", "country": ""}
        if personal_info and personal_info.address:
            location_info["city"] = personal_info.address.city or ""
            location_info["country"] = personal_info.address.country or ""
        
        return {
            "name": full_name,
            "email": email,
            "phone": phone,
            "job_title": personal_info.current_position or "" if personal_info else "",
            "linkedin": personal_info.linkedin_url or "" if personal_info else "",
            "website": personal_info.website_url or "" if personal_info else "",
            "summary": personal_info.profile_summary or "" if personal_info else "",
            "work_field": personal_info.work_field.value if personal_info and personal_info.work_field else "",
            "years_of_experience": personal_info.years_of_experience or "" if personal_info else "",
            "current_position": personal_info.current_position or "" if personal_info else "",
            **location_info
        }

    def process_skills(self, skills: List[Any], skill_type: str) -> List[str]:
        """Process skills and return list of skill names for templates."""
        try:
            if not skills:
                return []
            
            skill_names = []
            for skill in skills:
                if hasattr(skill, 'name') and skill.name:
                    skill_names.append(skill.name)
                else:
                    self.logger.warning(f"Invalid skill object in {skill_type}: {skill}")
            
            return skill_names
        except Exception as e:
            self.logger.error(f"Error processing {skill_type}: {e}")
            return []

    def process_experiences(self, experiences: List[Any]) -> List[Dict[str, Any]]:
        """Process experiences and return list of formatted experience data."""
        if not experiences:
            return []
        
        processed_experiences = []
        for exp in experiences:
            try:
                # Handle location
                location_str = ""
                if exp.location:
                    city = getattr(exp.location, 'city', '') or ""
                    country = getattr(exp.location, 'country', '') or ""
                    location_str = f"{city}, {country}".strip(", ")
                
                # Process description - handle bullet points and sentence splitting
                details = []
                if exp.description:
                    description = exp.description.strip()
                    
                    # Check if description already contains bullet points (• or -)
                    if '•' in description or description.startswith('-'):
                        # Split by bullet points
                        if '•' in description:
                            bullet_items = [item.strip() for item in description.split('•') if item.strip()]
                        else:
                            bullet_items = [item.strip() for item in description.split('-') if item.strip()]
                        
                        # Clean up each bullet item
                        for item in bullet_items:
                            if item:
                                # Remove leading/trailing spaces and ensure proper punctuation
                                cleaned_item = item.strip()
                                if cleaned_item and not cleaned_item.endswith(('.', '!', '?')):
                                    cleaned_item += '.'
                                details.append(cleaned_item)
                    else:
                        # Split by sentence-ending periods (with space after)
                        sentences = [s.strip() for s in description.split('. ') if s.strip()]
                        
                        # Add period back to sentences (except the last one if it already has one)
                        for i, sentence in enumerate(sentences):
                            if i == len(sentences) - 1:
                                # Last sentence - only add period if it doesn't end with punctuation
                                if not sentence.endswith(('.', '!', '?', ':')):
                                    sentence += '.'
                            else:
                                # Not last sentence - add period
                                if not sentence.endswith('.'):
                                    sentence += '.'
                            details.append(sentence)
                    
                    # If no details were created, keep original description
                    if not details and exp.description:
                        details = [exp.description]
                
                experience_data = {
                    "title": exp.title or "",
                    "company": exp.company or "",
                    "seniority_level": exp.seniority_level.value if exp.seniority_level else "",
                    "location": location_str,
                    "date_range": self.format_date_range(
                        exp.start_date,
                        exp.end_date,
                        exp.currently_working
                    ),
                    "details": details,
                }
                processed_experiences.append(experience_data)
                
            except Exception as e:
                self.logger.error(f"Error processing experience {getattr(exp, 'title', 'Unknown')}: {e}")
                continue
        
        return processed_experiences

    def process_education(self, education: List[Any]) -> List[Dict[str, Any]]:
        """Process education and return list of formatted education data."""
        if not education:
            return []
        
        processed_education = []
        for edu in education:
            try:
                education_data = {
                    "degree": edu.degree.value if edu.degree else "",
                    "field": edu.field or "",
                    "institution": edu.institution or "",
                    "date_range": self.format_date_range(
                        edu.start_date,
                        edu.end_date,
                        edu.currently_studying
                    ),
                    "description": edu.description or "",
                }
                processed_education.append(education_data)
                
            except Exception as e:
                self.logger.error(f"Error processing education {getattr(edu, 'institution', 'Unknown')}: {e}")
                continue
        
        return processed_education

    def process_certifications(self, certifications: List[Any]) -> List[Dict[str, Any]]:
        """Process certifications and return list of formatted certification data."""
        if not certifications:
            return []
        
        processed_certs = []
        for cert in certifications:
            try:
                cert_data = {
                    "name": cert.name or "",
                    "organization": cert.issuing_organization or "",
                    "issue_date": self.format_date(cert.issue_date),
                    "certificate_url": cert.certificate_url or "",
                    "description": cert.description or "",
                }
                processed_certs.append(cert_data)
                
            except Exception as e:
                self.logger.error(f"Error processing certification {getattr(cert, 'name', 'Unknown')}: {e}")
                continue
        
        return processed_certs

    def process_languages(self, languages: List[Any]) -> List[Dict[str, str]]:
        """Process languages and return list of formatted language data."""
        if not languages:
            return []
        
        processed_languages = []
        for lang in languages:
            try:
                lang_data = {
                    "name": lang.name or "",
                    "proficiency": lang.proficiency.value if lang.proficiency else ""
                }
                processed_languages.append(lang_data)
                
            except Exception as e:
                self.logger.error(f"Error processing language {getattr(lang, 'name', 'Unknown')}: {e}")
                continue
        
        return processed_languages

    def process_personal_projects(self, projects: List[Any]) -> List[Dict[str, Any]]:
        """Process personal projects and return list of formatted project data."""
        if not projects:
            return []
        
        processed_projects = []
        for project in projects:
            try:
                project_data = {
                    "title": project.title or "",
                    "description": project.description or "",
                    "technologies": project.technologies if hasattr(project, 'technologies') and project.technologies else [],
                    "url": project.url or "",
                    "repository_url": project.repository_url or "",
                    "date_range": self.format_date_range(
                        getattr(project, 'start_date', None),
                        getattr(project, 'end_date', None),
                        getattr(project, 'is_ongoing', False)
                    ) if hasattr(project, 'start_date') and project.start_date else ""
                }
                processed_projects.append(project_data)
                
            except Exception as e:
                self.logger.error(f"Error processing project {getattr(project, 'title', 'Unknown')}: {e}")
                continue
        
        return processed_projects

    def process_personal_links(self, links: List[Any]) -> List[Dict[str, str]]:
        """Process personal links and return list of formatted link data."""
        if not links:
            return []
        
        processed_links = []
        for link in links:
            try:
                link_data = {
                    "website_name": link.website_name or "",
                    "website_url": link.website_url or "",
                }
                processed_links.append(link_data)
                
            except Exception as e:
                self.logger.error(f"Error processing link {getattr(link, 'website_name', 'Unknown')}: {e}")
                continue
        
        return processed_links

    def prepare_resume_data(self, resume: Resume, current_user: Optional[dict] = None) -> Dict[str, Any]:
        """
        Prepare the resume data by processing all sections and creating template-ready data structure.
        """
        try:
            # Validate resume data first
            validation_errors = self.validate_resume_data(resume)
            if validation_errors:
                self.logger.warning(f"Resume validation warnings: {validation_errors}")
            
            # Start building the resume data dictionary
            resume_data = {}
            
            # Process personal information
            resume_data.update(self.extract_personal_info(resume, current_user))
            
            # Process skills (templates expect list of strings)
            resume_data["technical_skills"] = self.process_skills(resume.technical_skills, "technical_skills")
            resume_data["soft_skills"] = self.process_skills(resume.soft_skills, "soft_skills")
            
            # Process experiences
            resume_data["experience"] = self.process_experiences(resume.career_experiences)
            resume_data["volunteering"] = self.process_experiences(resume.volunteering_experiences)
            
            # Process education
            resume_data["education"] = self.process_education(resume.education)
            
            # Process certifications
            resume_data["certifications"] = self.process_certifications(resume.certifications)
            
            # Process languages
            resume_data["languages"] = self.process_languages(resume.languages)
            
            # Process personal projects
            resume_data["personal_work"] = self.process_personal_projects(resume.personal_projects)
            
            # Process personal links
            resume_data["personal_links"] = self.process_personal_links(resume.personal_links)
            
            self.logger.info("Resume data prepared successfully")
            return resume_data
            
        except Exception as e:
            self.logger.error(f"Error preparing resume data: {e}")
            raise ValueError(f"Failed to prepare resume data: {str(e)}")
    