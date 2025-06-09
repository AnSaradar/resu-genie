from string import Template

######################################################################## Evaluation Prompts ############################################################

# User Profile Evaluation
user_profile_evaluation_prompt = Template("""
You are an ATS and HR expert evaluating a user profile for resume optimization.

Evaluate this user profile based on:
1. LinkedIn URL presence and format
2. Profile summary quality (should contain current job title and services offered)
3. Current position clarity and relevance
4. Overall professional presentation

User Profile Data:
- LinkedIn URL: $linkedin_url
- Profile Summary: $profile_summary  
- Current Position: $current_position
- Work Field: $work_field
- Years of Experience: $years_of_experience

Provide evaluation in this exact JSON format:
{
  "score": [1-10 integer],
  "message": "[Short diagnostic summary in 1-2 sentences]",
  "suggestions": ["[Actionable tip 1]", "[Actionable tip 2]", "[Actionable tip 3]"]
}

Focus on ATS compatibility and professional presentation.
""")

# Experience Evaluation  
experience_evaluation_prompt = Template("""
You are an ATS and HR expert evaluating work experience entries for resume optimization.

Evaluate these experiences based on:
1. Job title clarity and professionalism
2. Description quality (should be in bullet points showing services/achievements)
3. Volunteer work motivation (if applicable)
4. Overall ATS compatibility and impact

Experience Data:
$experience_list

Provide evaluation in this exact JSON format:
{
  "score": [1-10 integer], 
  "message": "[Short diagnostic summary in 1-2 sentences]",
  "suggestions": ["[Actionable tip 1]", "[Actionable tip 2]", "[Actionable tip 3]"]
}

Focus on quantifiable achievements and ATS keyword optimization.
""")

# Education Evaluation
education_evaluation_prompt = Template("""
You are an ATS and HR expert evaluating education entries for resume optimization.

Evaluate these education entries based on:
1. Institution and degree information completeness
2. Field of study relevance and clarity  
3. Description quality and professional presentation
4. Overall contribution to candidacy

Education Data:
$education_list

Provide evaluation in this exact JSON format:
{
  "score": [1-10 integer],
  "message": "[Short diagnostic summary in 1-2 sentences]", 
  "suggestions": ["[Actionable tip 1]", "[Actionable tip 2]", "[Actionable tip 3]"]
}

Focus on relevance to career goals and professional presentation.
""") 