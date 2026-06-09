from google import genai
from app.__init__ import client
import os
import time
from app.constants import *
import mimetypes
import functools
import json

def filter_with_ai(all_job_details: list) -> list:
    filtered_jobs = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "resources", "cv", "CVForGemini.pdf")
    uploaded_file = upload_file(file_path, current_dir)

    for job in all_job_details:
        print("Evaluating link: ", job["link"])
        job_summary = search_summarise(job["text"], uploaded_file)
        if job_summary == "Error 503: Gemini server busy.":
            job["score"] = -1
            filtered_jobs.append(job)
            pass
        verdict = re_evaluate(job_summary).strip()
        job["keywords"] = [word.capitalize() for word in generate_keywords(job_summary)]
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


def search_summarise(description: str, uploaded_file: genai.types.File) -> str:
    response = _generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=["CANDIDATE'S CV:", uploaded_file, f"\nJOB DESCRIPTION: {description}"],
        config=genai.types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=SEARCH_INSTRUCTION,
        )
    )
    print("Evaluating summary: ", response.text)
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


def generate_keywords(summary: str) -> str:
    keyword_schema = genai.types.Schema(
        type=genai.types.Type.OBJECT,
        properties={
            "keywords": genai.types.Schema(
                type=genai.types.Type.ARRAY,
                items=genai.types.Schema(type=genai.types.Type.STRING),
                min_items=3,
                max_items=3,
            )
        },
        required=["keywords"],
    )

    response = _generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=["Job listing: " + str(summary)],
        config=genai.types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=KEYWORD_INSTRUCTION,
            response_mime_type="application/json",
            response_schema=keyword_schema,
        )
    )
    keywords = json.loads(response.text)["keywords"]
    return keywords


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