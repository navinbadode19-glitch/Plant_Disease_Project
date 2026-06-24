from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from flask import send_from_directory
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import json
import base64
from disease_info import disease_info
from recommendation_engine import generate_recommendation
import database
import translations

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    _env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    load_dotenv(dotenv_path=_env_path, override=True)
except ImportError:
    pass  # dotenv not installed yet

# Initialize Database
database.init_db()

# ── Initialize Groq AI (free, fast, multilingual) ────────────────────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
groq_client = None

_GROQ_KEY_VALID = (
    bool(GROQ_API_KEY)
    and GROQ_API_KEY != "your_groq_api_key_here"
    and len(GROQ_API_KEY) > 20
)

if _GROQ_KEY_VALID:
    try:
        from groq import Groq
        groq_client = Groq(api_key=GROQ_API_KEY)
        print("[AgriBot] Groq AI initialized successfully!")
    except Exception as e:
        print(f"[AgriBot] WARNING: Groq AI not initialized: {e}")
        groq_client = None
else:
    print("[AgriBot] WARNING: No valid GROQ_API_KEY in .env. Get a free key at https://console.groq.com")

AGRIBOT_SYSTEM_PROMPT = (
    "You are AgriBot, an expert agricultural advisor and plant pathologist with 30+ years of experience. "
    "You help farmers diagnose crop diseases, recommend treatments, and give practical farming advice. "
    "Always respond in the SAME LANGUAGE the user writes in or has set as their preference. "
    "If the user writes in Hindi, respond entirely in Hindi. If Tamil, respond in Tamil, etc. "
    "Keep answers clear, practical, and farmer-friendly - avoid overly technical jargon. "
    "When discussing treatments, mention both chemical and organic options. "
    "Be compassionate and encouraging - farming is hard work. "
    "If you receive crop disease context, use it to give more specific and relevant advice. "
    "Always end with a short encouraging line for the farmer."
)


app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "agri_guard_super_secret_key_123!")

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load Tensorflow model
model = tf.keras.models.load_model("plant_disease_model.keras")

with open("class_names.txt", "r") as f:
    class_names = [line.strip() for line in f.readlines()]


def predict_image(image_path):
    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))

    img_array = np.array(img)
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array, verbose=0)

    predicted_class = class_names[np.argmax(prediction)]
    confidence = float(np.max(prediction)) * 100

    return predicted_class, confidence


def analyze_image_vision(filepath, crop_type=None, language="English"):
    """Diagnose crop disease or pest using Groq Llama 4 Vision Model."""
    if not groq_client:
        return None
    try:
        with open(filepath, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
            
        crop_context = f"The crop type is selected as: {crop_type}. " if crop_type and crop_type != "Universal" else ""
        prompt = (
            "You are a professional plant pathologist and entomologist. "
            f"{crop_context}Identify the plant crop/species and the plant disease or pest visible in the image. "
            f"You MUST translate all dynamic descriptive values directly in the user's preferred language: {language}. "
            "Return a JSON object with the following keys:\n"
            "- 'crop': The common English name of the crop/plant identified in the image (e.g. 'Tomato', 'Potato', 'Pepper', 'Rice', 'Wheat', 'Maize', 'Cotton', 'Apple', 'Grape', 'Citrus', 'Mango', 'Sugarcane', 'Coffee_Tea', or other if unknown). This must be the simple English name of the crop/plant (not the disease/pest, and formatted matching one of these capitalization options if applicable).\n"
            "- 'name': The name of the disease or pest (translated in the user's language, e.g. 'टमाटर मकड़ी घुन' for Hindi).\n"
            "- 'symptoms': A brief description of signs/symptoms in the user's language.\n"
            "- 'cause': The biological organism or condition causing the issue in the user's language.\n"
            "- 'severity': One of 'High', 'Medium', or 'Low'. (Keep this English string: 'High', 'Medium', or 'Low').\n"
            "- 'chemical_treatment': Chemical recommendation in the user's language.\n"
            "- 'dosage': Application dosage in the user's language.\n"
            "- 'spray_interval': Recommendation interval in the user's language.\n"
            "- 'organic_treatment': Organic recommendation in the user's language.\n"
            "- 'recovery_time': Estimated recovery timeline in the user's language.\n"
            "- 'prevention': Preventive advice in the user's language.\n"
            "- 'urgency': One of 'Critical', 'Monitor Closely', or 'Routine'. (Keep this English string).\n"
            "- 'action': Short recommendation action in the user's language.\n"
            "- 'crop_loss': Estimated crop loss in the user's language (e.g. '15-25%').\n"
            "- 'timeline': A JSON array of 4 string steps written in the user's language.\n"
            "Provide clear, accurate, and concise information. If the plant looks completely healthy, "
            "set 'name' to 'Healthy' (or user language equivalent) and populate the treatments and recommendations as maintenance steps."
        )

        completion = groq_client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        result_text = completion.choices[0].message.content
        return json.loads(result_text)
    except Exception as e:
        print(f"[AgriBot] Groq Vision Error: {e}")
        return None


# ── Authentication and Authorization ────────────────────────
@app.before_request
def require_login():
    # Allow debugger pages/resources
    if '__debugger__' in request.args or 'content-type' in request.headers and 'debugger' in request.headers.get('content-type', ''):
        return
    if request.path.startswith('/_debug_toolbar/') or request.path == '/favicon.ico':
        return
        
    # Allow static resources and uploads directly
    if request.path.startswith('/static/') or request.path.startswith('/uploads/'):
        return

    allowed_routes = ['login', 'register', 'uploaded_file']
    if not request.endpoint:
        return  # Let 404 handler or other routing proceed without redirect loop
        
    if request.endpoint not in allowed_routes:
        if 'user_id' not in session:
            return redirect(url_for('login'))

@app.context_processor
def inject_translations():
    def translate_helper(text):
        lang = session.get('lang', 'English')
        return translations.translate_text(text, lang)
    return dict(_=translate_helper, current_lang=session.get('lang', 'English'))


@app.route("/login", methods=["GET", "POST"])
def login():
    if 'user_id' in session:
        return redirect(url_for('home'))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        
        user = database.login_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['lang'] = user['language']
            flash("Welcome back, Farmer!", "success")
            return redirect(url_for('home'))
        else:
            flash("Invalid username or password.", "error")
            return redirect(url_for('login'))
            
    return render_template("login.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "").strip()
    preferred_lang = request.form.get("preferred_lang", "English").strip()
    
    if not username or not password:
        flash("Username and password are required.", "error")
        return redirect(url_for('login', mode='register'))
        
    res = database.register_user(username, password, preferred_lang)
    if res["success"]:
        flash("Account created successfully! Please log in.", "success")
        return redirect(url_for('login'))
    else:
        flash(res["message"], "error")
        return redirect(url_for('login', mode='register'))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for('login'))

@app.route("/set_language", methods=["POST"])
def set_language():
    data = request.get_json() or {}
    lang = data.get("language", "English").strip()
    user_id = session.get('user_id')
    if user_id:
        database.update_user_language(user_id, lang)
        session['lang'] = lang
        return jsonify({"success": True, "language": lang})
    return jsonify({"success": False, "message": "Session expired."}), 401


# ── Main Routes ─────────────────────────────────────────────
@app.route("/")
def home():
    user_id = session.get('user_id')
    user_history = []
    if user_id:
        user_history = database.get_user_history(user_id)
    return render_template("index.html", history=user_history)

@app.route("/history/<int:record_id>")
def view_history_record(record_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM history WHERE id = ? AND user_id = ?', (record_id, user_id))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        flash("Record not found or access denied.", "error")
        return redirect(url_for('home'))
        
    disease = row["disease_name"].lower().replace(" ", "_")
    confidence = row["confidence"]
    image_url = row["image_path"]
    disease_name = row["disease_name"]
    symptoms = row["symptoms"]
    cause = row["cause"]
    severity = row["severity"]
    chemical_treatment = row["chemical_treatment"]
    dosage = "N/A"
    spray_interval = "N/A"
    organic_treatment = row["organic_treatment"]
    recovery_time = row["recovery_time"]
    prevention = row["prevention"]
    
    urgency = "Monitor Closely"
    if severity == "High":
        urgency = "Immediate Action Required"
    elif severity == "Low":
        urgency = "Preventive Action"
        
    action = "Inspect crops regularly."
    crop_loss = "Unknown"
    if severity == "High":
        crop_loss = "30-70%"
    elif severity == "Medium":
        crop_loss = "10-30%"
    elif severity == "Low":
        crop_loss = "0-10%"
        
    from recommendation_engine import generate_timeline
    timeline = generate_timeline(severity)
    confidence_note = "Diagnosis retrieved from history."
    
    return render_template(
        "result.html",
        crop_type=row["crop_type"],
        disease=disease,
        disease_name=disease_name,
        confidence=round(confidence, 2),
        image_path=image_url,
        symptoms=symptoms,
        cause=cause,
        severity=severity,
        chemical_treatment=chemical_treatment,
        dosage=dosage,
        spray_interval=spray_interval,
        organic_treatment=organic_treatment,
        recovery_time=recovery_time,
        prevention=prevention,
        urgency=urgency,
        action=action,
        confidence_note=confidence_note,
        crop_loss=crop_loss,
        timeline=timeline
    )

@app.route("/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return "No file uploaded"

    file = request.files["image"]
    if file.filename == "":
        return "No selected file"

    filepath = os.path.join(
        app.config["UPLOAD_FOLDER"],
        file.filename
    )
    file.save(filepath)

    analysis_mode = request.form.get("analysis_mode", "disease")
    crop_type = request.form.get("crop_type", "Universal")
    scanner_engine = request.form.get("scanner_engine", "auto")

    local_supported_crops = {"Tomato", "Potato", "Pepper"}
    use_ai_vision = False

    if groq_client:
        if scanner_engine == "ai_vision":
            use_ai_vision = True
        elif analysis_mode in ["pest", "advanced"]:
            use_ai_vision = True
        elif crop_type not in local_supported_crops:
            use_ai_vision = True

    user_lang = session.get('lang', 'English')
    vision_result = None
    if use_ai_vision:
        print(f"[AgriBot] Invoking Groq Llama 4 Vision diagnostic (Crop: {crop_type}, Language: {user_lang})...")
        vision_result = analyze_image_vision(filepath, crop_type=crop_type, language=user_lang)

    if vision_result:
        # Auto-detect crop name from the vision analysis response
        detected_crop = vision_result.get("crop", "").strip()
        if detected_crop:
            if detected_crop.lower() in ["coffee", "tea", "coffee_tea", "coffee/tea"]:
                crop_type = "Coffee_Tea"
            elif detected_crop.lower() in ["pepper", "bell pepper", "bell_pepper", "pepper (bell)"]:
                crop_type = "Pepper"
            else:
                crop_type = detected_crop.capitalize()

        disease_name = vision_result.get("name", "Detected Pest/Disease")
        disease = disease_name.lower().replace(" ", "_")
        confidence = 98.50  # Vision model high-confidence rating
        symptoms = vision_result.get("symptoms", "No symptom details available.")
        cause = vision_result.get("cause", "Unknown insect or pathogen.")
        severity = vision_result.get("severity", "Medium")
        chemical_treatment = vision_result.get("chemical_treatment", "None recommended.")
        dosage = vision_result.get("dosage", "N/A")
        spray_interval = vision_result.get("spray_interval", "N/A")
        organic_treatment = vision_result.get("organic_treatment", "None recommended.")
        recovery_time = vision_result.get("recovery_time", "N/A")
        prevention = vision_result.get("prevention", "No prevention info available.")
        urgency = vision_result.get("urgency", "Monitor Closely")
        action = vision_result.get("action", "Inspect crops regularly.")
        crop_loss = vision_result.get("crop_loss", "N/A")
        timeline = vision_result.get("timeline", ["Day 1 - Begin treatment", "Day 7 - Check spread", "Day 14 - Reinspect crop", "Day 21 - Expected recovery"])
        confidence_note = "Diagnosis generated dynamically using Llama Vision AI."
    else:
        disease, confidence = predict_image(filepath)
        # Auto-detect crop name from the CNN class name prefix
        if disease.lower().startswith("tomato"):
            crop_type = "Tomato"
        elif disease.lower().startswith("potato"):
            crop_type = "Potato"
        elif disease.lower().startswith("pepper") or disease.lower().startswith("bell_pepper"):
            crop_type = "Pepper"

        info = disease_info.get(
            disease,
            {
                "symptoms": "No information available",
                "cause": "No information available",
                "severity": "Unknown",
                "chemical_treatment": "No recommendation available",
                "dosage": "N/A",
                "spray_interval": "N/A",
                "organic_treatment": "N/A",
                "recovery_time": "N/A",
                "prevention": "No information available"
            }
        )
        recommendation = generate_recommendation(
            disease,
            info["severity"],
            confidence
        )
        disease_name = info.get("name", disease.replace("_", " "))
        
        # Translate localized model output properties using translations dictionary
        disease_name = translations.translate_text(disease_name, user_lang)
        symptoms = translations.translate_text(info["symptoms"], user_lang)
        cause = translations.translate_text(info["cause"], user_lang)
        severity = translations.translate_text(info["severity"], user_lang)
        chemical_treatment = translations.translate_text(info["chemical_treatment"], user_lang)
        dosage = translations.translate_text(info["dosage"], user_lang)
        spray_interval = translations.translate_text(info["spray_interval"], user_lang)
        organic_treatment = translations.translate_text(info["organic_treatment"], user_lang)
        recovery_time = translations.translate_text(info["recovery_time"], user_lang)
        prevention = translations.translate_text(info["prevention"], user_lang)
        urgency = translations.translate_text(recommendation["urgency"], user_lang)
        action = translations.translate_text(recommendation["action"], user_lang)
        crop_loss = translations.translate_text(recommendation["crop_loss"], user_lang)
        timeline = [translations.translate_text(step, user_lang) for step in recommendation["timeline"]]
        confidence_note = translations.translate_text(recommendation["confidence_note"], user_lang)

    # Use clean forward-slash URL for browser rendering
    image_url = f"/uploads/{file.filename}"

    # Log details to user scan history in database
    user_id = session.get('user_id')
    if user_id:
        database.add_history_record(
            user_id=user_id,
            crop_type=crop_type,
            disease_name=disease_name,
            severity=severity,
            confidence=round(confidence, 2),
            image_path=image_url,
            symptoms=symptoms,
            cause=cause,
            chemical_treatment=chemical_treatment,
            organic_treatment=organic_treatment,
            recovery_time=recovery_time,
            prevention=prevention
        )

    return render_template(
        "result.html",
        crop_type=crop_type,
        disease=disease,
        disease_name=disease_name,
        confidence=round(confidence, 2),
        image_path=image_url,
        symptoms=symptoms,
        cause=cause,
        severity=severity,
        chemical_treatment=chemical_treatment,
        dosage=dosage,
        spray_interval=spray_interval,
        organic_treatment=organic_treatment,
        recovery_time=recovery_time,
        prevention=prevention,
        urgency=urgency,
        action=action,
        confidence_note=confidence_note,
        crop_loss=crop_loss,
        timeline=timeline
    )

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )

@app.route('/chat', methods=['POST'])
def chat():
    """AI-powered multilingual farmer support chatbot endpoint (powered by Groq)."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    user_message = data.get("message", "").strip()
    language = data.get("language", session.get('lang', 'English'))
    context = data.get("context", {})

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    if not groq_client:
        return jsonify({
            "reply": (
                "AgriBot is not configured yet. "
                "Please add your free Groq API key to the .env file as GROQ_API_KEY. "
                "Get your free key at: https://console.groq.com"
            )
        }), 200

    # Build contextual prompt with disease context if available
    context_block = ""
    if context.get("disease_name"):
        context_block = (
            f"\n[CROP ANALYSIS CONTEXT]\n"
            f"Detected Disease: {context.get('disease_name', 'Unknown')}\n"
            f"Severity: {context.get('severity', 'Unknown')}\n"
            f"Confidence: {context.get('confidence', 'Unknown')}%\n"
            f"Symptoms: {context.get('symptoms', '')}\n"
            f"Cause: {context.get('cause', '')}\n"
            f"Chemical Treatment: {context.get('chemical_treatment', '')}\n"
            f"Organic Treatment: {context.get('organic_treatment', '')}\n"
            f"Prevention: {context.get('prevention', '')}\n"
            f"[END CONTEXT]\n"
        )

    user_prompt = (
        f"Farmer is communicating in: {language}. "
        f"Please respond entirely in {language}."
        f"{context_block}\n"
        f"Farmer's question: {user_message}"
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": AGRIBOT_SYSTEM_PROMPT},
                {"role": "user",   "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        reply = completion.choices[0].message.content
        return jsonify({"reply": reply})
    except Exception as e:
        error_str = str(e)
        if "401" in error_str or "invalid_api_key" in error_str.lower() or "auth" in error_str.lower():
            user_msg = "Invalid Groq API key. Please check GROQ_API_KEY in .env and restart."
        elif "429" in error_str or "rate_limit" in error_str.lower():
            user_msg = "Too many requests. Please wait a moment and try again."
        elif "503" in error_str or "unavailable" in error_str.lower():
            user_msg = "Groq service is temporarily busy. Please try again in a few seconds."
        else:
            user_msg = f"AI error: {error_str}"
        print(f"[AgriBot] Groq API error: {error_str}")
        return jsonify({"reply": user_msg}), 200


@app.route('/fertilizer', methods=['POST'])
def fertilizer():
    """AI Fertilizer recommendation route."""
    data = request.get_json() or {}
    crop = data.get("crop_type", "Crop").strip()
    stage = data.get("growth_stage", "Vegetative").strip()
    soil = data.get("soil_type", "Loamy").strip()
    symptoms = data.get("symptoms", "None").strip()
    language = data.get("language", session.get('lang', 'English')).strip()

    if not groq_client:
        return jsonify({
            "plan": "Groq AI is not configured. Please add GROQ_API_KEY to your .env file."
        }), 200

    prompt = (
        f"Generate a customized fertilizer recommendation for a crop.\n"
        f"Crop Type: {crop}\n"
        f"Growth Stage: {stage}\n"
        f"Soil Type: {soil}\n"
        f"Observed leaf symptoms/nutrient deficiencies: {symptoms}\n\n"
        f"Please provide:\n"
        f"1. Recommended fertilizer types (mention both organic composting/manures and NPK mineral ratios).\n"
        f"2. Exact dosage guidelines.\n"
        f"3. Timing and application method (e.g. soil application, foliar spray).\n"
        f"4. Crucial tips to prevent nutrient lock or root burn.\n\n"
        f"Format the output using clear markdown headers, bold text, and bullet points. "
        f"Ensure you respond entirely in {language}."
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional agronomist and soil nutrient expert. Give practical, structured advice for farmers."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=1000
        )
        plan = completion.choices[0].message.content
        return jsonify({"plan": plan})
    except Exception as e:
        return jsonify({"plan": f"AI error generating plan: {str(e)}"}), 200


@app.route('/weather_advisory', methods=['POST'])
def weather_advisory():
    """Generates LLM weather-based farming advisory action items."""
    data = request.get_json() or {}
    temp = str(data.get("temperature", "25")).strip()
    humidity = str(data.get("humidity", "60")).strip()
    precip = str(data.get("precipitation", "0")).strip()
    weather_code = str(data.get("weather_code", "0")).strip()
    crop = data.get("crop_type", "General Crops").strip()
    language = data.get("language", session.get('lang', 'English')).strip()

    if not groq_client:
        return jsonify({
            "advisory": "Groq AI is not configured. Connect your Groq API key in your .env file to get smart weather alerts."
        }), 200

    prompt = (
        f"You are a weather-smart farming advisor. "
        f"Given the current conditions: Temperature: {temp}°C, Humidity: {humidity}%, Recent Precipitation: {precip}mm, weather code {weather_code}. "
        f"For the Crop: {crop}.\n"
        f"Provide a brief weather-based agricultural action list (3-4 bullet points) explaining:\n"
        f"- Water/Irrigation action: Should they irrigate or delay due to rain?\n"
        f"- Disease/Pest warning: Does this temp/humidity raise disease risks (like blight/fungus)?\n"
        f"- Spray/Fertilizer application advice: Is it safe to spray foliar sprays/fertilizers or will they be washed away?\n\n"
        f"Keep the bullet points very brief, direct, and actionable for farmers. Respond entirely in {language}."
    )

    try:
        completion = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a meteorological farming consultant. Speak directly and concisely."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=600
        )
        advisory = completion.choices[0].message.content
        return jsonify({"advisory": advisory})
    except Exception as e:
        return jsonify({"advisory": f"Unable to generate weather advice: {str(e)}"}), 200


if __name__ == "__main__":
    app.run(debug=True)