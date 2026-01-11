import os
import time
import re
from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
from google import genai
from fpdf import FPDF

# --- YAPILANDIRMA ---
load_dotenv()
app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
RAG_FOLDER = "RAG files"
FONT_FOLDER = "fonts"
FONT_NORMAL = os.path.join(FONT_FOLDER, "TIMES.ttf")
FONT_BOLD = os.path.join(FONT_FOLDER, "TIMESBD.ttf")

for folder in [UPLOAD_FOLDER, RAG_FOLDER, FONT_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# --- YARDIMCI FONKSİYONLAR ---
def extract_score_from_text(text):
    """
    Extract score from text using multiple methods
    """
    # Method 1: Direct number patterns
    patterns = [
        r'Puan\s*[:\-]?\s*(\d{1,3})',
        r'Skor\s*[:\-]?\s*(\d{1,3})',
        r'(\d{1,3})\s*/\s*100',
        r'Score\s*[:\-]?\s*(\d{1,3})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                score = int(match.group(1))
                if 0 <= score <= 100:
                    return score
            except:
                continue
    
    # Method 2: Look for numbers in context
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in ['puan', 'skor', 'score']):
            # Check this line and next 2 lines for numbers
            for j in range(i, min(i+3, len(lines))):
                numbers = re.findall(r'\b(\d{1,3})\b', lines[j])
                for num in numbers:
                    try:
                        score = int(num)
                        if 0 <= score <= 100:
                            return score
                    except:
                        continue
    
    return 0  # Default if no score found

# PDF Sınıfı
class PDFReport(FPDF):
    FONT_NAME = "Custom-Font" 
    def __init__(self):
        super().__init__()
        if os.path.exists(FONT_NORMAL):
            self.add_font(self.FONT_NAME, "", FONT_NORMAL, uni=True)
        if os.path.exists(FONT_BOLD):
            self.add_font(self.FONT_NAME, "B", FONT_BOLD, uni=True)

    def header(self):
        self.set_font(self.FONT_NAME, 'B', 14)
        self.cell(0, 10, "PROJE DEĞERLENDİRME RAPORU", ln=True, align='C')
        self.ln(5)

    def write_markdown_line(self, line):
        self.set_font(self.FONT_NAME, '', 11)
        line = line.strip()
        if line.startswith(('* ', '- ')):
            self.write(8, "  • ")
            line = line[2:]
        parts = re.split(r'(\*\*.*?\*\*)', line)
        for part in parts:
            if part.startswith('**') and part.endswith('**'):
                self.set_font(self.FONT_NAME, 'B', 11)
                self.write(8, part.replace('**', ''))
                self.set_font(self.FONT_NAME, '', 11)
            else:
                self.write(8, part)
        self.ln(8)

def upload_rag_files(client, rag_folder_name):
    uploaded_rag_files = []
    if not os.path.exists(rag_folder_name): 
        return uploaded_rag_files
    for item in os.listdir(rag_folder_name):
        rag_file_path = os.path.join(rag_folder_name, item)
        if os.path.isfile(rag_file_path):
            try:
                uploaded_file = client.files.upload(file=rag_file_path)
                while uploaded_file.state.name == "PROCESSING":
                    time.sleep(1)
                    uploaded_file = client.files.get(name=uploaded_file.name)
                if uploaded_file.state.name == "ACTIVE":
                    uploaded_rag_files.append(uploaded_file)
            except Exception as e: 
                print(f"RAG Hatası ({item}): {e}")
    return uploaded_rag_files

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"success": False, "error": "Dosya seçilmedi"})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "error": "Geçersiz dosya"})

    # 1. Dosyayı Kaydet
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # 2. RAG ve Birincil Dosya Yükleme
        rag_files = upload_rag_files(client, RAG_FOLDER)
        primary_file = client.files.upload(file=file_path)

        while primary_file.state.name == "PROCESSING":
            time.sleep(1)
            primary_file = client.files.get(name=primary_file.name)
        
        # Soru Dosyasını Oku
        questions_path = "question-dataset.txt"
        with open(questions_path, "r", encoding="utf-8") as f:
            questions_list = [line.strip() for line in f if line.strip()]
        questions_text = "\n".join([f"{i+1}. {q}" for i, q in enumerate(questions_list)])

        # 3. Model 1: Genel Değerlendirme (Gemini 2.5 Flash)
        main_prompt = (
            "Bu proje teklifi belgesini baştan sona inceleyin. RAG belgelerini bağlam olarak kullanın.\n"
            "Şunları yapın:\n"
            "1. Proje Başlığı: [BAŞLIK] formatında proje adını belirtin.\n"
            "2. Projenin temel özelliklerini listeleyin.\n"
            "3. Projeyi ekteki belgelerdeki 3 boyuta göre ayrı başlıklarla değerlendirin. Paragraf şeklinde detaylı bir şekilde değerlendir. Başlık: 'Projenin Belirlenen Kriterlere Göre Değerlendirilmesi'\n"
            "4. Olası başarısızlık risklerini açıklayın.\n"
            "5. Projeyle ilgili kritik ek sorular oluşturun.\n"
            "7. Puan: [X]/100 formatında kesin bir puan verin ve gerekçesini belirtin. Puanı [X] formatında ve sayısal olarak belirtin. Örnek: Puan: 85/100\n"
            "Yanıtı resmi bir proje raporu formatında sunun. Lütfen puanı açık ve belirgin bir şekilde belirtin."
        )

        main_response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=[primary_file] + rag_files + [main_prompt]
        )
        main_text = main_response.text

        # 4. Model 2: Soru Seti Cevapları (Gemini 2.5 Flash Lite)
        lite_prompt = (
            "Sana verilen dökümana göre sadece aşağıdaki soruları yanıtla.\n"
            "Yanıt formatı: **Soru No:** [Soru]\n"
            "**Karar:** [EVET/KISMEN/HAYIR]\n"
            "**Alıntı:** \"...\"\n"
            "**Açıklama:** [Açıklama]\n\n"
            f"Sorular:\n{questions_text}"
        )

        lite_response = client.models.generate_content(
            model="gemini-2.5-flash-lite", 
            contents=[primary_file] + [lite_prompt]
        )
        lite_text = lite_response.text

        # --- VERİ AYIKLAMA (REGEX) ---
        
        # Puanı bul: Multiple patterns to catch different formats
        proje_puani = 0
        puan_patterns = [
            # Pattern 1: "Puan: 85/100" or "Puan: 85 / 100"
            r'Puan\s*[:\-]?\s*(\d{1,3})\s*(?:/\s*100)?',
            
            # Pattern 2: "Skor: [85]" or "Puan: [85]"
            r'(?:Puan|Skor)\s*[:\-]?\s*\[(\d{1,3})\]',
            
            # Pattern 3: "85/100" anywhere in the text (as fallback)
            r'(\d{1,3})\s*/\s*100\b',
            
            # Pattern 4: "Puan: 85 (Gerekçe...)"
            r'Puan\s*[:\-]?\s*(\d{1,3})\s*(?:\(|olarak|-)',
            
            # Pattern 5: Looking for the specific section header
            r'7\.\s*(?:Puan|Skor).*?(\d{1,3})',
        ]

        # First try to find in the main text
        for pattern in puan_patterns:
            puan_match = re.search(pattern, main_text, re.IGNORECASE)
            if puan_match:
                try:
                    proje_puani = int(puan_match.group(1))
                    if 0 <= proje_puani <= 100:
                        print(f"Puan bulundu (pattern): {proje_puani}")
                        break  # Found a valid score
                except (ValueError, IndexError):
                    continue

        # If still not found, try helper function
        if proje_puani == 0:
            proje_puani = extract_score_from_text(main_text)
            if proje_puani > 0:
                print(f"Puan bulundu (helper): {proje_puani}")

        # If still not found, try to extract from the "Puan:" section in split parts
        if proje_puani == 0:
            parts = re.split(r'(?i)(7\.\s*Puan:|Puan:|Skor:)', main_text, maxsplit=1)
            if len(parts) >= 3:
                puan_section = parts[1] + parts[2]
                for pattern in puan_patterns:
                    puan_match = re.search(pattern, puan_section, re.IGNORECASE)
                    if puan_match:
                        try:
                            proje_puani = int(puan_match.group(1))
                            if 0 <= proje_puani <= 100:
                                print(f"Puan bulundu (section): {proje_puani}")
                                break
                        except:
                            continue

        # Log if score extraction failed
        if proje_puani == 0:
            print(f"UYARI: Puan bulunamadı. İlk 500 karakter: {main_text[:500]}...")
        else:
            print(f"Puan başarıyla çıkarıldı: {proje_puani}")

        # Başlığı bul: Improved title extraction
        baslik_match = re.search(
            r'(?:Proje\s*(?:Başlığı|Adı|İsmi)|Başlık|Title)\s*[:\-]?\s*(.*?)(?:\n|$)', 
            main_text, 
            re.IGNORECASE
        )
        safe_title = "proje_analiz_raporu"
        
        if baslik_match:
            raw_title = baslik_match.group(1).strip()
            # Başlığın başındaki ve sonundaki [ ] veya # gibi işaretleri temizle
            raw_title = re.sub(r'^[\[#\s]+|[\]#\s]+$', '', raw_title)
            # Dosya adı için temizlik
            safe_title = re.sub(r'[^\w\s-]', '', raw_title).replace(' ', '_')[:60]
            if not safe_title:
                safe_title = "proje_analiz_raporu"

        # --- METİN BİRLEŞTİRME (Sıralı Enjeksiyon) ---
        # 7. maddeyi (Puan) ayırıp araya Soru Setini sokuyoruz
        parts = re.split(r'(?i)(7\.\s*Puan:|Puan:|Skor:)', main_text, maxsplit=1)
        
        final_full_text = ""
        if len(parts) >= 3:
            final_full_text += parts[0].strip() + "\n\n"
            final_full_text += "### 6. Soru Seti Cevapları\n"
            final_full_text += lite_text + "\n\n"
            final_full_text += "### " + parts[1] + parts[2]
        else:
            final_full_text = main_text + "\n\n### 6. Soru Seti Cevapları\n" + lite_text

        # --- PDF OLUŞTURMA ---
        output_filename = f"{safe_title}_{int(time.time())}.pdf"
        pdf_path = os.path.join(UPLOAD_FOLDER, output_filename)

        pdf = PDFReport()
        pdf.add_page()


        lines = final_full_text.split('\n')
        for line in lines:
            if line.startswith('###'):
                pdf.ln(4)
                pdf.set_font(pdf.FONT_NAME, 'B', 12)
                pdf.write(10, line.replace('#', '').strip())
                pdf.ln(10)
            elif line.startswith('---'):
                pdf.line(10, pdf.get_y(), 200, pdf.get_y())
                pdf.ln(5)
            elif line.strip():
                pdf.write_markdown_line(line)

        pdf.output(pdf_path)

        return jsonify({
            "success": True, 
            "filename": output_filename,
            "score": proje_puani,
            "message": f"Rapor başarıyla oluşturuldu. Puan: {proje_puani}/100" if proje_puani > 0 else "Rapor başarıyla oluşturuldu (Puan bulunamadı)"
        })

    except Exception as e:
        print(f"Hata detayı: {e}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/download/<filename>')
def download(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)