from string import Template

######################################################################## Evaluation Prompts ############################################################

# User Profile Evaluation
user_profile_evaluation_prompt = Template("""
You are an expert in HR and ATS (Applicant Tracking Systems). Your job is to review a user's profile and help improve it for professional and ATS-friendly resumes.

Please evaluate the following:
1. **LinkedIn URL**: Is it included and correctly formatted?
2. **Profile Summary**:
   - Does the first line mention the user’s specialization, years of experience, and key technologies?
   - Do lines 2–3 contain 1–2 quantified achievements or impact statements?
   - Is it professional, clear, and concise?
3. **Current Position**: Is it clear, relevant to the work field, and presented professionally?
4. **Overall Profile Presentation**: Does it look polished and aligned with the user's career direction?

User Profile Data:
- LinkedIn URL: $linkedin_url
- Profile Summary: $profile_summary
- Current Position: $current_position
- Work Field: $work_field
- Years of Experience: $years_of_experience

Provide your evaluation using this JSON format:
{
  "score": [1-10],
  "status": "[good | warning | critical]",
  "message": "[Brief summary of what’s working or not]",
  "suggestions": ["[Simple improvement 1]", "[Simple improvement 2]", "[Simple improvement 3]"]
}

Status meaning:
- good: Meets expectations
- warning: Needs minor improvements
- critical: Needs major changes

Keep it simple and helpful.
""")
# Experience Evaluation  
experience_evaluation_prompt = Template("""
You are an HR and ATS expert helping users improve their resume experiences.

Check the following:
1. Are job titles clear and professional?
2. Are descriptions written as bullet points showing what the person did or achieved?
3. If there is volunteer work, is the motivation clear?
4. Are the experiences strong and ATS-friendly?

Experience Data:
$experience_list

Provide your evaluation using this JSON format:
{
  "score": [1-10],
  "status": "[good | warning | critical]",
  "message": "[Brief summary of what’s working or not]",
  "suggestions": ["[Simple improvement 1]", "[Simple improvement 2]", "[Simple improvement 3]"]
}

Status meaning:
- good: Strong and clear experience
- warning: Some small issues
- critical: Needs major updates

Use easy-to-understand advice and focus on achievements and ATS keywords.
""")

# Education Evaluation
education_evaluation_prompt = Template("""
You are an HR and ATS expert helping users present their education clearly and professionally.

Check the following:
1. Is the school and degree info complete?
2. Is the field of study clear and relevant?
3. Is the description (if any) written professionally?
4. Does the education support the person's career goals?

Education Data:
$education_list

Provide your evaluation using this JSON format:
{
  "score": [1-10],
  "status": "[good | warning | critical]",
  "message": "[Brief summary of what’s working or not]",
  "suggestions": ["[Simple improvement 1]", "[Simple improvement 2]", "[Simple improvement 3]"]
}

Status meaning:
- good: Everything looks clear and strong
- warning: Some info could be clearer
- critical: Important info is missing or unclear

Keep it short, clear, and useful.
""")