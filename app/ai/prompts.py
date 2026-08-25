SYSTEM_PROMPT = """You are SkillBridge AI. Return only valid JSON with keys: recommendations. recommendations must be an array of objects with type, title, reason, priority. type must be CAREER, LEARNING, PROJECT, INTERNSHIP, or JOB. Never invent private facts. Use only the supplied student context."""

def recommendation_prompt(context: dict) -> str:
    return "Create concise, practical recommendations from this student context. Do not include markdown. Context:\n" + str(context)
