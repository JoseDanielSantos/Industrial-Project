from flask import Flask, render_template, send_file, send_from_directory
from fpdf import FPDF
from elasticsearch import Elasticsearch
from datetime import datetime
import io

app = Flask(__name__)

ES_HOST = "http://localhost:9200"
ES_USER = "elastic"
ES_PASS = "changeme" 
LOGO_PATH = "PICadvanced_logo.png"


class PDF(FPDF):
    def header(self):
        try:
            self.image(LOGO_PATH, 10, 8, 40)
        except: pass
        self.set_font('Helvetica', 'B', 15)
        self.cell(80)
        self.cell(80, 10, 'Clean Room Telemetry Report', 0, 0, 'R')
        self.ln(20)
        self.set_draw_color(216, 27, 96)
        self.set_line_width(1)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}}', 0, 0, 'C')

def gerar_pdf_bytes():
    # 1. Buscar Dados
    es = Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASS), verify_certs=False)
    res = es.search(index="sala_limpa", size=50, sort=[{"timestamp": "desc"}])
    data = [hit['_source'] for hit in res['hits']['hits']]

    # 2. Criar PDF
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)

    # Info
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "1. General Information", 0, 1)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.cell(0, 6, "Location: Clean Room A", 0, 1)
    pdf.ln(5)

    # Tabela
    pdf.set_font("Helvetica", 'B', 10)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(50, 8, "Timestamp", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "Sensor", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "Metric", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "Value", 1, 1, 'C', fill=True)

    pdf.set_font("Helvetica", size=9)
    for row in data:
        ts = row.get('timestamp', 'N/A').replace("T", " ").split(".")[0]
        pdf.cell(50, 7, ts, 1)
        pdf.cell(40, 7, str(row.get('sensor_id')), 1)
        pdf.cell(40, 7, str(row.get('metric_type')), 1)
        
        valor = row.get('metric_value', 0)
        if isinstance(valor, (int, float)) and valor > 25 and row.get('metric_type') == 'temperatura':
             pdf.set_text_color(220, 50, 50)
        else:
             pdf.set_text_color(0)
        
        pdf.cell(30, 7, str(valor), 1, 1, 'R')
        pdf.set_text_color(0)

    return pdf.output()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gerar-relatorio')
def download_report():
    try:
        pdf_content = gerar_pdf_bytes()
        #envia o PDF para o browser como um download
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f"Relatorio_SalaLimpa_{datetime.now().strftime('%Y%m%d')}.pdf"
        )
    except Exception as e:
        return f"Erro a gerar PDF: {e}"


@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    #corre o servidor na porta 5000
    app.run(host='0.0.0.0', port=5000, debug=True)
