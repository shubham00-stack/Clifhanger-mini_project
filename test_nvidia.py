
import os
from dotenv import load_dotenv
from openai import OpenAI, APIStatusError

load_dotenv()

client = OpenAI(
    api_key=os.getenv("NVIDIA_API_KEY"),
    base_url=os.getenv(
        "NVIDIA_BASE_URL",
        "https://integrate.api.nvidia.com/v1"
    )
)

model = os.getenv("MODEL_PRIMARY_NARRATIVE")

print("Testing NVIDIA NIM...")
print("Model:", model)

try:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": "Say hello in one sentence."}
        ],
        max_tokens=100
    )

    print("\nSUCCESS!")
    print(response.choices[0].message.content)

except APIStatusError as e:
    print("\nAPI ERROR:", e.status_code)
    print("ERROR DETAILS:", e.response.text)

except Exception as e:
    print("\nOTHER ERROR:", repr(e))
