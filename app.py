from flask import Flask, render_template, request, url_for, send_from_directory
import os
import random
import base64
import json
import requests
import openai

# load .env if present (optional)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# GROQ config (optional)
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
GROQ_API_URL = os.environ.get('GROQ_API_URL', 'https://api.groq.com/openai/v1/chat/completions')

# GEMINI config (optional)
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

import uuid
from werkzeug.utils import secure_filename
import logging
from flask_cors import CORS

app = Flask(__name__, static_folder='frontend/dist', static_url_path='/')

CORS(app)
app.logger.setLevel(logging.INFO)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# OpenAI config (set OPENAI_API_KEY in environment)
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
if OPENAI_API_KEY:
    # strip accidental surrounding quotes
    OPENAI_API_KEY = OPENAI_API_KEY.strip().strip('"').strip("'")
    try:
        openai.api_key = OPENAI_API_KEY
    except Exception:
        pass

# Models to try (comma-separated in OPENAI_MODEL env to override)
MODELS_TRY = os.environ.get('OPENAI_MODEL', 'gpt-4o,gpt-4-turbo,gpt-4o-mini').split(',')


def analyze_with_openai(image_path: str):
    """Send image to OpenAI Responses (vision-capable) and request a
    structured JSON reply describing skin type, conditions and
    recommended product categories.
    This function attempts a best-effort parse; if anything goes wrong
    it returns None so caller can fallback to a simulated result.
    """
    if not OPENAI_API_KEY:
        return None

    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')

    # Quick probe: verify the model/key works with a small text request
    try:
        client = openai.OpenAI()
        try:
            probe = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": "Test"}])
        except Exception as e:
            app.logger.error(f"Model probe failed: {e}")
            return None
    except Exception:
        # if SDK isn't usable, we'll fall back to raw request later
        pass

    prompt = (
        "Anda adalah seorang dokter kulit (dermatologist) ahli dengan spesialisasi dalam menganalisis kondisi kulit secara visual. "
        "Analisis foto wajah yang diberikan dengan sangat teliti dan detail. Perhatikan baik-baik kilau (sebum/minyak), pori-pori, "
        "garis halus, tekstur kasar, kemerahan, pustula/jerawat, komedo, dan hiperpigmentasi.\n\n"
        "Berdasarkan analisis visual tersebut, kembalikan HANYA objek JSON (tanpa teks ekstra) dengan kunci berikut:\n"
        "- skin_type: tipe kulit yang PALING dominan, pilih salah satu dari: 'Kering', 'Berminyak', 'Kombinasi', 'Normal', 'Sensitif'. (Pertimbangkan zona-T untuk kombinasi).\n"
        "- conditions: daftar kondisi kulit yang spesifik yang terlihat nyata pada gambar (contoh: ['jerawat inflamasi', 'komedo terbuka', 'hiperpigmentasi', 'kemerahan', 'kusam', 'pori-pori besar', 'tekstur tidak merata']).\n"
        "- situation: deskripsi singkat situasi wajah saat ini berdasarkan visual (misal: 'berminyak di area-T', 'kemerahan iritasi', 'jerawat aktif', 'terlihat lelah').\n"
        "- recommendations: objek dengan kunci (Pembersih Wajah, Pelembap, Serum, Tabir Surya, Tambahan) dan saran spesifik yang aman dan sesuai dengan kondisi yang ditemukan.\n\n"
        "PENTING: Pastikan prediksi akurat berdasarkan gambar asli, jangan menebak secara acak. Output harus valid JSON saja tanpa format markdown markdown ```."
    )

    # Select a working model by probing small text requests (avoid sending large image first)
    chosen_model = None
    for model_candidate in MODELS_TRY:
        try:
            client = openai.OpenAI()
            client.chat.completions.create(model=model_candidate.strip(), messages=[{"role": "user", "content": "Test"}])
            chosen_model = model_candidate.strip()
            app.logger.info(f"Selected model: {chosen_model}")
            break
        except Exception as e:
            app.logger.info(f"Model probe failed for {model_candidate}: {e}")
            continue

    if not chosen_model:
        app.logger.error(f"No available model found among candidates: {MODELS_TRY}")
        return None

    payload = {
        "model": chosen_model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prefer using the official openai SDK client if available
    try:
        client = openai.OpenAI()
        resp = client.chat.completions.create(**payload)
        # SDK returns object-like structure; convert to dict
        data = resp.to_dict() if hasattr(resp, 'to_dict') else resp
    except Exception as e:
        # Attempt raw requests as a fallback, but capture and log detailed info
        try:
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            try:
                body = resp.text
            except Exception:
                body = '<unreadable body>'
            app.logger.error(f"OpenAI HTTP status: {getattr(resp, 'status_code', 'n/a')} body={body}")
            resp.raise_for_status()
            data = resp.json()
        except Exception as inner_e:
            # Log exception details including response if present
            try:
                app.logger.exception(f"OpenAI analyze error (sdk/raw): {inner_e}")
            except Exception:
                pass
            return None

        # Attempt to find textual output in the responses payload
        outputs = None
        if isinstance(data, dict):
            outputs = data.get('choices')
        else:
            outputs = data
        text = None

        if isinstance(outputs, list) and outputs:
            # scan for text content
            for out in outputs:
                # new Responses API might put text under 'content'
                message = out.get('message', {}) if isinstance(out, dict) else None
                if message and isinstance(message, dict):
                    content = message.get('content')
                    if content:
                        text = content
                        break

        # final fallback: try top-level 'text' field
        if not text:
            text = data.get('text') or data.get('response')

        if not text:
            app.logger.info("No text found in OpenAI response payload")
            return None

        # parse JSON from the model output (strip surrounding whitespace)
        text = text.strip()

        # Some models may include surrounding ```json blocks; strip common markers
        if text.startswith('```'):
            # remove any triple-backtick fences
            parts = text.split('```')
            # find the first part that looks like JSON
            for p in parts:
                p = p.strip()
                if p.startswith('{'):
                    text = p
                    break

        try:
            result_json = json.loads(text)
            return result_json
        except Exception as e:
            app.logger.error(f"Failed to json.loads model output: {e} - output={text}")
            return None

    except Exception as e:
        try:
            app.logger.exception("OpenAI analyze error:")
        except Exception:
            pass
        return None


def analyze_with_groq(image_path: str):
    """Send image to GROQ endpoint. The exact GROQ API may differ; this
    implementation posts a JSON payload similar to the Responses API and
    returns a parsed JSON object on success or None on failure.
    Configure `GROQ_API_URL` and `GROQ_API_KEY` in .env.
    """
    if not GROQ_API_KEY or not GROQ_API_URL:
        return None
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')

    prompt = (
        "Anda adalah seorang dokter kulit (dermatologist) ahli dengan spesialisasi dalam menganalisis kondisi kulit secara visual. "
        "Analisis foto wajah yang diberikan dengan sangat teliti dan detail. Perhatikan baik-baik kilau (sebum/minyak), pori-pori, "
        "garis halus, tekstur kasar, kemerahan, pustula/jerawat, komedo, dan hiperpigmentasi.\n\n"
        "Berdasarkan analisis visual tersebut, kembalikan HANYA objek JSON (tanpa teks ekstra) dengan kunci berikut:\n"
        "- skin_type: tipe kulit yang PALING dominan, pilih salah satu dari: 'Kering', 'Berminyak', 'Kombinasi', 'Normal', 'Sensitif'. (Pertimbangkan zona-T untuk kombinasi).\n"
        "- conditions: daftar kondisi kulit yang spesifik yang terlihat nyata pada gambar (contoh: ['jerawat inflamasi', 'komedo terbuka', 'hiperpigmentasi', 'kemerahan', 'kusam', 'pori-pori besar', 'tekstur tidak merata']).\n"
        "- situation: deskripsi singkat situasi wajah saat ini berdasarkan visual (misal: 'berminyak di area-T', 'kemerahan iritasi', 'jerawat aktif', 'terlihat lelah').\n"
        "- recommendations: objek dengan kunci (Pembersih Wajah, Pelembap, Serum, Tabir Surya, Tambahan) dan saran spesifik yang aman dan sesuai dengan kondisi yang ditemukan.\n\n"
        "PENTING: Pastikan prediksi akurat berdasarkan gambar asli, jangan menebak secara acak. Output harus valid JSON saja tanpa format markdown markdown ```."
    )

    payload = {
        "model": os.environ.get('GROQ_MODEL', 'llama-3.2-90b-vision-preview'),     
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}}
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        url = GROQ_API_URL
        if "responses" in url:
            url = url.replace("responses", "chat/completions")
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        try:
            body = resp.text
        except Exception:
            body = '<unreadable body>'
        if resp.status_code != 200:
            app.logger.error(f"GROQ HTTP status: {resp.status_code} body={body}")
            return None
        data = resp.json()

        # attempt to extract textual JSON output
        outputs = data.get('choices')
        text = None
        if isinstance(outputs, list):
            for out in outputs:
                if isinstance(out, dict):
                    message = out.get('message', {})
                    if message and isinstance(message, dict):
                        content = message.get('content')
                        if content:
                            text = content
                            break

        if not text:
            text = data.get('text') or data.get('response')
        if not text:
            app.logger.info('No text found in GROQ response payload')
            return None

        # strip fences and parse JSON
        text = text.strip()
        if text.startswith('```'):
            parts = text.split('```')
            for p in parts:
                p = p.strip()
                if p.startswith('{'):
                    text = p
                    break

        try:
            result_json = json.loads(text)
            return result_json
        except Exception as e:
            app.logger.error(f"Failed to json.loads GROQ output: {e} - output={text}")
            return None

    except Exception as e:
        try:
            app.logger.exception(f"GROQ analyze error: {e}")
        except Exception:
            pass
        return None


def analyze_with_gemini(image_path: str):
    """Send image to Google Gemini REST API."""
    if not GEMINI_API_KEY:
        return None
    import mimetypes
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/jpeg"

    import time
    max_retries = 3
    
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('utf-8')

    prompt = (
        "Anda adalah seorang dokter kulit (dermatologist) ahli dengan spesialisasi dalam menganalisis kondisi kulit secara visual. "
        "Analisis foto wajah yang diberikan dengan sangat teliti dan detail. Perhatikan baik-baik kilau (sebum/minyak), pori-pori, "
        "garis halus, tekstur kasar, kemerahan, pustula/jerawat, komedo, dan hiperpigmentasi.\n\n"
        "Berdasarkan analisis visual tersebut, kembalikan HANYA objek JSON (tanpa teks ekstra) dengan kunci berikut:\n"
        "- skin_type: tipe kulit yang PALING dominan, pilih salah satu dari: 'Kering', 'Berminyak', 'Kombinasi', 'Normal', 'Sensitif'. (Pertimbangkan zona-T untuk kombinasi).\n"
        "- conditions: daftar kondisi kulit yang spesifik yang terlihat nyata pada gambar (contoh: ['jerawat inflamasi', 'komedo terbuka', 'hiperpigmentasi', 'kemerahan', 'kusam', 'pori-pori besar', 'tekstur tidak merata']).\n"
        "- situation: deskripsi singkat situasi wajah saat ini berdasarkan visual (misal: 'berminyak di area-T', 'kemerahan iritasi', 'jerawat aktif', 'terlihat lelah').\n"
        "- recommendations: objek dengan kunci (Pembersih Wajah, Pelembap, Serum, Tabir Surya, Tambahan) dan saran spesifik yang aman dan sesuai dengan kondisi yang ditemukan.\n\n"
        "PENTING: Pastikan prediksi akurat berdasarkan gambar asli, jangan menebak secara acak. Output harus valid JSON saja tanpa format markdown markdown ```."
    )

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inline_data": {
                        "mime_type": mime_type,
                        "data": b64
                    }
                }
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }
    headers = {"Content-Type": "application/json"}

    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if resp.status_code == 503:
                app.logger.warning(f"Gemini API overloaded (503). Retrying {attempt + 1}/{max_retries}...")
                time.sleep(2 ** attempt) # Exponential backoff
                continue

            if resp.status_code != 200:
                app.logger.error(f"Gemini HTTP status {resp.status_code}: {resp.text}")
                return None

            data = resp.json()
            parts = data.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])
            text = parts[0].get('text', '') if parts else ''

            if not text:
                app.logger.info("No text found in Gemini response payload")
                return None

            # strip fences and parse JSON
            text = text.strip()
            if text.startswith('```'):
                parts_split = text.split('```')
                for p in parts_split:
                    p = p.strip()
                    if p.startswith('{'):
                        text = p
                        break
            
            result_json = json.loads(text)
            return result_json

        except requests.exceptions.Timeout:
            app.logger.warning(f"Gemini API timeout. Retrying {attempt + 1}/{max_retries}...")
            time.sleep(2 ** attempt)
        except Exception as e:
            app.logger.exception(f"Gemini analyze error: {e}")
            return None

    app.logger.error("Gemini analysis failed after max retries.")
    return None

# ANALYZE API
@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    if 'image' not in request.files:
        return {"error": "No image provided"}, 400
    file = request.files['image']
    if file:
        # create a secure, unique filename to avoid caching/overwrite
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_name = f"{uuid.uuid4().hex}{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
        file.save(filepath)
        # frontend URL (Flask serves from /static)
        image_url = f"http://127.0.0.1:5000/static/uploads/{unique_name}"
        
        ai_response = None
        # 1. Try Gemini first (Best for Vision currently if Groq fails)
        if GEMINI_API_KEY:
            ai_response = analyze_with_gemini(filepath)
            app.logger.info(f"Gemini response object: {ai_response}")
            
        # 2. Try GROQ if Gemini not used or failed
        if not ai_response and GROQ_API_KEY:
            ai_response = analyze_with_groq(filepath)
            app.logger.info(f"GROQ response object: {ai_response}")
            
        # 3. Try OpenAI if GROQ failed
        if not ai_response and OPENAI_API_KEY:
            ai_response = analyze_with_openai(filepath)
            app.logger.info(f"OpenAI response object: {ai_response}")
            
        app.logger.info(f"AI response object: {ai_response}")
        
        if ai_response:
            # map to simple display strings
            skin_type = ai_response.get('skin_type')
            conditions = ai_response.get('conditions')
            recommendations = ai_response.get('recommendations')
            
            # format result and recommendation for the template
            result = skin_type if skin_type else 'Unknown'
            app.logger.info(f"Using AI result: {result}")
            
            # build a short recommendation string
            if recommendations and isinstance(recommendations, dict):
                # Send the raw dict to the frontend
                recommendation = recommendations
            else:
                recommendation = {'General': ', '.join(conditions)} if conditions else {'General': 'No recommendation'}
            source = 'AI'
        else:
            # SIMULASI AI (fallback)
            skin_types = ["Kulit Kering", "Kulit Berminyak", "Kulit Normal"]
            result = random.choice(skin_types)
            app.logger.info(f"Fallback chosen: {result}")
            
            if result == "Kulit Kering":
                recommendation = {"Pelembap": "Gunakan pelembap agar tidak kering.", "Tabir Surya": "Gunakan tabir surya yang melembapkan (Hydrating)."}
            elif result == "Kulit Berminyak":
                recommendation = {"Pembersih Wajah": "Gunakan pembersih dengan kandungan salicylic acid.", "Tabir Surya": "Gunakan tabir surya berbahan ringan (gel)."}
            else:
                recommendation = {"Perawatan Rutin": "Maintain your skincare routine and stay hydrated."}
            source = 'Fallback'
        
        return {
            "result": result,
            "recommendation": recommendation,
            "image_url": image_url,
            "source": source
        }

# Main route - serve React app
@app.route('/')
def index():
    return send_from_directory('frontend/dist', 'index.html')

# Serve static uploads
@app.route('/static/uploads/<path:filename>')
def serve_uploads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)