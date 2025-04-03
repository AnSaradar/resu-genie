from schemas.resume import Resume
import logging
from datetime import date

class ResumeController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def format_date(self, date_obj: date) -> str:
        """Format date object to YYYY-MM format."""
        if not date_obj:
            return ""
        return date_obj.strftime("%Y-%m")

    def format_date_range(self, start_date: date, end_date: date = None, is_current: bool = False) -> str:
        """Format date range with consistent YYYY-MM format."""
        start = self.format_date(start_date)
        if is_current:
            return f"{start} - Present"
        return f"{start} - {self.format_date(end_date)}" if end_date else start

    def prepare_resume_data(self, resume: Resume) -> dict:
        """
        Prepare the resume data by flattening nested structures 
        to match the template variables.
        """
        # Flatten `PersonalInfo`
        personal_info = resume.personal_info.dict()
        resume_data = {
            "name": personal_info.get("name"),
            "email": personal_info.get("email"),
            "phone": personal_info.get("phone"),
            "job_title": personal_info.get("current_job_title"),
            "linkedin": personal_info.get("linkedin"),
            "website": personal_info.get("website"),
            "city": personal_info.get("address").get("city"),
            "country": personal_info.get("address").get("country"),
            "summary": personal_info.get("profile_summary") if personal_info.get("profile_summary") else "",
            "technical_skills": [skill.name for skill in resume.technical_skills],
            "soft_skills": [skill.name for skill in resume.soft_skills],
        }

        # Process Experiences
        resume_data["experience"] = [
            {
                "title": exp.title,
                "company": exp.company,
                "seniority_level": exp.seniority_level.value,
                "location": exp.location,
                "date_range": self.format_date_range(
                    exp.start_date,
                    exp.end_date,
                    exp.currently_working
                ),
                "details": [exp.description] if exp.description else [],
            }
            for exp in resume.career_experiences
        ]

        # Process Volunteering
        resume_data["volunteering"] = [
            {
                "title": exp.title,
                "company": exp.company,
                "seniority_level": exp.seniority_level.value,
                "location": exp.location,
                "date_range": self.format_date_range(
                    exp.start_date,
                    exp.end_date,
                    exp.currently_working
                ),
                "details": [exp.description] if exp.description else [],
            }
            for exp in resume.volunteering_experiences
        ]

        # Process Education
        resume_data["education"] = [
            {
                "degree": edu.degree.value,
                "field": edu.field,
                "institution": edu.institution,
                "date_range": self.format_date_range(
                    edu.start_date,
                    edu.end_date,
                    edu.currently_studying
                ),
            }
            for edu in resume.education
        ]

        # Add Certifications (if any)
        resume_data["certifications"] = [
            {
                "name": cert.name,
                "organization": cert.issuing_organization,
                "issue_date": self.format_date(cert.issue_date),
            }
            for cert in (resume.certifications or [])
        ]

        resume_data["languages"] = [
            {
                "name" : lang.name,
                "proficiency" : lang.proficiency
            }

            for lang in (resume.languages or [])
        ]

        # Add Personal Work
        resume_data["personal_work"] = [
            {
                "title": project.title,
                "description": project.description,
            }
            for project in (resume.personal_projects or [])
        ]

        return resume_data
    