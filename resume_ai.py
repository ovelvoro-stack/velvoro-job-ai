def score_resume(resume_text, category, experience):
    score = 0

    keywords = {
        "IT": ["python", "java", "sql", "developer"],
        "NON-IT": ["sales", "marketing", "account", "hr"]
    }

    for word in keywords.get(category, []):
        if word.lower() in resume_text.lower():
            score += 15

    exp_years = int(experience.split()[0])
    score += min(exp_years * 2, 20)

    return min(score, 100)
