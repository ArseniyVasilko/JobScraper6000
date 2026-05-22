from google import genai
from app.__init__ import client
import os
import time
from app.constants import SEARCH_INSTRUCTION, CLASSIFY_INSTRUCTION, REVALIDATION_INSTRUCTION
import mimetypes

def filter_with_ai(all_job_links: list) -> list:
    filtered_links = []
    discarded_links = []
    failed_evaluations = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "..", "resources", "cv", "CVForGemini.pdf")
    uploaded_file = upload_file(file_path, current_dir)

    for link in all_job_links:
        job_summary = search_summarise(link, uploaded_file)
        verdict = classify(job_summary).strip().lower()
        if verdict != "a" and verdict != "b":
            print("AI model provided unstandardised response - attempting to extract meaning")
            verdict = re_evaluate(verdict).strip().lower()
        if verdict == "a":
            filtered_links.append(link)
            print("Job passes evaluation")
        elif verdict == "b":
            discarded_links.append(link)
            print("Job does not pass evaluation")
        else:
            failed_evaluations.append(link)
            print("AI failed to give standardised answer after re-evaluation, given response: " + verdict)
    return {"filtered_links": filtered_links,
            "discarded_links": discarded_links,
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


def search_summarise(link: str, uploaded_file: genai.types.File) -> str:
    print("Evaluating link: ", link)
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
    print("Job AI summary: " + response.text)
    return response.text


def classify(summary: str) -> str:
    response = client.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=["Candidate's structured evaluation: " + summary],
        config=genai.types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=CLASSIFY_INSTRUCTION,
        )
    )
    return response.text


def re_evaluate(verdict: str) -> str:
    response = client.models.generate_content(
        model="models/gemini-2.5-flash-lite",
        contents=["Previous AI response: " + verdict],
        config=genai.types.GenerateContentConfig(
            temperature=0.0,
            system_instruction=REVALIDATION_INSTRUCTION
        )
    )
    return response.text



