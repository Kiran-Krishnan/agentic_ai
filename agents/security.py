def analyze_security(context):
    risks = []

    if "password" in context.lower():
        risks.append("Sensitive data exposure")

    if "admin" in context.lower():
        risks.append("Privilege-related data")

    return risks


#Need to add more security parameters