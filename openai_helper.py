import os
import openai
from dotenv import load_dotenv
from functools import lru_cache

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

@lru_cache(maxsize=1000)
def get_timezone_from_segment(segment: str) -> str:
    """
    Uses OpenAI to determine the standard IANA timezone string from a rough segment (location) string.
    Returns the timezone string (e.g., 'Europe/London') or 'UTC' as a fallback.
    """
    if not segment or segment.strip().lower() in ['none', 'null', 'na', '']:
        return "UTC"

    prompt = (
        f"You are a timezone extraction tool. Convert the following location/segment into a standard IANA timezone string "
        f"(e.g., 'America/Los_Angeles', 'Europe/London', 'Asia/Kolkata').\n"
        f"If the location is broad (like 'APAC' or 'EMEA'), pick a representative timezone (like 'Asia/Singapore' or 'Europe/Paris').\n"
        f"If you are unsure, default to 'UTC'.\n"
        f"Output ONLY the timezone string, nothing else.\n\n"
        f"Location: '{segment}'\n"
        f"Timezone:"
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=15,
            temperature=0
        )
        tz = response.choices[0].message.content.strip()
        # Basic validation (could be improved by checking against pytz.all_timezones)
        if "/" in tz or tz == "UTC":
            return tz
        return "UTC"
    except Exception as e:
        print(f"Error getting timezone: {e}")
        return "UTC"
