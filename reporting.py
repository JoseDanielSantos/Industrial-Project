from fpdf import FPDF
from elasticsearch import Elasticsearch
from datetime import datetime

# --- CONFIGURAÇÕES ---
ES_HOST = "http://localhost:9200"
ES_USER = "elastic"
ES_PASS = "changeme" 
LOGO_PATH = "PICadvanced_logo.png"
OUTPUT_FILENAME = "CleanRoom_Report.pdf"

class PDF(FPDF):
    def header(self):
        try:
            self.image(LOGO_PATH, 10, 8, 40)
        except:
            pass         
        self.set_font('Helvetica', 'B', 15)
        self.cell(80)
        # Title
        self.cell(80, 10, 'Clean Room Telemetry Report', 0, 0, 'R')
        self.ln(20)
        
        
        self.set_draw_color(216, 27, 96) #cor vermelha da PIC
        self.set_line_width(1)
        self.line(10, 25, 200, 25)
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()}/{{nb}} - Generated automatically by Telemetry System', 0, 0, 'C')

def get_data():
    #liga ao Elastic
    es = Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASS), verify_certs=False)
    
    #ver últimos 20 registos - depois tenho de mudar
    res = es.search(index="sala_limpa", size=20, sort=[{"timestamp": "desc"}])
    return [hit['_source'] for hit in res['hits']['hits']]

def generate_pdf():
    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    # 1.INFO GERAL
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "1. General Information", 0, 1)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Date generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 0, 1)
    pdf.cell(0, 6, "Location: Clean Room A - Aveiro", 0, 1)
    pdf.cell(0, 6, "System Status: ONLINE", 0, 1)
    pdf.ln(10)

    # 2.ESPAÇO PARA TEXTO DA EMPRESA (tenho de ver o que alterar depois)
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "2. Technical Notes", 0, 1)
    pdf.set_font("Helvetica", size=10)
    pdf.multi_cell(0, 6, "This report contains the latest telemetry data acquired via the Zigbee sensor network. Atmospheric conditions must be maintained within the specified thresholds to ensure the quality of optical components.")
    pdf.ln(5)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(0, 6, "[Additional comments from Engineering Dept. can be inserted here via configuration...]")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(10)

    try:
        data = get_data()
    except Exception as e:
        print(f"Erro ao ligar ao Elastic: {e}")
        return

    # 3.TABELA DE DADOS
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "3. Sensor Data Logs (Last 20 entries)", 0, 1)
    
    #Cabeçalho da tabela
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", 'B', 10)
    pdf.cell(50, 8, "Timestamp", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "Sensor ID", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "Metric", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "Value", 1, 1, 'C', fill=True)

    #Linhas da tabela
    pdf.set_font("Helvetica", size=9)
    for row in data:
        ts = row.get('timestamp', 'N/A')
        try:
            ts = ts.replace("T", " ").split(".")[0]
        except: pass

        pdf.cell(50, 7, ts, 1)
        pdf.cell(40, 7, str(row.get('sensor_id', 'N/A')), 1)
        pdf.cell(40, 7, str(row.get('metric_type', 'N/A')), 1)
        
        #verificar se valor é crítico (> 25) para pintar de vermelho
        valor = row.get('metric_value', 0)
        pdf.set_text_color(0) # Preto normal
        if isinstance(valor, (int, float)) and valor > 25 and row.get('metric_type') == 'temperatura':
             pdf.set_text_color(220, 50, 50) # Vermelho
             
        pdf.cell(30, 7, str(valor), 1, 1, 'R')
        pdf.set_text_color(0) # Reset cor

    pdf.output(OUTPUT_FILENAME)
    print(f"Sucesso! Relatório gerado: {OUTPUT_FILENAME}")

if __name__ == "__main__":
    generate_pdf()
