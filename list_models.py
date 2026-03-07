from dotenv import load_dotenv
import os
load_dotenv()
from google import genai
client = genai.Client()
print('Listing models:')
for m in client.models.list():
    print(m.name)