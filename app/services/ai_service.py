from google import genai
from app.__init__ import client
import os
import time
from app.constants import SEARCH_INSTRUCTION, CLASSIFY_INSTRUCTION, REVALIDATION_INSTRUCTION, GENAI_REQUEST_RETRIES
import mimetypes
import functools

def filter_with_ai(all_job_details: list) -> list:
    filtered_jobs = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "resources", "cv", "CVForGemini.pdf")
    uploaded_file = upload_file(file_path, current_dir)

    for job in all_job_details:
        job_summary = search_summarise(job["link"], uploaded_file)
        if job_summary == "Error 503: Gemini server busy.":
            job["score"] = -1
            filtered_jobs.append(job)
            pass
        verdict = re_evaluate(job_summary).strip()
        if not verdict.isdigit() or not (0 <= int(verdict) <= 100):
            print("AI model provided unstandardised response - attempting to extract meaning")
            verdict = re_evaluate(verdict).strip()
        if 0 <= int(verdict) <= 100:
            job["score"] = int(verdict)
            filtered_jobs.append(job)
            print("Job evaluation score: " + str(job["score"]))
        else:
            print("AI failed to give standardised answer after re-evaluation, given response: " + verdict)
            job["score"] = -1
            filtered_jobs.append(job)
    return filtered_jobs


def upload_file(file_path: str, current_dir: str) -> genai.types.File:
    # Guess the mime type based on the file extension
    mime_type, _ = mimetypes.guess_type(file_path)
    # Fallback to binary stream if type is unknown
    if mime_type is None:
        mime_type = "application/octet-stream"
    print(f"Uploading file ({mime_type}) to AI service")
    uploaded_file = client.files.upload(
        file=file_path,
        config=genai.types.UploadFileConfig(mime_type=mime_type)
    )
    print("Processing File...")
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(2)
        uploaded_file = client.files.get(name=uploaded_file.name)
    if uploaded_file.state.name == "FAILED":
        raise ValueError(f"File processing failed: {uploaded_file.error.message}")
    return uploaded_file

# Dummy class for replacing response.text below if genai fails to provide a response
class ErrorResponse:
    text = "Error 503: Gemini server busy."

# Decorator shortcut to retry X denied AI server requests
def retry_on_server_error(retries: int = GENAI_REQUEST_RETRIES):
    """Retries the wrapped function on genai.errors.ServerError, returns None after all retries exhausted."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for _ in range(retries):
                try:
                    return func(*args, **kwargs)
                except genai.errors.ServerError:
                    print("Genai server error - retrying...")
            return ErrorResponse
        return wrapper
    return decorator

@retry_on_server_error()
def _generate_content(*args, **kwargs):
    return client.models.generate_content(*args, **kwargs)


def search_summarise(link: str, uploaded_file: genai.types.File) -> str:
    print("Evaluating link: ", link)
    response = _generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=[uploaded_file, f"\nJob listing link: {link}"],
        config=genai.types.GenerateContentConfig(
            temperature=0.0,
            # Enables Google Search to look up the URL
            tools=[genai.types.Tool(google_search=genai.types.GoogleSearch())],
            system_instruction=SEARCH_INSTRUCTION,
        )
    )
    return response.text


def classify(summary: str) -> str:
    response = _generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=["Candidate's structured evaluation: " + str(summary)],
        config=genai.types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=CLASSIFY_INSTRUCTION,
        )
    )
    return response.text


def re_evaluate(verdict: str) -> str:
    response = _generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=["Previous AI response: " + str(verdict)],
        config=genai.types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=REVALIDATION_INSTRUCTION
        )
    )
    return response.text