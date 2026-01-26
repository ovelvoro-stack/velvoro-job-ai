def resume_score(text):
    score = 0
    keywords = ["python","java","sql","sales","marketing","excel"]

    score += min(len(text)//200, 30)

    for k in keywords:
        if k in text.lower():
            score += 10

    return min(score, 100)
