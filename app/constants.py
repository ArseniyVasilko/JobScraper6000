# General settings
REQUEST_DELAY_MIN=3 # Non-negative int/float only, seconds
REQUEST_DELAY_MAX=8 # Non-negative int/float only, seconds
GENAI_REQUEST_RETRIES = 10 # Non-negative int only

# Duunitori settings
DUUNITORI_MAX_PAGES = 1 # Non-negative int only
DUUNITORI_REQUEST_TIMEOUT = 120 # Non-negative int/float only, seconds
MAX_JOBS_PARSED_DUUNITORI = 5 # Int if need a limit, else use None

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
You will be given a job description and a candidate's CV.

Produce a structured evaluation with the following sections:

ROLE: One line — job title, company, and industry.
REQUIREMENTS: Extract and list only the qualifications, skills, and experience explicitly stated or directly implied by the job description. Do not add, infer, or invent requirements that are not grounded in the job description text itself.
CANDIDATE FIT: For each requirement listed above, explicitly state whether the candidate MEETS, PARTIALLY MEETS, or LACKS it. Cite specific evidence from the CV. If evidence is absent, mark as LACKS.
VERDICT: A single concluding sentence summarising overall suitability. Be direct and unambiguous.

Keep the total response under 1000 words. Be concise throughout. Do not invent or assume any information not present in the provided job description or CV.
"""

CLASSIFY_INSTRUCTION = """You are a strict numeric scorer. You will be given a structured evaluation of a candidate against a job listing.
Read the evaluation — paying particular attention to the CANDIDATE FIT and VERDICT sections — and output a single integer score from 0 to 100, where:
0 = completely unfit (no relevant skills, experience, or alignment with the role)
100 = perfect match (all requirements met, ideal background and profile)

Rules:
- Output ONLY a single integer between 0 and 100 (inclusive).
- No spaces, punctuation, explanation, or newlines.
- Any response other than a bare integer in range [0, 100] is a failure."""

REVALIDATION_INSTRUCTION = """You are a strict response formatter.
You will be given a previous AI response ("PREVIOUS AI RESPONSE") that was supposed to output only an integer from 0 to 100 but failed to comply. You will also be given the previous AI input for context ("PREVIOUS AI INPUT").

Read both, identify the intended numeric score, and output ONLY that integer.

Inference rules (apply in order):
1. If a valid integer 0–100 appears in the response, extract and return it.
2. If a score is described qualitatively (e.g. "strong fit", "poor match"), map it to the nearest reasonable integer.
3. If the response is genuinely ambiguous or contains no extractable signal, return -1.

- ONE integer. No spaces. No punctuation. No explanation. No newlines.
- Any response other than a bare integer in range [0, 100] is a failure."""