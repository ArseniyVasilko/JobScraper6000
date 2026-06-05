# General settings
REQUEST_DELAY_MIN=3 # Non-negative int/float only, seconds
REQUEST_DELAY_MAX=8 # Non-negative int/float only, seconds
GENAI_REQUEST_RETRIES = 10 # Non-negative int only

# Duunitori settings
DUUNITORI_MAX_PAGES = 10 # Non-negative int only
DUUNITORI_REQUEST_TIMEOUT = 120 # Non-negative int/float only, seconds
MAX_JOBS_PARSED_DUUNITORI = None # Int if need a limit, else use None

# LinkedIn Settings
MAX_PAGES_LINKEDIN = 10 # Non-negative int only
DUUNITORI_REQUEST_TIMEOUT = 20 # Non-negative int/float only, seconds
MAX_JOBS_PARSED_LINKEDIN = None # Int if need a limit, else use None

# TotalJobs Settings
MAX_PAGES_TOTALJOBS = 10 # Non-negative int only
DUUNITORI_REQUEST_TIMEOUT = 20 # Non-negative int/float only, seconds
MAX_JOBS_PARSED_TOTALJOBS = None # Int if need a limit, else use None

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