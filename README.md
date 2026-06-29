#  Project Proposal Evaluation and Analysis System

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg?style=for-the-badge\&logo=python)](https://www.python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3.3-black.svg?style=for-the-badge\&logo=flask)](https://flask.palletsprojects.com/)
[![Gemini](https://img.shields.io/badge/Google_Gemini-2.5-orange.svg?style=for-the-badge\&logo=google-gemini)](https://ai.google.dev/)
[![Tailwind](https://img.shields.io/badge/Tailwind_CSS-3.0-06B6D4.svg?style=for-the-badge\&logo=tailwind-css)](https://tailwindcss.com)

An advanced, corporate-grade web application designed to automatically evaluate academic and corporate project proposals using **Multi-Model LLM Architecture** and **Retrieval-Augmented Generation (RAG)**.

The system parses proposal documents, detects structural and operational risks, masks sensitive information, and generates official AI-assisted evaluation reports in PDF format.

> 🎓 **Graduation Project**
> Developed as a Graduation Project for the Department of Computer Engineering at **Gebze Technical University (GTU)**.

---

# 📚 Table of Contents

* [Overview](#-overview)
* [Core Features](#-core-features)
* [System Architecture](#-system-architecture)
* [Technical Pipelines](#-technical-pipelines)
* [Technology Stack](#-technology-stack)
* [Project Structure](#-project-structure)
* [Installation](#-installation)
* [Environment Variables](#-environment-variables)
* [Running the Application](#-running-the-application)
* [License](#-license)

---

# 📌 Overview

This platform automates the evaluation workflow of academic, institutional, and corporate project proposals by combining:

* **Large Language Models (LLMs)**
* **Retrieval-Augmented Generation (RAG)**
* **Semantic document parsing**
* **Regex-based validation**
* **Unicode-safe PDF generation**

The system is designed for organizations that require:

* Standardized proposal scoring
* Blind evaluation workflows
* Automated compliance verification
* AI-assisted auditing
* Structured reporting pipelines

---

# ✨ Core Features

## 📄 Intelligent PDF Proposal Parsing

* Upload and process `.pdf` project proposals
* Extract contextual content using **PyMuPDF**
* Assemble semantic context windows for LLM analysis

## 🧠 Multi-Model AI Evaluation Architecture

### Primary Evaluator — `gemini-2.5-flash`

Handles:

* Structural proposal analysis
* Risk assessment
* Budget and timeline validation
* Strategic consistency checks
* Final scoring generation (`0-100`)

### Cross-Examiner — `gemini-2.5-flash-lite`

Handles:

* Matrix-based auditing
* Deterministic Q&A validation
* Rule-based proposal inspection
* Citation extraction from proposal text

Outputs:

* `[EVET]`
* `[KISMEN]`
* `[HAYIR]`

Alongside direct proposal quotations (`Alıntı`) as evidence.

---

## 📚 Retrieval-Augmented Generation (RAG)

The application dynamically injects institutional reference files into the AI context pipeline.

Examples:

* Academic scoring rubrics
* Legal frameworks
* Corporate compliance policies
* Evaluation baselines

This minimizes hallucinations and ensures evaluations remain grounded within organizational standards.

---

## 🔒 PII & Sensitive Data Masking

The backend sanitizes administrative and sensitive information before report compilation.

Masked fields include:

* Project manager names
* Institutional identifiers
* Proposal numbers
* Organization names

Implemented using cascading Regex-based filtering pipelines.

---

## 📑 Unicode-Compliant PDF Report Generation

Generated reports support full Turkish UTF-8 rendering using embedded TrueType fonts.

Supported characters include:

* `ı`
* `ş`
* `ğ`
* `İ`
* `Ş`
* `Ğ`

The rendering engine also includes:

* Dynamic line wrapping
* Overflow protection
* Multi-cell paragraph rendering
* Structured section formatting

---

# 🏗️ System Architecture

```text
[User Upload (PDF)]
          │
          ▼
[PyMuPDF Parser]
          │
          ▼
[Text Extraction & Context Assembly]
          │
 ┌────────┴──────────────────────────────────────────┐
 │                                                   │
 ▼                                                   ▼

[Pipeline 1: Core Evaluator]              [Pipeline 2: Cross-Examiner]

Model: gemini-2.5-flash                  Model: gemini-2.5-flash-lite

Tasks:                                   Tasks:
- Structural Analysis                    - Matrix-Based Auditing
- Risk Detection                         - Constraint Validation
- Proposal Scoring                       - Evidence Extraction

          └──────────────┬──────────────┘
                         ▼

         [Regex Mining & Masking Layer]

                - Score Extraction
                - PII Sanitization
                - Formatting Cleanup

                         ▼

             [Unicode PDF Rendering Engine]

                - fpdf2 Renderer
                - DejaVu Font Binding
                - UTF-8 Protection
```

---

# ⚙️ Technical Pipelines

# 1️⃣ Ingestion & RAG Injection Pipeline

## Document Upload

When a user uploads a `.pdf` file:

1. The server uploads the document to the Google GenAI File API.
2. The backend continuously polls the file state until processing completes.
3. The file becomes available for semantic analysis.

Example polling logic:

```python
while primary_file.state.name == "PROCESSING":
    time.sleep(2)
```

---

## RAG Context Injection

The system dynamically scans the `RAG files/` directory and injects institutional reference files into the LLM context window.

Purpose:

* Prevent hallucinations
* Enforce organizational constraints
* Standardize evaluation behavior

---

# 2️⃣ Dual-Model LLM Coordination Strategy

## Primary Evaluator — `gemini-2.5-flash`

Responsible for:

* Deep semantic analysis
* Timeline consistency checks
* Budget integrity validation
* Operational dependency analysis
* Numerical proposal scoring

Output:

```text
Final Score: 87/100
```

---

## Granular Auditor — `gemini-2.5-flash-lite`

Processes the `question-dataset.txt` matrix.

Outputs structured decisions:

```text
[EVET]
[KISMEN]
[HAYIR]
```

Includes direct proposal excerpts as evidence.

---

# 3️⃣ Regex Post-Processing & PII Masking Layer

## Cascading Score Extraction

The system uses multiple Regex heuristics to reliably detect scores from varying LLM response formats.

```python
patterns = [
    r'Puan\s*[:\-]?\s*(\d{1,3})\s*(?:/\s*100)?',
    r'(?:Puan|Skor)\s*[:\-]?\s*\[(\d{1,3})\]',
    r'(\d{1,3})\s*/\s*100\b'
]
```

---

## Sensitive Information Removal

Administrative identifiers are stripped before PDF compilation.

Examples:

* `Proje Yürütücüsü`
* `Kuruluş`
* `Proje No`

---

# 4️⃣ Dynamic Font Binding & PDF Rendering Engine

The reporting engine is built using `fpdf2`.

## Features

* Unicode-safe rendering
* Turkish UTF-8 support
* Dynamic page overflow management
* Automatic paragraph wrapping
* Structured section formatting

## Font Integration

```python
pdf.add_font("DejaVu", "", "fonts/DejaVuSans.ttf", uni=True)
pdf.add_font("DejaVu", "B", "fonts/DejaVuSans-Bold.ttf", uni=True)
```

---

# 🧰 Technology Stack

| Layer                  | Technologies                       |
| ---------------------- | ---------------------------------- |
| Backend                | Python 3.10+, Flask                |
| AI Infrastructure      | Google Gemini API                  |
| RAG Context System     | Local Institutional Knowledge Base |
| Document Parsing       | PyMuPDF                            |
| PDF Rendering          | fpdf2                              |
| Environment Management | python-dotenv                      |
| Frontend               | HTML5, Tailwind CSS                |
| Icons                  | Font Awesome v6                    |
| Production Server      | Gunicorn                           |

---

# 📁 Project Structure

```text
Project-Proposal-Evaluation-and-Analysis-System/
│
├── app.py
├── question-dataset.txt
├── requirements.txt
├── .env.example
│
├── templates/
│   └── index.html
│
├── fonts/
│   ├── DejaVuSans.ttf
│   └── DejaVuSans-Bold.ttf
│
├── RAG files/
├── uploads/
├── logs/
│
└── sandbox/
    └── qa.py
```

---

# ⚡ Installation

# 1️⃣ Clone the Repository

```bash
git clone https://github.com/your-username/project-proposal-evaluation-system.git

cd project-proposal-evaluation-system
```

---

# 2️⃣ Create Environment Variables

Copy the example configuration file:

```bash
cp .env.example .env
```

Populate the environment variables:

```env
GEMINI_API_KEY=your_google_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

---

# 3️⃣ Create Virtual Environment

## Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

## Windows

```bash
venv\Scripts\activate
```

---

# 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🚀 Running the Application

Start the Flask development server:

```bash
python app.py
```

The application will become accessible at:

```text
http://localhost:5000
```

---


# 📄 License

This project is licensed under the MIT License.

---

# 👨‍💻 Author

Developed as a Graduation Project for:

**Gebze Technical University (GTU)**
Department of Computer Engineering
