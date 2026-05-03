import os
from flask import Flask, render_template, request, jsonify
from google import genai as google_genai
from dotenv import load_dotenv

# Load environment variables from .env (safe — .env is gitignored)
load_dotenv()

app = Flask(__name__)

# Gemini client — only active when GEMINI_API_KEY env var is set
_GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Static Dataset
AREA_DATA = {
    "Andhra Pradesh": {
        "Guntur": {"MLA": "Demo MLA (Guntur)", "MP": "Demo MP (Guntur)", "Party": "Demo Party A"},
        "Vijayawada": {"MLA": "Demo MLA (Vijayawada)", "MP": "Demo MP (Vijayawada)", "Party": "Demo Party B"}
    },
    "Telangana": {
        "Hyderabad": {"MLA": "Demo MLA (Hyd)", "MP": "Demo MP (Hyd)", "Party": "Demo Party C"},
        "Warangal": {"MLA": "Demo MLA (War)", "MP": "Demo MP (War)", "Party": "Demo Party D"}
    },
    "Karnataka": {
        "Bengaluru": {"MLA": "Demo MLA (Blr)", "MP": "Demo MP (Blr)", "Party": "Demo Party E"},
        "Mysuru": {"MLA": "Demo MLA (Mys)", "MP": "Demo MP (Mys)", "Party": "Demo Party F"}
    },
    "Tamil Nadu": {
        "Chennai": {"MLA": "Demo MLA (Che)", "MP": "Demo MP (Che)", "Party": "Demo Party G"},
        "Madurai": {"MLA": "Demo MLA (Mad)", "MP": "Demo MP (Mad)", "Party": "Demo Party H"}
    },
    "Maharashtra": {
        "Mumbai": {"MLA": "Demo MLA (Mum)", "MP": "Demo MP (Mum)", "Party": "Demo Party I"},
        "Pune": {"MLA": "Demo MLA (Pun)", "MP": "Demo MP (Pun)", "Party": "Demo Party J"}
    },
    "Kerala": {
        "Kochi": {"MLA": "Demo MLA (Koc)", "MP": "Demo MP (Koc)", "Party": "Demo Party K"},
        "Trivandrum": {"MLA": "Demo MLA (Tri)", "MP": "Demo MP (Tri)", "Party": "Demo Party L"}
    },
    "Gujarat": {
        "Ahmedabad": {"MLA": "Demo MLA (Ahm)", "MP": "Demo MP (Ahm)", "Party": "Demo Party M"},
        "Surat": {"MLA": "Demo MLA (Sur)", "MP": "Demo MP (Sur)", "Party": "Demo Party N"}
    },
    "Rajasthan": {
        "Jaipur": {"MLA": "Demo MLA (Jai)", "MP": "Demo MP (Jai)", "Party": "Demo Party O"},
        "Jodhpur": {"MLA": "Demo MLA (Jod)", "MP": "Demo MP (Jod)", "Party": "Demo Party P"}
    },
    "Uttar Pradesh": {
        "Lucknow": {"MLA": "Demo MLA (Luc)", "MP": "Demo MP (Luc)", "Party": "Demo Party Q"},
        "Kanpur": {"MLA": "Demo MLA (Kan)", "MP": "Demo MP (Kan)", "Party": "Demo Party R"}
    },
    "Delhi": {
        "New Delhi": {"MLA": "Demo MLA (ND)", "MP": "Demo MP (ND)", "Party": "Demo Party S"},
        "South Delhi": {"MLA": "Demo MLA (SD)", "MP": "Demo MP (SD)", "Party": "Demo Party T"}
    }
}

REGISTRATION_DAYS = 5
ELECTION_DAYS_REMAINING = 3

def calculate_timeline_gap(registration_days, election_days_remaining):
    return registration_days - election_days_remaining

def generate_reasons(age, registered, gap, registration_days, election_days_remaining, use_gemini=False):
    if age < 18:
        base_reasons = [
            "You are under 18 years of age.",
            "Legal voting age in India is 18.",
            "You must wait until you are 18 to register."
        ]
    elif registered:
        base_reasons = [
            "You are of legal voting age.",
            "You are already registered to vote.",
            f"You have {election_days_remaining} days left until the election."
        ]
    else:
        if gap > 0:
            base_reasons = [
                f"You need {registration_days} days to complete registration.",
                f"Only {election_days_remaining} days are left before election.",
                f"You are short by {gap} days.",
                f"Because you are not registered and only {election_days_remaining} days remain, you cannot complete registration in time."
            ]
        else:
            base_reasons = [
                f"You need {registration_days} days to complete registration.",
                f"You still have {election_days_remaining} days, so act immediately!"
            ]
            
    if use_gemini and _GEMINI_API_KEY:
        try:
            client = google_genai.Client(api_key=_GEMINI_API_KEY)
            prompt = (
                f"Given these basic reasons why someone can or cannot vote: {base_reasons}. "
                "Generate a more engaging, personalized, and concise 3-bullet-point explanation. "
                "Only return the bullet points separated by newlines (no asterisks, numbers, or extra formatting)."
            )
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            if response.text:
                gemini_reasons = [r.strip().lstrip("-*\u2022 ") for r in response.text.strip().split("\n") if r.strip()]
                if gemini_reasons:
                    return gemini_reasons
        except Exception as e:
            print(f"Gemini API Error (falling back to static reasons): {e}")
            
    return base_reasons

def calculate_voting_status(age, registered, state, district):
    area_info = AREA_DATA.get(state, {}).get(district, {"MLA": "Unknown", "MP": "Unknown", "Party": "Unknown"})
    
    gap = calculate_timeline_gap(REGISTRATION_DAYS, ELECTION_DAYS_REMAINING)
    
    result = {
        "verdict": "",
        "verdict_class": "",
        "tag": "",
        "tag_class": "",
        "reasons": [],
        "timeline_mismatch": False,
        "is_ready": False,
        "registration_days": REGISTRATION_DAYS,
        "election_days_remaining": ELECTION_DAYS_REMAINING,
        "gap": gap,
        "area_info": {
            "State": state,
            "District": district,
            **area_info
        }
    }
    
    if age < 18:
        result["verdict"] = "❌ You Are Not Eligible to Vote"
        result["verdict_class"] = "red"
        result["tag"] = "❌ Not Eligible"
        result["tag_class"] = "tag-red"
        result["timeline_mismatch"] = False
        result["is_ready"] = False
    elif registered:
        result["verdict"] = "✅ You Can Vote"
        result["verdict_class"] = "green"
        result["tag"] = "✅ Ready Voter"
        result["tag_class"] = "tag-green"
        result["timeline_mismatch"] = False
        result["is_ready"] = True
    else:
        if gap > 0:
            result["verdict"] = "❌ You Will Likely Miss This Election"
            result["verdict_class"] = "red"
            result["tag"] = "⚠️ At Risk"
            result["tag_class"] = "tag-red"
            result["timeline_mismatch"] = True
            result["is_ready"] = False
        else:
            # Fallback if constants change
            result["verdict"] = "⚠️ You Can Vote If You Act Now"
            result["verdict_class"] = "orange"
            result["tag"] = "⚠️ Action Needed"
            result["tag_class"] = "tag-orange"
            result["timeline_mismatch"] = False
            result["is_ready"] = False
            
    # Use Gemini only when the API key environment variable is set
    use_gemini = bool(_GEMINI_API_KEY)
    result["reasons"] = generate_reasons(age, registered, gap, REGISTRATION_DAYS, ELECTION_DAYS_REMAINING, use_gemini)
            
    return result

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        try:
            state = request.form.get("state", "").strip()
            district = request.form.get("district", "").strip()
            age_str = request.form.get("age", "0").strip()
            registered = request.form.get("registered") == "yes"
            
            if not age_str.isdigit():
                raise ValueError("Age must be a valid number.")
            age = int(age_str)
            
            if age < 0 or age > 120:
                raise ValueError("Age must be between 0 and 120.")
                
            if state not in AREA_DATA:
                raise ValueError("Please select a valid state.")
                
            if district not in AREA_DATA.get(state, {}):
                raise ValueError("Please select a valid district.")
                
            result = calculate_voting_status(age, registered, state, district)
        except ValueError as ve:
            error = str(ve)
        except Exception as e:
            print(f"Error processing request: {e}")
            error = "Something went wrong. Please try again."
        
    states = list(AREA_DATA.keys())
    return render_template("index.html", result=result, states=states, error=error)

@app.route("/api/districts/<state>")
def get_districts(state):
    districts = list(AREA_DATA.get(state, {}).keys())
    return jsonify({"districts": districts})

if __name__ == "__main__":
    app.run(debug=False, port=5001)
