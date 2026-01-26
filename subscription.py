def can_use_ai(plan):
    return plan in ["PRO", "ENTERPRISE"]

def job_limit(plan):
    if plan == "FREE":
        return 5
    return 1000
