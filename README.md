# 🎬 Gemini Video Automation Studio

**Turn a single idea into a full multimedia production package with one click.**

Gemini Video Automation Studio is a local, AI-powered pipeline that uses Google's latest generative models to create video scripts, professional voiceovers, visual prompting strategies, and high-definition scene images automatically.

---

## ✨ Key Features

* **⚡ Zero-Friction Interface:** A modern, "Glassmorphism" dark-mode web UI to manage your productions.
* **📝 Storytelling Engine:** Generates engaging scripts with custom word counts.
* **🎙️ Native Audio Synthesis:** Creates human-quality voiceovers using Gemini.
* **🎨 AI Art Direction:** Brainstorms consistent image prompts based on your chosen art style (e.g., "Shadow", "Cyberpunk").
* **🖼️ High-Speed Rendering:** Generates batch images using **Imagen 4.0 Fast** (or Imagen 3), handling bursts of 30+ images.
* **🛡️ Smart Rate-Limiting:** Built-in "Retry Engine" automatically pauses and resumes to bypass Google's Free Tier `429 Resource Exhausted` errors.
* **💾 Resume Capability:** Smart file checking ensures you never lose progress. If the app stops, simply run it again—it picks up exactly where it left off.

---

## 🚀 Getting Started

Follow these steps to set up your own Director's Studio.

### Prerequisites
* Python installed on your system.
* A **Google AI Studio API Key** (Free). [Get it here](https://aistudio.google.com/app/apikey).

### Installation

1.  **Clone the Repository**
    ```bash
    git clone [https://github.com/yourusername/simple-gemini-video-automation.git](https://github.com/yourusername/simple-gemini-video-automation.git)
    cd simple-gemini-video-automation
    ```

2.  **Install Dependencies**
    ```bash
    pip install flask google-genai
    ```

3.  **Configure API Key**
    Open `app.py` in a text editor and paste your API key on line 15:
    ```python
    API_KEY = "YOUR_PASTED_KEY_HERE"
    ```

4.  **Launch the Studio**
    Double-click `LAUNCH.bat` or run:
    ```bash
    python app.py
    ```

5.  **Access the UI**
    Open your browser and go to: `http://127.0.0.1:5000`

---

## 🎛️ How to Use

1.  **Enter Project Details:** Give your video a Title and a Context (what is it about?).
2.  **Set Constraints:** Use the sliders to choose Script Length (300-2000 words) and Image Count (1-50).
3.  **Define Style:** Input an art style prompt (e.g., *"geometric, silhouette style"*).
4.  **Select Scope:** Check/Uncheck boxes for Script, Voice, Prompts, or Images depending on what you need.
5.  **Click "Initiate Production":** The system will handle the API traffic, generate files, and save them to a new folder in `Rendered_Projects`.

---

## 📂 Project Structure

Your generated projects are organized automatically:

```text
Rendered_Projects/
└── The_Mystery_of_Time/       <-- Your Title
    ├── script.txt             <-- Full Video Script
    ├── voiceover.wav          <-- 24kHz Audio File
    ├── prompts.json           <-- AI Generated Image Prompts
    └── visuals/               <-- Folder containing all images
        ├── scene_01.png
        ├── scene_02.png
        └── ...