# Project Proposal Evaluation and Analysis System

An AI-powered web-based system designed to automatically evaluate project proposal documents
using Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG).
The system analyzes PDF-based project proposals, generates a structured evaluation report,
assigns a quantitative score, and presents the results through an interactive web interface.

This project was developed as a graduation project for the Computer Engineering Department
at Gebze Technical University.

---

## Features

- Upload and analyze project proposal PDFs
- Dual-model LLM architecture for improved evaluation quality
- Retrieval-Augmented Generation (RAG) support using reference documents
- Automatic project scoring (0–100)
- Structured evaluation report generation
- PDF report export
- Interactive frontend with progress tracking and score visualization
- Multilingual interface (Turkish / English)

---

## System Architecture

The system consists of three main components:

1. **Frontend**
   - Built with HTML, Tailwind CSS, and JavaScript
   - Provides file upload, progress visualization, score display, and PDF preview

2. **Backend**
   - Implemented using Flask (Python)
   - Handles file uploads, LLM requests, RAG integration, score extraction, and PDF generation

3. **AI Evaluation Layer**
   - Uses Google Gemini models:
     - `gemini-2.5-flash` for detailed project evaluation
     - `gemini-2.5-flash-lite` for structured question-based assessment
   - RAG documents are uploaded and used as contextual references during evaluation

---

## Technologies Used

- **Backend:** Python, Flask
- **Frontend:** HTML, Tailwind CSS, JavaScript
- **AI Models:** Google Gemini API
- **PDF Processing:** FPDF
- **Environment Management:** python-dotenv
- **Version Control:** Git & GitHub

---

## Project Structure

```text
Project-Proposal-Evaluation-and-Analysis-System/
│
├── app.py                     # Flask backend application
├── templates/
│   └── index.html              # Frontend UI
├── uploads/                    # Uploaded and generated PDF files
├── RAG files/                  # Reference documents for RAG
├── fonts/                      # Custom fonts for PDF generation
├── question-dataset.txt        # Evaluation question set
├── .env                        # Environment variables (API key)
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
