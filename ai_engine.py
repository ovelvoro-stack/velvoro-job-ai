def score_resume(text):
    keywords = [
        "python","java","developer","experience",
        "skills","project","sales","marketing"
    ]
    score = 0
    text = text.lower()
    for k in keywords:
        if k in text:
            score += 10
    return min(score, 100)
