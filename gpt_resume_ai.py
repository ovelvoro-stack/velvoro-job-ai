import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def gpt_score_resume(resume_text, job_role, experience):
    prompt = f"""
    You are an HR AI.
    Job Role: {job_role}
    Experience: {experience} years

    Resume:
    {resume_text}

    Give a score from 0 to 100.
    Only return the number.
    """

    model = genai.GenerativeModel("models/gemini-1.5-flash")
    response = model.generate_content(prompt)

    try:
        score = int("".join(filter(str.isdigit, response.text)))
        return min(score, 100)
    except:
        return 50
