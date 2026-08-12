import os
import json
import logging
from pathlib import Path
from flask import Flask, render_template, request, jsonify, session, redirect, url_for

from auth.auth_handler import create_user, authenticate_user
from agents.local_agent import local_commerce_agent
from tools.orders_tools import get_customer_orders
from voice.voice_agent import VoiceAgent
from voice.telephony import TelephonyManager

# Setup Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask App
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("FLASK_SECRET_KEY", "ai_commerce_copilot_super_secret_key_2026")

# Lazy initialize voice agent
voice_agent_instance = None

def get_voice_agent():
    global voice_agent_instance
    if voice_agent_instance is None:
        voice_agent_instance = VoiceAgent()
    return voice_agent_instance

# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route("/login", methods=["GET"])
def login_page():
    if session.get("is_authenticated"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    success, result = authenticate_user(email, password)
    if success:
        session["is_authenticated"] = True
        session["user_info"] = {"name": result, "email": email}
        session["customer_id"] = "C001"
        session["language"] = "en"
        session["order_state"] = {}
        return jsonify({"success": True, "user_name": result})
    else:
        return jsonify({"success": False, "message": result}), 401

@app.route("/api/signup", methods=["POST"])
def api_signup():
    data = request.get_json() or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "Please fill all fields."}), 400

    success, msg = create_user(name, email, password)
    if success:
        session["is_authenticated"] = True
        session["user_info"] = {"name": name, "email": email}
        session["customer_id"] = "C001"
        session["language"] = "en"
        session["order_state"] = {}
        return jsonify({"success": True, "message": msg})
    else:
        return jsonify({"success": False, "message": msg}), 400

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"success": True})

# ============================================================
# MAIN DASHBOARD ROUTE
# ============================================================

@app.route("/")
def dashboard():
    if not session.get("is_authenticated"):
        return redirect(url_for("login_page"))

    user_info = session.get("user_info", {"name": "User", "email": ""})
    customer_id = session.get("customer_id", "C001")
    user_language = session.get("language", "en")

    return render_template(
        "index.html",
        user_name=user_info.get("name", "User"),
        user_email=user_info.get("email", ""),
        customer_id=customer_id,
        user_language=user_language
    )

# ============================================================
# CUSTOMER & ORDERS APIS
# ============================================================

@app.route("/api/customer/orders", methods=["GET"])
def api_customer_orders():
    if not session.get("is_authenticated"):
        return jsonify({"error": "Unauthorized"}), 401

    customer_id = request.args.get("customer_id", session.get("customer_id", "C001")).strip().upper()
    session["customer_id"] = customer_id

    try:
        customer_orders = get_customer_orders(customer_id)
    except Exception as e:
        logger.error(f"Failed to fetch orders: {e}")
        customer_orders = []

    total_orders = len(customer_orders)
    active_orders = sum(1 for o in customer_orders if o.get("status") not in ["Cancelled", "Delivered"])
    cancelled_orders = sum(1 for o in customer_orders if o.get("status") == "Cancelled")
    total_spending = sum(float(o.get("amount", 0)) for o in customer_orders if o.get("status") != "Cancelled")

    return jsonify({
        "customer_id": customer_id,
        "orders": customer_orders,
        "metrics": {
            "total": total_orders,
            "active": active_orders,
            "cancelled": cancelled_orders,
            "spending": total_spending
        }
    })

# ============================================================
# CHAT & AI ASSISTANT APIS
# ============================================================

@app.route("/api/chat", methods=["POST"])
def api_chat():
    if not session.get("is_authenticated"):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    message = data.get("message", "").strip()
    language = data.get("language", session.get("language", "en"))

    session["language"] = language
    order_state = session.get("order_state", {})

    if not message:
        return jsonify({"response": "Please enter a message.", "order_state": order_state})

    try:
        response_text = local_commerce_agent(message, order_state, language=language)
        session["order_state"] = order_state
        return jsonify({
            "response": response_text,
            "order_state": order_state
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({
            "response": f"❌ Sorry, an error occurred: {str(e)}",
            "order_state": order_state
        }), 500

@app.route("/api/chat/clear", methods=["POST"])
def api_chat_clear():
    session["order_state"] = {}
    return jsonify({"success": True, "order_state": {}})

# ============================================================
# VOICE AI & TELEPHONY APIS
# ============================================================

@app.route("/api/voice/process", methods=["POST"])
def api_voice_process():
    if not session.get("is_authenticated"):
        return jsonify({"error": "Unauthorized"}), 401

    if "audio" not in request.files:
        return jsonify({"success": False, "message": "No audio file provided."}), 400

    audio_file = request.files["audio"]
    wav_bytes = audio_file.read()
    language = request.form.get("language", session.get("language", "en"))
    order_state = session.get("order_state", {})

    try:
        agent = get_voice_agent()
        result = agent.process_web_audio(
            wav_bytes=wav_bytes,
            language=language,
            order_state=order_state
        )
        session["order_state"] = order_state
        return jsonify(result)
    except Exception as e:
        logger.error(f"Voice processing error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/voice/call", methods=["POST"])
def api_voice_call():
    if not session.get("is_authenticated"):
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json() or {}
    phone_number = data.get("phone_number", "").strip()

    if not phone_number:
        return jsonify({"success": False, "message": "Phone number is required."}), 400

    try:
        telephony = TelephonyManager()
        call_sid = telephony.make_call(phone_number)
        return jsonify({"success": True, "call_sid": call_sid})
    except Exception as e:
        logger.error(f"Telephony call error: {e}")
        return jsonify({"success": False, "message": str(e)}), 500

# ============================================================
# TWILIO VOICE WEBHOOK ROUTES
# ============================================================

from voice.call_manager import call_manager
from config.settings import WEBHOOK_BASE_URL, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

@app.route("/voice/incoming", methods=["POST", "GET"])
def voice_incoming():
    try:
        call_sid = request.form.get("CallSid") or request.args.get("CallSid")
        from_num = request.form.get("From") or request.args.get("From")
        to_num = request.form.get("To") or request.args.get("To")

        logger.info(f"Incoming call from {from_num} to {to_num} (SID: {call_sid})")

        telephony = TelephonyManager()
        if not call_sid:
            return app.response_class("<Response><Reject /></Response>", mimetype="application/xml")

        call_manager.get_or_create_session(call_sid, from_num)
        call_manager.cleanup_old_sessions()

        # Natural human greeting
        greeting = "I am calling from an AI calling agent. How can I help you?"
        action_url = f"{WEBHOOK_BASE_URL}/voice/process"

        twiml = telephony.create_gather_twiml(
            action_url=action_url,
            say_text=greeting,
            language="en-IN",
            timeout=6,
        )
        return app.response_class(twiml, mimetype="application/xml")
    except Exception as e:
        logger.error(f"Error in voice_incoming: {e}")
        telephony = TelephonyManager()
        return app.response_class(telephony.create_say_twiml("Hello! Thank you for calling AI Commerce Copilot. How can I help you today?"), mimetype="application/xml")

@app.route("/voice/language_selection", methods=["POST", "GET"])
def voice_language_selection():
    # Redirect to voice_process for seamless flow
    return voice_process_speech()

@app.route("/voice/process", methods=["POST", "GET"])
def voice_process_speech():
    try:
        call_sid = request.form.get("CallSid") or request.args.get("CallSid")
        speech_result = request.form.get("SpeechResult") or request.form.get("Digits")

        telephony = TelephonyManager()
        agent = get_voice_agent()

        if not call_sid:
            return app.response_class("<Response><Reject /></Response>", mimetype="application/xml")

        session_data = call_manager.get_session(call_sid)
        if not session_data:
            session_data = call_manager.get_or_create_session(call_sid, "phone")

        current_lang = session_data.get("language", "en")

        # If user spoke, auto-detect language (English, Telugu, Hindi)
        if speech_result:
            detected_lang = agent.detect_language(speech_result)
            if detected_lang != current_lang:
                current_lang = detected_lang
                call_manager.update_session(call_sid, "language", current_lang)

        if not speech_result:
            action_url = f"{WEBHOOK_BASE_URL}/voice/process"
            fallback_texts = {
                "en": "I'm listening. How can I help you today?",
                "te": "నేను వింటున్నాను. మీకు ఎలా సహాయం చేయగలను?",
                "hi": "मैं सुन रहा हूँ। मैं आपकी क्या मदद कर सकता हूँ?"
            }
            fallback = fallback_texts.get(current_lang, fallback_texts["en"])

            twiml = telephony.create_gather_twiml(
                action_url=action_url,
                say_text=fallback,
                language=current_lang,
                timeout=6,
            )
            return app.response_class(twiml, mimetype="application/xml")

        logger.info(f"User said on call {call_sid} ({current_lang}): {speech_result}")
        session_data["conversation_history"].append({"role": "user", "content": speech_result})

        from agents.commerce_agent import ask_commerce_agent
        response_text = ask_commerce_agent(speech_result)
        session_data["conversation_history"].append({"role": "agent", "content": response_text})

        # Format into clean 100% human speech (no emojis, no markdown, no technical instructions)
        clean_text = agent._strip_markdown(response_text)

        action_url = f"{WEBHOOK_BASE_URL}/voice/process"
        twiml = telephony.create_gather_twiml(
            action_url=action_url,
            say_text=clean_text,
            language=current_lang,
            timeout=6,
        )
        return app.response_class(twiml, mimetype="application/xml")
    except Exception as e:
        logger.error(f"Error in voice_process_speech: {e}")
        telephony = TelephonyManager()
        twiml = telephony.create_gather_twiml(
            action_url=f"{WEBHOOK_BASE_URL}/voice/process",
            say_text="Could you please tell me how I can help you?",
            language="en-IN",
            timeout=6
        )
        return app.response_class(twiml, mimetype="application/xml")
    except Exception as e:
        logger.error(f"Error in voice_process_speech: {e}")
        telephony = TelephonyManager()
        twiml = telephony.create_gather_twiml(
            action_url=f"{WEBHOOK_BASE_URL}/voice/process",
            say_text="Sorry, I had trouble understanding that. Could you please repeat your request?",
            language="en-IN",
            timeout=6
        )
        return app.response_class(twiml, mimetype="application/xml")

@app.route("/voice/status", methods=["POST", "GET"])
def voice_call_status():
    call_sid = request.form.get("CallSid") or request.args.get("CallSid")
    call_status_val = request.form.get("CallStatus") or request.args.get("CallStatus")

    if call_status_val == "completed" and call_sid:
        session_data = call_manager.get_session(call_sid)
        if session_data:
            from datetime import datetime
            log_entry = {
                "call_sid": call_sid,
                "timestamp": datetime.now().isoformat(),
                "customer_id": session_data.get("customer_id"),
                "language": session_data.get("language"),
                "history": session_data.get("conversation_history", [])
            }
            logs_file = Path(__file__).parent / "data" / "call_logs.json"
            try:
                if logs_file.exists():
                    with open(logs_file, "r", encoding="utf-8") as f:
                        logs = json.load(f)
                else:
                    logs = []
                logs.append(log_entry)
                with open(logs_file, "w", encoding="utf-8") as f:
                    json.dump(logs, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Failed to save call logs: {e}")
            call_manager.end_session(call_sid)

    return app.response_class("<Response></Response>", mimetype="application/xml")

# ============================================================
# MAIN ENTRYPOINT
# ============================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)