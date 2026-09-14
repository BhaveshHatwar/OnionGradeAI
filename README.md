# OnionGradeAI
AI-powered onion quality assessment prototype using the Gemini 3.5 Flash API to analyze onion images, evaluate size, color, shape, surface condition, and visible defects, and generate a standardized quality score and grade.

# 🧅 OnionGradeAI

### AI-Powered Onion Quality Assessment & Grading

OnionGradeAI is an **AI-powered prototype for assessing onion quality from images**. The system uses the **Gemini 2.5 Flash API** to analyze uploaded onion images and evaluate multiple visible quality parameters using a predefined onion-grading framework.

The goal is to reduce subjectivity in manual onion inspection and provide a **consistent, transparent, and easy-to-understand quality assessment**.

---

## 🎯 Problem

Traditional onion grading largely depends on visual inspection by human graders. Different graders may evaluate the same onion lot differently due to differences in experience, judgment, lighting conditions, and interpretation of quality parameters.

This can lead to:

* Inconsistent grading
* Disputes between farmers and buyers
* Difficulty maintaining standardized quality assessments
* Lack of a digital record of the grading decision

---

## 💡 Our Solution

OnionGradeAI allows a user to upload an image of an onion. The system sends the image to **Gemini 2.5 Flash through the Gemini API**, along with an onion-specific grading prompt.

Gemini analyzes the image and evaluates:

* 📏 Size
* 🎨 Colour
* ⚪ Shape
* 🧅 Surface condition
* 🩹 Visible defects and damage

The system then generates individual parameter scores, calculates an overall quality score, and assigns a grade.

---

## 🔄 How It Works

```text
        📷 Upload Onion Image
                 │
                 ▼
        🖼️ Image Processing
                 │
                 ▼
       🤖 Gemini 2.5 Flash
        Image Understanding
                 │
                 ▼
       🔍 Quality Assessment
      ┌──────────┼──────────┐
      │          │          │
    Size      Colour      Shape
      │          │          │
      └──────┬───┴──────────┘
             │
     Surface Condition
             │
      Defects / Damage
             │
             ▼
      📊 Weighted Scoring
             │
             ▼
       🏆 Final Grade
        A / B / C
             │
             ▼
      📋 Assessment Report
```

---

## 🧠 Technical Approach

The current prototype uses **Gemini 2.5 Flash's multimodal image-understanding capability through the Gemini API**.

A predefined grading prompt instructs the model to:

1. Verify whether the uploaded image contains an onion.
2. Analyze the visible characteristics of the onion.
3. Score each quality parameter from 0–100.
4. Apply predefined parameter weights.
5. Calculate the overall quality score.
6. Map the score to Grade A, B, or C.
7. Return the result in structured JSON format.

### Parameter Weights

| Parameter         | Weight |
| ----------------- | -----: |
| Size              |    20% |
| Colour            |    15% |
| Shape             |    15% |
| Surface Condition |    25% |
| Defects & Damage  |    25% |

### Grade Mapping

| Score    | Grade | Interpretation          |
| -------- | ----- | ----------------------- |
| 85–100   | A     | Premium                 |
| 65–84    | B     | Standard                |
| Below 65 | C     | Below Standard / Review |

---

## 🛡️ Image Validation

The system first checks whether the uploaded image actually contains an onion.

If the image is not an onion, the system rejects the input and asks the user to upload a clear onion image instead.

This prevents unrelated images from being accidentally processed as onion-quality assessments.

---

## 🖥️ Current Application

The prototype is built using **Streamlit** and provides:

* Image upload
* Optional contextual information
* AI-based onion analysis
* Overall quality score
* Grade classification
* Parameter-wise scores
* Explanation of individual scores
* Onion/non-onion validation
* Raw model output for debugging

---
## 🔐 API Key Setup

This project uses the Gemini API to analyze onion images.

For security reasons, the Gemini API key is not included in this repository.

### 1. Get a Gemini API key

Create your own Gemini API key.

### 2. Create a `.env` file

In the project root directory, create a file named:

`.env`

Add:

```env
GEMINI_APIKEY=your_own_api_key
## 🛠️ Technology Stack

**Frontend / Interface**

* Streamlit

**Programming Language**

* Python

**AI**

* Google Gemini API
* Gemini 2.5 Flash

**Image Processing**

* Pillow (PIL)

**Configuration**

* Python-dotenv

**Data Format**

* JSON

---

## 📁 Project Structure

```text
OnionGradeAI/
│
├── onion_grade_ai.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

> **Important:** `.env` should never be pushed to GitHub because it contains your Gemini API key.

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/OnionGradeAI.git
cd OnionGradeAI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

**macOS / Linux**

```bash
source venv/bin/activate
```

**Windows**

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Gemini API key

Create a `.env` file in the project directory:

```env
GEMINI_APIKEY=your_gemini_api_key_here
```

### 5. Run the application

```bash
streamlit run onion_grade_ai.py
```

The application will open in your browser.

---

## 🔐 API Key Security

The Gemini API key is loaded from an environment variable rather than being written directly into the source code.

**Never commit this file:**

```text
.env
```

Add it to `.gitignore`:

```text
.env
venv/
__pycache__/
*.pyc
```

If an API key has already been pushed to a public GitHub repository, **revoke/regenerate the key immediately**.

---

## 📊 Example Output

The system produces an assessment similar to:

```text
Overall Score: 87/100

Grade: A

Parameter Breakdown:

Size              90/100
Colour            88/100
Shape             86/100
Surface Condition 85/100
Defects & Damage  90/100

Overall Assessment:
The onion shows good visual quality with a healthy
appearance and minimal visible defects.
```

---

## ⚠️ Current Limitations

This is currently a **prototype**, not a certified commercial grading system.

The curre
