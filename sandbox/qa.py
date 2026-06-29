import os
import time
import json
from dotenv import load_dotenv
from groq import Groq
import fitz  # PyMuPDF

# .env dosyasındaki API anahtarını yükler
load_dotenv()

# ----------------------------
# 1. Yardımcı Fonksiyon: PDF Metni Çıkarma
# ----------------------------
def extract_pdf_text(path):
    """PDF dosyasındaki tüm sayfaları okur ve metin olarak döndürür."""
    text = ""
    try:
        with fitz.open(path) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        print(f"❌ PDF okuma hatası: {e}")
        return ""

# ----------------------------
# 2. Kurulum ve Hazırlık
# ----------------------------
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct" # Mevcut model adınızı buraya yazın

pdf_path = "uploads/1249064_Proje_Onerisi.pdf"
document_text = extract_pdf_text(pdf_path)

if not document_text:
    print("⚠️ PDF metni boş veya dosya bulunamadı!")
    exit()

print(f"✅ Metin uzunluğu: {len(document_text)} karakter")

# Soruları oku
with open("question-dataset.txt", "r", encoding="utf-8") as f:
    questions = [q.strip() for q in f if q.strip()]

print(f"📋 Toplam soru: {len(questions)}")

# ----------------------------
# 3. SORU-CEVAP DÖNGÜSÜ
# ----------------------------
results = []
output_file = "analiz_sonuclari.json"

for idx, question in enumerate(questions, start=1):
    print(f"\n--- Soru {idx}/{len(questions)} İşleniyor ---")
    
    start_time = time.time()
    
    # Her soru için özelleştirilmiş prompt
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

    try:
        # API Çağrısı
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        answer_text = response.choices[0].message.content
        elapsed = time.time() - start_time
        
        # Sonucu listeye ekle
        res_data = {
            "soru_no": idx,
            "soru": question,
            "cevap": answer_text,
            "sure_sn": round(elapsed, 2)
        }
        results.append(res_data)
        
        # Ekranda göster
        print(answer_text)
        print(f"⏱️ Süre: {elapsed:.2f} sn")
        time.sleep(5)  # Her soru arasında 2 saniye bekle

    except Exception as e:
        print(f"❌ Soru {idx} işlenirken hata oluştu: {e}")
        continue # Hata olsa da sonraki soruya geç

# ----------------------------
# 4. Kayıt ve Özet
# ----------------------------
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=4)

print(f"\n✅ İşlem tamamlandı. Sonuçlar '{output_file}' dosyasına kaydedildi.")