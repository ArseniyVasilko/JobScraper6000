ALL_JOB_PAGES = {
    "Duunitori": "https://duunitori.fi/tyopaikat?haku=tieto-+ja+tietoliikennetekniikka+%28ala%29&order_by=date_posted&sivu="
}

SEARCH_INSTRUCTION = """
You will be given a job listing URL and a candidate's CV.
Retrieve the job listing from the URL using Google Search.

Then produce a structured evaluation with the following sections:

ROLE: One line — job title, company, and industry.
REQUIREMENTS: Key qualifications, skills, and experience the job demands.
CANDIDATE FIT: For each requirement, explicitly state whether the candidate meets it, partially meets it, or lacks it entirely. Be specific and critical — do not be generous.
VERDICT: A short concluding sentence on overall suitability. Be direct.
"""

CLASSIFY_INSTRUCTION = """
You are a strict binary classifier. You will be given a structured evaluation of a candidate against a job listing.

Read the evaluation — paying particular attention to the CANDIDATE FIT and VERDICT sections — and output a single classification:

"A" — the candidate is a reasonable fit and the job is worth applying to.
"B" — the candidate is not a good fit or the job is irrelevant to their profile.

Rules:
- Output ONLY a single uppercase letter: A or B.
- No spaces, punctuation, explanation, or newlines.
- Any response other than a single "A" or "B" is a failure.
"""

REVALIDATION_INSTRUCTION = """
You are a strict response formatter.
You will be given a previous AI response that was supposed to output only "A" or "B" but failed.
Read it, identify the final conclusion, and output ONLY that single letter.
- "A" if the conclusion was that the candidate is a reasonable fit.
- "B" if the conclusion was that the candidate is not a fit, or if the response is ambiguous.
- ONE character. No spaces. No punctuation. No explanation. No newlines.
"""

# SYSTEM_INSTRUCTION_OLD = system_instruction = """
# You are a precise, strict binary classifier evaluating a candidate's CV against a job description.
# Your primary task is to read the CV from given contents, evaluate the job description from the URL provided in the request, and determine if the job is worth applying to.
# The candidate's CV is provided directly as a file - Do NOT search for it online. Only use Google Search to look up the job listing URL.
#
# CRITICAL EVALUATION CRITERIA:
# 1. RELEVANCE CHECK: The job position MUST directly match the core education and technical/professional skills listed in the candidate's CV. If it is in an entirely different or irrelevant industry/field, automatically fail it.
# 2. COMPARISON CHECK: Analyze if the candidate satisfies a reasonable majority of the required experience, qualifications, and core skill requirements specified in the job description.
#
# OUTPUT FORMAT RULES:
# - You must ONLY output a single uppercase letter.
# - Output "A" if the job is relevant and worth applying to based on the criteria.
# - Output "B" if the job is irrelevant or the candidate does not meet the core qualifications.
# - DO NOT include spaces, punctuation, quotes, introductions, explanation text, or line breaks.
# - DO NOT provide additional text, information, summaries - ONLY A SINGLE "A" or "B"!
# - Strict penalty for deviation: ANY response other than a single "A" or "B" character is a failure.
# """
#

