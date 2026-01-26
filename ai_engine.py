def ai_score_candidate(experience, qualification):
    score = 0

    if experience.lower() != "fresher":
        score += 50
    if qualification.lower() in ["degree","btech","mba"]:
        score += 50

    result = "PASS" if score >= 50 else "FAIL"
    return score, result
