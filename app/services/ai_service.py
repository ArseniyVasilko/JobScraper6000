from google import genai
from app.__init__ import client
import os
import time
from app.constants import SEARCH_INSTRUCTION, CLASSIFY_INSTRUCTION, REVALIDATION_INSTRUCTION, GENAI_REQUEST_RETRIES
import mimetypes

def filter_with_ai(all_job_details: list) -> list:
    filtered_jobs = []
    discarded_jobs = []
    failed_evaluations = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "resources", "cv", "CVForGemini.pdf")
    uploaded_file = upload_file(file_path, current_dir)

    for job in all_job_details:
        job_summary = search_summarise(job["link"], uploaded_file)
        if job_summary == "Error 503: Gemini server busy.":
            failed_evaluations.append(job)
            pass
        verdict = classify(job_summary).strip().lower()
        if verdict != "a" and verdict != "b":
            print("AI model provided unstandardised response - attempting to extract meaning")
            verdict = re_evaluate(verdict).strip().lower()
        if verdict == "a":
            filtered_jobs.append(job)
            print("Job passes evaluation")
        elif verdict == "b":
            discarded_jobs.append(job)
            print("Job does not pass evaluation")
        else:
            failed_evaluations.append(job)
            print("AI failed to give standardised answer after re-evaluation, given response: " + verdict)
    return {"filtered_jobs": filtered_jobs,
            "discarded_jobs": discarded_jobs,
            "failed_evaluations": failed_evaluations}


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

def search_summarise(link: str, uploaded_file: genai.types.File) -> str:
    print("Evaluating link: ", link)
    response = ErrorResponse()

    # Retries to get response from Genai X times before defaulting to response above
    for _ in range(GENAI_REQUEST_RETRIES):
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash-lite",
                contents=[uploaded_file, f"\nJob listing link: {link}"],
                config=genai.types.GenerateContentConfig(
                    temperature=0.0,
                    # Enables Google Search to look up the URL
                    tools=[genai.types.Tool(google_search=genai.types.GoogleSearch())],
                    system_instruction=SEARCH_INSTRUCTION,
                )
            )
            break
        except genai.errors.ServerError:
            print("Genai server error - retrying...")
            pass
    print("Job AI summary: " + str(response.text))
    return response.text


def classify(summary: str) -> str:
    response = ErrorResponse()

    # Retries to get response from Genai x times before defaulting to response above
    for _ in range(GENAI_REQUEST_RETRIES):
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash-lite",
                contents=["Candidate's structured evaluation: " + str(summary)],
                config=genai.types.GenerateContentConfig(
                    temperature=0.0,
                    system_instruction=CLASSIFY_INSTRUCTION,
                )
            )
            break
        except genai.errors.ServerError:
            print("Genai server error - retrying...")
            pass
    return response.text


def re_evaluate(verdict: str) -> str:
    response = ErrorResponse()

    # Retries to get response from Genai x times before defaulting to response above
    for _ in range(GENAI_REQUEST_RETRIES):
        try:
            response = client.models.generate_content(
                model="models/gemini-2.5-flash-lite",
                contents=["Previous AI response: " + str(verdict)],
                config=genai.types.GenerateContentConfig(
                    temperature=0.0,
                    system_instruction=REVALIDATION_INSTRUCTION
                )
            )
        except genai.errors.ServerError:
            print("Genai server error - retrying...")
            pass
    return response.text



