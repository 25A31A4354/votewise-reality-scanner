from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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

def calculate_status(age, registered, state, district):
    area_info = AREA_DATA.get(state, {}).get(district, {"MLA": "Unknown", "MP": "Unknown", "Party": "Unknown"})
    
    gap = REGISTRATION_DAYS - ELECTION_DAYS_REMAINING
    
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
        result["reasons"] = [
            "You are under 18 years of age.",
            "Legal voting age in India is 18.",
            "You must wait until you are 18 to register."
        ]
        result["timeline_mismatch"] = False
        result["is_ready"] = False
    elif registered:
        result["verdict"] = "✅ You Can Vote"
        result["verdict_class"] = "green"
        result["tag"] = "✅ Ready Voter"
        result["tag_class"] = "tag-green"
        result["reasons"] = [
            "You are of legal voting age.",
            "You are already registered to vote.",
            f"You have {ELECTION_DAYS_REMAINING} days left until the election."
        ]
        result["timeline_mismatch"] = False
        result["is_ready"] = True
    else:
        if gap > 0:
            result["verdict"] = "❌ You Will Likely Miss This Election"
            result["verdict_class"] = "red"
            result["tag"] = "⚠️ At Risk"
            result["tag_class"] = "tag-red"
            result["reasons"] = [
                f"You need {REGISTRATION_DAYS} days to complete registration.",
                f"Only {ELECTION_DAYS_REMAINING} days are left before election.",
                f"You are short by {gap} days.",
                f"Because you are not registered and only {ELECTION_DAYS_REMAINING} days remain, you cannot complete registration in time."
            ]
            result["timeline_mismatch"] = True
            result["is_ready"] = False
        else:
            # Fallback if constants change
            result["verdict"] = "⚠️ You Can Vote If You Act Now"
            result["verdict_class"] = "orange"
            result["tag"] = "⚠️ Action Needed"
            result["tag_class"] = "tag-orange"
            result["reasons"] = [
                f"You need {REGISTRATION_DAYS} days to complete registration.",
                f"You still have {ELECTION_DAYS_REMAINING} days, so act immediately!"
            ]
            result["timeline_mismatch"] = False
            result["is_ready"] = False
            
    return result

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        state = request.form.get("state", "")
        district = request.form.get("district", "")
        age = int(request.form.get("age", 0))
        registered = request.form.get("registered") == "yes"
        
        result = calculate_status(age, registered, state, district)
        
    states = list(AREA_DATA.keys())
    return render_template("index.html", result=result, states=states)

@app.route("/api/districts/<state>")
def get_districts(state):
    districts = list(AREA_DATA.get(state, {}).keys())
    return jsonify({"districts": districts})

if __name__ == "__main__":
    app.run(debug=True, port=5001)
