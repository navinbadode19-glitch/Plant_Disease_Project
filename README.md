# 🌾 AgriGuard — Multilingual Crop Disease Diagnostics & Smart Farming Platform

> **AI-powered crop disease detection system with dual-engine diagnostics, multilingual chatbot support, weather-smart advisories, and soil nutrient planning — built for Indian farmers.**

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.15+-orange?logo=tensorflow)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green?logo=flask)](https://flask.palletsprojects.com/)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_4-purple?logo=groq)](https://console.groq.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📌 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Tech Stack](#-tech-stack)
- [Dataset Information](#-dataset-information)
- [Model Architecture & Training](#-model-architecture--training)
- [Project Structure](#-project-structure)
- [Installation & Setup](#-installation--setup)
- [Usage Guide](#-usage-guide)
- [Development Phases](#-development-phases)
- [Screenshots](#-screenshots)
- [API Keys & Configuration](#-api-keys--configuration)
- [Contributing](#-contributing)
- [Author](#-author)
- [License](#-license)

---

## 🔍 Overview

**AgriGuard** is an end-to-end digital agriculture advisory platform designed to help small-scale and marginal farmers across India. Farmers can simply upload a photo of a diseased crop leaf, and the system instantly identifies the disease, recommends both organic and chemical treatments with dosage and timelines, and provides weather-smart advisories — all in their preferred local language.

The system uses a **dual-inference approach**:
- A **local offline CNN model** (MobileNetV2 transfer learning) for fast, data-saving diagnosis of Tomato, Potato, and Pepper diseases.
- A **cloud-based Groq LLM Vision fallback** (LLaMA 4 Scout) for diagnosing complex pests, insects, and diseases across 10+ additional crop types.

---

## ✨ Key Features

### 🔬 1. Dual-Engine Disease Diagnostics
| Engine | Description | Use Case |
|--------|-------------|----------|
| **Local CNN (Offline)** | MobileNetV2 transfer learning model trained on PlantVillage dataset | Fast classification of 15 disease categories (Tomato, Potato, Pepper) — works without internet |
| **Groq Cloud AI Vision** | LLaMA 4 Scout 17B multimodal model via Groq API | Complex pest/insect identification, rare diseases, and extended crop support (Apple, Wheat, Cotton, Grape, Citrus, Mango, Sugarcane, etc.) |

- Automatic fallback to cloud AI when local CNN confidence is low
- Structured JSON diagnostic output with symptoms, severity, treatment, and recovery timeline
- Dynamic 21-day treatment timeline generation

### 🤖 2. Multilingual AgriBot (AI Chatbot)
- **Context-aware conversations**: Inherits scan history (disease name, symptoms, treatment, severity) so farmers can ask direct follow-up questions
- **Auto language detection**: Responds in the same language the farmer writes in
- **Powered by**: `llama-3.3-70b-versatile` via Groq
- Supports: **English, Hindi (हिन्दी), Tamil (தமிழ்), Telugu (తెలుగు), Marathi (मराठी)**

### 🌤️ 3. Weather-Smart Intelligence
- Fetches real-time local weather data (temperature, humidity, precipitation)
- Generates agricultural advisories based on weather conditions
- Warnings for: blight/fungus spread risk, irrigation timing, foliar spray wash-away risk
- Location-based coordinate integration

### 🌱 4. Growth-Stage Soil Nutrient Planner
- Custom fertilization recipes based on:
  - Crop variety
  - Growth phase (vegetative, flowering, fruiting)
  - Soil type (loamy, clayey, sandy)
- Recommends NPK ratios, composting guides, manure applications
- Root burn prevention warnings

### 🔐 5. User Authentication & Scan History
- Secure user registration and login system
- Salted & hashed password storage (SQLite-based)
- Complete history of crop scans, diagnoses, timelines, and treatments per user
- Session-based authentication with Flask

### 🌍 6. Full Multilingual Localization
- Complete UI translation for **5 languages**: English, Hindi, Tamil, Telugu, Marathi
- Dynamic label translation across all screens, advisories, and results
- Language preference saved per user session

---

## 🏗️ System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                      USER (Farmer)                           │
│              Upload leaf image / Chat / Weather              │
└──────────────────────┬───────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│                   Flask Web Application                      │
│                      (app.py)                                │
│  ┌─────────────┐  ┌───────────┐  ┌─────────────────────┐    │
│  │   Login /   │  │  Upload   │  │    AgriBot Chat     │    │
│  │  Register   │  │  & Scan   │  │   (Context-Aware)   │    │
│  └─────────────┘  └─────┬─────┘  └──────────┬──────────┘    │
│                         │                    │               │
│                    ┌────▼────┐          ┌────▼─────┐         │
│                    │ Local   │          │ Groq LLM │         │
│                    │ CNN     │          │ llama-3.3│         │
│                    │MobileV2 │          │ -70b     │         │
│                    └────┬────┘          └──────────┘         │
│                         │                                    │
│                    ┌────▼──────────┐                         │
│                    │ Low Confidence│                         │
│                    │  Fallback?    │                         │
│                    └────┬─────────┘                         │
│                         │ YES                                │
│                    ┌────▼────────┐                           │
│                    │ Groq Vision │                           │
│                    │ LLaMA 4    │                           │
│                    │ Scout 17B  │                           │
│                    └─────────────┘                           │
└──────────────────────────────────────────────────────────────┘
         │                    │                    │
    ┌────▼────┐         ┌────▼────┐          ┌────▼────┐
    │SQLite DB│         │disease_ │          │translat-│
    │(users,  │         │info.py  │          │ions.py  │
    │ scans)  │         │(15 crop │          │(5 langs)│
    └─────────┘         │diseases)│          └─────────┘
                        └─────────┘
```

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| **Backend Framework** | Flask 3.0+ |
| **Deep Learning** | TensorFlow 2.15+ / Keras |
| **Pre-trained Model** | MobileNetV2 (ImageNet weights) |
| **Cloud AI** | Groq API — LLaMA 4 Scout 17B (Vision), LLaMA 3.3 70B (Chat) |
| **Database** | SQLite3 (via `database.py`) |
| **Image Processing** | Pillow (PIL) 10.0+ |
| **Numerical Computing** | NumPy 1.23+ |
| **Environment Config** | python-dotenv |
| **Production Server** | Gunicorn 21.2+ |
| **Frontend** | HTML5, CSS3, Jinja2 Templates |
| **Language** | Python 3.10+ |

---

## 📊 Dataset Information

| Property | Details |
|----------|---------|
| **Dataset Name** | PlantVillage |
| **Total Images** | 20,638 |
| **Training Split** | 16,511 images (80%) |
| **Validation Split** | 4,127 images (20%) |
| **Number of Classes** | 15 |
| **Image Resolution** | 224 × 224 pixels (RGB) |
| **Crops Covered** | Tomato, Potato, Bell Pepper |

### 15 Disease Classes

| # | Class Name | Crop | Condition |
|---|-----------|------|-----------|
| 1 | Pepper\_\_bell\_\_\_Bacterial\_spot | Bell Pepper | Diseased |
| 2 | Pepper\_\_bell\_\_\_healthy | Bell Pepper | Healthy |
| 3 | Potato\_\_\_Early\_blight | Potato | Diseased |
| 4 | Potato\_\_\_Late\_blight | Potato | Diseased |
| 5 | Potato\_\_\_healthy | Potato | Healthy |
| 6 | Tomato\_Bacterial\_spot | Tomato | Diseased |
| 7 | Tomato\_Early\_blight | Tomato | Diseased |
| 8 | Tomato\_Late\_blight | Tomato | Diseased |
| 9 | Tomato\_Leaf\_Mold | Tomato | Diseased |
| 10 | Tomato\_Septoria\_leaf\_spot | Tomato | Diseased |
| 11 | Tomato\_Spider\_mites\_Two\_spotted\_spider\_mite | Tomato | Diseased |
| 12 | Tomato\_\_Target\_Spot | Tomato | Diseased |
| 13 | Tomato\_\_Tomato\_YellowLeaf\_\_Curl\_Virus | Tomato | Diseased |
| 14 | Tomato\_\_Tomato\_mosaic\_virus | Tomato | Diseased |
| 15 | Tomato\_healthy | Tomato | Healthy |

---

## 🧠 Model Architecture & Training

### Transfer Learning Pipeline

```
Input Image (224×224×3)
        │
        ▼
┌──────────────────┐
│  Rescaling Layer │  (pixel values: [0,255] → [-1,1])
│  x / 127.5 - 1.0│
└────────┬─────────┘
         │
         ▼
┌──────────────────────┐
│    MobileNetV2       │  (Pre-trained on ImageNet)
│  (Weights Frozen)    │  (include_top=False)
│  1,280 feature maps  │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│ GlobalAveragePooling │  (1,280 → 1,280)
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   Dropout (0.3)      │  (Regularization)
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│   Dense (15 units)   │  (Softmax activation)
│   Output: 15 classes │
└──────────────────────┘
```

### Training Configuration

| Parameter | Value |
|-----------|-------|
| **Base Model** | MobileNetV2 (ImageNet pre-trained) |
| **Base Weights** | Frozen (not trainable) |
| **Optimizer** | Adam |
| **Loss Function** | Sparse Categorical Crossentropy |
| **Batch Size** | 32 |
| **Epochs** | 10 |
| **Input Normalization** | Rescaling (x/127.5 - 1.0), built into model |
| **Regularization** | Dropout (rate = 0.3) |
| **Data Split** | 80% train / 20% validation (seed=123) |

### Validation Results

| Metric | Score |
|--------|-------|
| **Validation Accuracy** | 89.6% |
| **Validation Loss** | 0.3048 |

### Critical Bug Fix (Phase 5)
> ⚠️ A double-preprocessing bug was identified where `preprocess_input()` was being called both in the prediction script AND inside the compiled Keras model (via the Rescaling layer). This caused the model to output ~99% confidence for `Tomato_Late_blight` on ALL inputs. The fix was to remove the redundant `preprocess_input()` call from `predict.py`, since normalization is already handled by the model's built-in Rescaling layer.

---

## 📁 Project Structure

```
Plant_Disease_Project/
│
├── app.py                        # Main Flask web application & API routes
│                                 #   - Authentication, image upload, diagnosis
│                                 #   - Weather advisory, soil nutrient planner
│                                 #   - AgriBot chat integration
│
├── train.py                      # ML training pipeline script
│                                 #   - Loads PlantVillage dataset
│                                 #   - Builds MobileNetV2 transfer learning model
│                                 #   - Trains, validates, and saves .keras model
│
├── predict.py                    # Standalone CLI prediction script
│                                 #   - Loads model and runs inference on a single image
│                                 #   - Outputs predicted class and confidence score
│
├── verify_model.py               # Model verification & validation tool
│                                 #   - Checks model layer structure and input shape
│                                 #   - Runs mock inference to validate output
│
├── database.py                   # SQLite database interface
│                                 #   - User registration/login with hashed passwords
│                                 #   - Scan history logging per user
│
├── disease_info.py               # Local disease knowledge base
│                                 #   - 15 entries with symptoms, causes, treatments
│                                 #   - Chemical/organic treatment recommendations
│                                 #   - Severity levels and prevention tips
│
├── recommendation_engine.py      # Advisory logic & treatment timeline generator
│                                 #   - Treatment timeline plans
│                                 #   - Crop loss estimations
│
├── translations.py               # Multilingual translation dictionary
│                                 #   - Supports: English, Hindi, Tamil, Telugu, Marathi
│                                 #   - Covers all UI labels and dynamic content
│
├── class_names.txt               # Alphabetical list of 15 disease class labels
│                                 #   - Maps model output indices to disease names
│
├── plant_disease_model.keras     # Trained CNN model file (~9.4 MB)
│                                 #   - MobileNetV2 base + custom classification head
│
├── requirements.txt              # Python package dependencies
│
├── .env                          # Environment variables (API keys - not committed)
├── .gitignore                    # Git ignore rules
│
├── templates/                    # Jinja2 HTML templates
│   ├── index.html                #   - Main dashboard & upload page
│   ├── login.html                #   - Login & registration page
│   ├── result.html               #   - Disease diagnosis results page
│   └── chatbot.html              #   - AgriBot AI chatbot interface
│
├── static/                       # Frontend static assets
│   └── style.css                 #   - Global CSS styles (23 KB)
│
├── uploads/                      # Uploaded images directory (runtime)
└── PlantVillage/                 # Dataset directory (not committed)
    └── PlantVillage/
        ├── Pepper__bell___Bacterial_spot/
        ├── Pepper__bell___healthy/
        ├── Potato___Early_blight/
        ├── ...
        └── Tomato_healthy/
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git
- ~500 MB disk space (for TensorFlow + model)

### Step 1: Clone the Repository

```bash
git clone https://github.com/navinbadode19-glitch/Plant_Disease_Project.git
cd Plant_Disease_Project
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/Mac
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```env
GROQ_API_KEY=your_groq_api_key_here
FLASK_SECRET_KEY=your_super_secret_session_key
```

> 💡 **Get a free Groq API key** at [https://console.groq.com](https://console.groq.com) — required for the AI chatbot and cloud vision features. The local CNN model works without an API key.

### Step 5: Download Dataset (For Training Only)

If you want to retrain the model, download the **PlantVillage** dataset:

1. Download from [Kaggle - PlantVillage Dataset](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset)
2. Extract and place category folders under: `PlantVillage/PlantVillage/`
3. Ensure folder names match the entries in `class_names.txt`

> ℹ️ **Note**: The pre-trained model (`plant_disease_model.keras`) is included in the repository, so you can skip this step if you just want to run the application.

---

## 🚀 Usage Guide

### 1. Start the Web Application

```bash
python app.py
```



### 2. Train the Model (Optional)

```bash
python train.py
```

This will:
- Load the PlantVillage dataset from `PlantVillage/PlantVillage/`
- Build MobileNetV2 architecture with frozen base weights
- Train for 10 epochs with 80/20 train-validation split
- Save the trained model to `plant_disease_model.keras`

### 3. Verify Model Integrity

```bash
python verify_model.py
```

Runs structural asserts on model layers, input/output shapes, and mock inference.

### 4. Run CLI Prediction

```bash
python predict.py <path_to_image>

# Example:
python predict.py uploads/test_leaf.jpg
```

---

## 📈 Development Phases

The project was developed through a systematic 10-phase pipeline:

| Phase | Name | Description |
|-------|------|-------------|
| **1** | Environment Setup | Installed TensorFlow and dependencies; resolved h5py/NumPy compatibility issues |
| **2** | Dataset Preparation | Selected 15 target categories from the PlantVillage database |
| **3** | Dataset Verification | Fixed nested folder structures, aligned alphabetical class lists, verified 20,638 image count and 80/20 split statistics |
| **4** | Model Training | Configured MobileNetV2 transfer learning with frozen ImageNet base, Random Data Augmentation, and Dropout(0.3) head |
| **5** | Diagnostics & Bug Fix | Resolved critical double-preprocessing bug causing 99% `Tomato_Late_blight` for all inputs |
| **6** | Web Interface & Routing | Built Flask endpoints for user sessions, image upload, and AI chat |
| **7** | Database Persistence | Structured SQLite schemas for user accounts and diagnostic history |
| **8** | Multilingual Localization | Integrated translation dictionaries for Hindi, Tamil, Telugu, and Marathi |
| **9** | Intelligent Advisories | Implemented weather-smart advisories and growth-stage soil nutrient calculator |
| **10** | QA & Script Verification | Wrote `verify_model.py` and `predict.py` for model shape asserts and mock predictions |

---

## 🖼️ Screenshots

<!-- 
Add your screenshots here! Example:
![Dashboard](screenshots/dashboard.png)
![Disease Result](screenshots/result.png)
![AgriBot Chat](screenshots/chatbot.png)
-->

> 📷 *Screenshots coming soon — run the app locally to explore the full UI.*

---

## 🔑 API Keys & Configuration

| Variable | Required | Source | Description |
|----------|----------|--------|-------------|
| `GROQ_API_KEY` | Optional* | [console.groq.com](https://console.groq.com) | Powers AI chatbot & cloud vision diagnosis |
| `FLASK_SECRET_KEY` | Recommended | Generate any random string | Secures Flask session cookies |

> \* The local CNN model works fully offline. The Groq API key is only needed for the AI chatbot and cloud-based vision features.

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/your-feature`)
3. **Commit** your changes (`git commit -m 'Add some feature'`)
4. **Push** to the branch (`git push origin feature/your-feature`)
5. **Open** a Pull Request

### Ideas for Contribution
- Add support for more crops and diseases
- Improve model accuracy with data augmentation
- Add more language translations
- Implement mobile-responsive UI improvements
- Add REST API endpoints for mobile app integration

---

## 👨‍💻 Author

**Navin Badode**

- GitHub: [@navinbadode19-glitch](https://github.com/navinbadode19-glitch)

---



## 🙏 Acknowledgements

- **PlantVillage Dataset** — [Kaggle](https://www.kaggle.com/datasets/abdallahalidev/plantvillage-dataset)
- **MobileNetV2** — [Google Research](https://arxiv.org/abs/1801.04381)
- **Groq** — [groq.com](https://groq.com) for free, fast LLM inference
- **TensorFlow / Keras** — [tensorflow.org](https://www.tensorflow.org/)
- **Flask** — [flask.palletsprojects.com](https://flask.palletsprojects.com/)

---

<p align="center">
  🌾 <strong>Built with ❤️ for Indian Farmers</strong> 🌾
</p>
