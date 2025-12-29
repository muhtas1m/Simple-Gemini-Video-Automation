import os
import re
import wave
import time
import json
import random
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from google.genai.errors import ClientError

app = Flask(__name__)

# ---USER SETUP---
API_KEY = "Paste Your API Key Here"  # <--- PASTE KEY HERE

# --- CONFIGURATION ---
TEXT_MODEL = "gemini-2.5-flash" #free version
AUDIO_MODEL = "gemini-2.5-flash-preview-tts" #free version
IMAGE_MODEL = "imagen-4.0-fast-generate-001" #paid, no free version yet

VOICE_NAME = "Enceladus" #You can change this to any available voice from Google AI Studio
SAMPLE_RATE = 24000
BASE_OUTPUT_DIR = "Rendered_Projects"
SAFE_DELAY = 12 # Seconds to wait between images (Prevents 429 Errors)

if not os.path.exists(BASE_OUTPUT_DIR):
    os.makedirs(BASE_OUTPUT_DIR)

client = None
if API_KEY and API_KEY != "PASTE_YOUR_API_KEY_HERE":
    client = genai.Client(api_key=API_KEY)

# --- UTILITIES ---
def sanitize(name):
    return re.sub(r'[\\/*?:"<>|]', "", name).strip().replace(" ", "_")

def save_wav(filepath, audio_data):
    try:
        with wave.open(filepath, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_data)
        return True
    except:
        return False

# ---SMART RETRY ENGINE---
def api_call_with_retry(call_function, *args, **kwargs):
    max_retries = 8
    base_wait = 10 
    for attempt in range(max_retries):
        try:
            return call_function(*args, **kwargs)
        except ClientError as e:
            error_str = str(e)
            if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                wait_time = base_wait * (attempt + 1) + random.uniform(1, 4)
                print(f"   ⏳ Limit hit. Cooling down for {int(wait_time)}s...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("Max retries exceeded. API is busy.")

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if not client: return jsonify({'error': 'API Key missing'}), 500
    
    data = request.json
    title = data.get('title')
    desc = data.get('description')
    
    # User Preferences
    word_count = int(data.get('word_count', 500))
    img_count = int(data.get('img_count', 10))
    art_style = data.get('art_style')
    if not art_style: art_style = "Cinematic lighting, hyper-realistic 8k."

    # Checkboxes (Default to True if missing)
    do_script = data.get('do_script', True)
    do_voice = data.get('do_voice', True)
    do_prompts = data.get('do_prompts', True)
    do_images = data.get('do_images', True)

    # Setup Folders
    safe_title = sanitize(title)
    project_path = os.path.join(BASE_OUTPUT_DIR, safe_title)
    if not os.path.exists(project_path): os.makedirs(project_path)
    visuals_path = os.path.join(project_path, "visuals")
    if not os.path.exists(visuals_path): os.makedirs(visuals_path)

    script_text = ""
    prompts_list = []

    try:
        # --- 1. SCRIPT ---
        script_path = os.path.join(project_path, "script.txt")
        
        if do_script:
            print(f"📝 Generating Script...")
            script_resp = api_call_with_retry(
                client.models.generate_content,
                model=TEXT_MODEL,
                contents=f"Write a {word_count}-word video script for '{title}'. Context: {desc}. Format: Single continuous paragraph. Tone: Storyteller. No scene headers."
            )
            script_text = script_resp.text.replace("\n", " ")
            with open(script_path, "w", encoding="utf-8") as f: f.write(script_text)
            time.sleep(1)
        elif os.path.exists(script_path):
            print("📖 Loading existing script...")
            with open(script_path, "r", encoding="utf-8") as f: script_text = f.read()

        # --- 2. VOICE ---
        if do_voice:
            if not script_text: raise ValueError("Cannot generate Voice: No script found.")
            
            print(f"🎙️ Recording Voice...")
            voice_path = os.path.join(project_path, "voiceover.wav")
            audio_resp = api_call_with_retry(
                client.models.generate_content,
                model=AUDIO_MODEL,
                contents=f"Narrate this: {script_text[:9000]}",
                config=types.GenerateContentConfig(
                    response_modalities=["AUDIO"],
                    speech_config=types.SpeechConfig(
                        voice_config=types.VoiceConfig(
                            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE_NAME)
                        )
                    )
                )
            )
            audio_data = b"".join([p.inline_data.data for p in audio_resp.candidates[0].content.parts if p.inline_data])
            save_wav(voice_path, audio_data)
            time.sleep(2)
        else:
            print("⏭️ Skipping Voice.")

        # --- 3. PROMPTS ---
        prompts_path = os.path.join(project_path, "prompts.json")
        
        if do_prompts:
            if not script_text: raise ValueError("Cannot generate Prompts: No script found.")
            print(f"🧠 Designing {img_count} Prompts...")
            
            prompt_req = (
                f"Read this script and generate exactly {img_count} image prompts.\n"
                f"SCRIPT: {script_text[:4000]}\n"
                f"INSTRUCTIONS: Return a JSON Array of objects with 'prompt'.\n"
                f"STYLE TEMPLATE: {art_style}\n"
                f"Apply the style template to every prompt.\n"
                f"Name them serially from scene 1 to scene {img_count}.\n"
            )
            
            prompt_resp = api_call_with_retry(
                client.models.generate_content,
                model=TEXT_MODEL,
                contents=prompt_req,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            prompts_list = json.loads(prompt_resp.text.replace("```json", "").replace("```", ""))
            with open(prompts_path, "w", encoding="utf-8") as f: json.dump(prompts_list, f, indent=2)
            time.sleep(1)
        elif os.path.exists(prompts_path):
            print("📂 Loading existing prompts...")
            with open(prompts_path, "r", encoding="utf-8") as f: prompts_list = json.load(f)

        # --- 4. IMAGES ---
        generated_count = 0
        if do_images:
            if not prompts_list: raise ValueError("Cannot generate Images: No prompts found.")
            print(f"🎨 Painting {len(prompts_list)} Scenes...")
            
            for i, item in enumerate(prompts_list):
                if i >= img_count: break 
                save_path = os.path.join(visuals_path, f"scene_{i+1:02d}.png")
                
                if os.path.exists(save_path):
                    print(f"   -> Scene {i+1} exists.", end="\r")
                    generated_count += 1
                    continue

                print(f"    Painting {i+1}/{len(prompts_list)}...", end="\r")
                
                try:
                    img_resp = api_call_with_retry(
                        client.models.generate_images,
                        model=IMAGE_MODEL,
                        prompt=item['prompt'],
                        config=types.GenerateImagesConfig(
                            number_of_images=1,
                            aspect_ratio="16:9"
                        )
                    )
                    
                    if img_resp.generated_images:
                        img_resp.generated_images[0].image.save(save_path)
                        generated_count += 1
                    
                    time.sleep(SAFE_DELAY)

                except Exception as e:
                    print(f"\n    ⚠️ Skipped scene {i+1}: {e}")
                    time.sleep(SAFE_DELAY)
        else:
            print("⏭️ Skipping Images.")

        return jsonify({
            'status': 'success',
            'folder': project_path,
            'message': f"Operation Complete."
        })

    except Exception as e:
        print(f"ERROR: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, threaded=True, port=5000)