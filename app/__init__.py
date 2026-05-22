from flask import Flask
from app.config import Config
import os
from google import genai
from dotenv import load_dotenv

#Loads environment variables
load_dotenv()

#Flask setup and config
app = Flask(__name__)
app.config.from_object(Config)
print("config updated")

#Google genai setup and config
MODEL = "gemini-2.5-flash-lite"
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
print("genai client loaded with API key " + os.getenv("GOOGLE_API_KEY"))

from app import routes
