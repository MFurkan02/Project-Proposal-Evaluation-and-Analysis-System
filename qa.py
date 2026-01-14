import os
import time
from dotenv import load_dotenv
from groq import Groq
import fitz  # PyMuPDF

load_dotenv()

# ----------------------------
# 1. Groq Client Setup
# ----------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"

# ----------------------------
# 2. Extract PDF TEXT
# ----------------------------
print("📄 PDF metni çıkarılıyor...")
pdf_path = "uploads/1249064_Proje_Onerisi 2.pdf"
document_text = extract_pdf_text(pdf_path)

print(f"✅ Metin uzunluğu: {len(document_text)} karakter")

# ----------------------------
# 3. Read Questions
# ----------------------------
with open("question-dataset.txt", "r", encoding="utf-8") as f:
    questions = [q.strip() for q in f if q.strip()]

print(f"📋 Toplam soru: {len(questions)}")

# ----------------------------
# 4. ONE-BY-ONE QUESTION ANALYSIS
# ----------------------------
results = []
total_start = time.time()

for idx, question in enumerate(questions, start=1):
    print(f"\n🔍 Soru {idx} analiz ediliyor...")

    start_time = time.time()

    prompt = f"""
AŞAĞIDAKİ PROJE TEKLİF METNİNİ KULLANARAK SORUYU YANITLA.

=== PROJE METNİ BAŞLANGIÇ ===
{document_text}
=== PROJE METNİ BİTİŞ ===

SORU:
{question}

CEVAP FORMATI (ZORUNLU):
- Soru: {question}
- Karar: [EVET], [KISMEN] veya [HAYIR]
- Alıntı: "Metinden birebir cümle"
- Analiz: Kısa ve teknik Türkçe açıklama
"""

    response = client.chat.completions.create(
        model=MODEL_ID,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.1
    )

    answer_text = response.choices[0].message.content
    elapsed = time.time() - start_time

    print(answer_text)
    print(f"⏱️ Süre: {elapsed:.2f} sn")

    results.append({
        "question_no": idx,
        "question": question,
        "answer": answer_text,
        "time": elapsed
    })

total_elapsed = time.time() - total_start

# ----------------------------
# 5. Summary
# ----------------------------
print("\n==============================")
print("✅ TÜM SORULAR TAMAMLANDI")
print(f"🧠 Toplam süre: {total_elapsed:.2f} sn")
print(f"📊 Ortalama süre / soru: {total_elapsed / len(questions):.2f} sn")
print("==============================")
