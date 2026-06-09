import random

# General settings
GENAI_REQUEST_RETRIES = 10 # Non-negative int only

# Duunitori settings
DUUNITORI_MAX_PAGES = 1 # Non-negative int only
DUUNITORI_REQUEST_TIMEOUT = 120 # Non-negative int/float only, seconds
MAX_JOBS_PARSED_DUUNITORI = 5 # Int if need a limit, else use None
DUUNITORI_REQUEST_DELAY_MIN=3 # Non-negative int/float only, seconds
DUUNITORI_REQUEST_DELAY_MAX=8 # Non-negative int/float only, seconds
DUUNITORI_MAX_WORKERS = 4 # Max asynch connectors to the job board, don't put too high or will get ip banned

# LinkedIn Settings
MAX_PAGES_LINKEDIN = 10 # Non-negative int only
LINKEDIN_REQUEST_TIMEOUT = 20 # Non-negative int/float only, seconds
MAX_JOBS_PARSED_LINKEDIN = None # Int if need a limit, else use None
LINKEDIN_REQUEST_DELAY_MIN=3 # Non-negative int/float only, seconds
LINKEDIN_REQUEST_DELAY_MAX=8 # Non-negative int/float only, seconds
LINKEDIN_MAX_WORKERS = 4 # Max asynch connectors to the job board, don't put too high or will get ip banned

# TotalJobs Settings
MAX_PAGES_TOTALJOBS = 10 # Non-negative int only
TOTALJOBS_REQUEST_TIMEOUT = 20 # Non-negative int/float only, seconds
MAX_JOBS_PARSED_TOTALJOBS = None # Int if need a limit, else use None
TOTALJOBS_REQUEST_DELAY_MIN=3 # Non-negative int/float only, seconds
TOTALJOBS_REQUEST_DELAY_MAX=8 # Non-negative int/float only, seconds
TOTALJOBS_MAX_WORKERS = 4 # Max asynch connectors to the job board, don't put too high or will get ip banned

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

KEYWORD_INSTRUCTION = """You are a CONCISE job listing summarizer. You will be given a job listing summary.
Read it and output exactly 3 keywords that describe the role at a glance.

Rules:
- Output ONLY 3 keywords separated by commas (e.g. Frontend,Remote,Senior).
- Keywords should capture the most salient aspects: role type, seniority, domain, or notable trait.
- No spaces around commas, no punctuation, no explanation, no newlines.
- Any response other than exactly 3 comma-separated keywords is a failure."""

REVALIDATION_INSTRUCTION = """You are a strict response formatter.
You will be given a previous AI response ("PREVIOUS AI RESPONSE") that was supposed to output only an integer from 0 to 100 but failed to comply. You will also be given the previous AI input for context ("PREVIOUS AI INPUT").

Read both, identify the intended numeric score, and output ONLY that integer.

Inference rules (apply in order):
1. If a valid integer 0–100 appears in the response, extract and return it.
2. If a score is described qualitatively (e.g. "strong fit", "poor match"), map it to the nearest reasonable integer.
3. If the response is genuinely ambiguous or contains no extractable signal, return -1.

- ONE integer. No spaces. No punctuation. No explanation. No newlines.
- Any response other than a bare integer in range [0, 100] is a failure."""


# A few headers and a randomizer function to help avoid accidental bot detection when scraping
HEADERS_LIST = [
    # Chrome 124 on Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Sec-CH-UA": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
    },
    # Firefox 125 on Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "TE": "trailers",
    },
    # Chrome 123 on macOS — fixed: standardised to "Not-A.Brand" with v="99"
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-CH-UA": '"Chromium";v="123", "Google Chrome";v="123", "Not-A.Brand";v="99"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"macOS"',
    },
    # Safari 17 on macOS
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4.1 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    },
    # Edge 124 on Windows
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36 Edg/124.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-CH-UA": '"Chromium";v="124", "Microsoft Edge";v="124", "Not-A.Brand";v="99"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
    },
    # Chrome 124 on Android — fixed: added missing "Not-A.Brand" token
    {
        "User-Agent": "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.6367.82 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-CH-UA": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        "Sec-CH-UA-Mobile": "?1",
        "Sec-CH-UA-Platform": '"Android"',
    },
]

def get_random_headers() -> dict:
    return random.choice(HEADERS_LIST).copy()