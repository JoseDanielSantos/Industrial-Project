from flask import Flask, render_template, send_file, send_from_directory, request
from fpdf import FPDF
from elasticsearch import Elasticsearch
from datetime import datetime
import io
import statistics

app = Flask(__name__)

# --- CONFIGURATION ---
ES_HOST = "http://localhost:9200"
ES_USER = "elastic"
ES_PASS = "changeme" 
LOGO_PATH = "PICadvanced_logo.png"
INDEX_NAME = "salalimpa-*" 


THRESHOLDS = {
    'temp': 25.0,   # > 25 C
    'hum': 60.0,    # > 60 %
    'vib': 50.0,    # > 50 (Adjust based on your raw values)
    'pm1': 20.0,    # Example limit
    'pm25': 35.0,   # Standard limit
    'pm10': 50.0    # Standard limit
}

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

def gerar_pdf_bytes(time_range, metricas_escolhidas):
    es = Elasticsearch(ES_HOST, basic_auth=(ES_USER, ES_PASS), verify_certs=False)
    
    query = {
        "range": {
            "@timestamp": {
                "gte": f"now-{time_range}", 
                "lte": "now"
            }
        }
    }

    limit = 1000
    if 'w' in time_range or 'M' in time_range:
        limit = 3000
    
    res = es.search(index=INDEX_NAME, query=query, size=limit, sort=[{"@timestamp": "desc"}])
    raw_data = [hit['_source'] for hit in res['hits']['hits']]

    processed_rows = []

    stats_collector = {
        'temp': [], 'hum': [], 'vib': [], 
        'pm1': [], 'pm25': [], 'pm10': []
    }

    for row in raw_data:
        ts = row.get('@timestamp', 'N/A').replace("T", " ").split(".")[0]
        
        payload = row.get('payload', {})
        if not payload: payload = row.get('payload_data', {})

        def process_metric(key_user, key_tech_list, label, unit):
            if key_user in metricas_escolhidas:
                val = None
                for k in key_tech_list:
                    if k in payload:
                        val = payload[k]
                        break
                
                if val is not None and isinstance(val, (int, float)):
                    if key_user in stats_collector:
                        stats_collector[key_user].append(val)
                    
                    limit_val = THRESHOLDS.get(key_user, 999999)
                    is_alert = val > limit_val
                    
                    processed_rows.append({
                        'ts': ts,
                        'metric': label,
                        'val': val,
                        'unit': unit,
                        'alert': is_alert
                    })

        process_metric('temp', ['temperature', 'temperature_2'], 'Temperature', '°C')
        process_metric('hum',  ['humidity', 'temperature_3'],    'Humidity', '%')
        process_metric('vib',  ['vibration', 'temperature_4'],   'Vibration', 'vib')
        process_metric('pm1',  ['pm1', 'temperature_5'],         'PM 1.0', 'ug/m3')
        process_metric('pm25', ['pm25', 'temperature_1'],        'PM 2.5', 'ug/m3')
        process_metric('pm10', ['pm10', 'temperature_6'],        'PM 10', 'ug/m3')

    pdf = PDF()
    pdf.alias_nb_pages()
    pdf.add_page()
    
    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "1. General Information", 0, 1)
    pdf.set_font("Helvetica", size=10)
    pdf.cell(0, 6, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", 0, 1)
    pdf.cell(0, 6, f"Time Range Requested: Last {time_range}", 0, 1)
    pdf.cell(0, 6, f"Total Records Found: {len(processed_rows)}", 0, 1)
    pdf.ln(5)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "2. Statistics Summary", 0, 1)
    pdf.set_font("Helvetica", size=10)
    
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(40, 7, "Metric", 1, 0, 'C', fill=True)
    pdf.cell(30, 7, "Average", 1, 0, 'C', fill=True)
    pdf.cell(30, 7, "Max", 1, 0, 'C', fill=True)
    pdf.cell(30, 7, "Min", 1, 1, 'C', fill=True)
    
    pdf.set_font("Helvetica", size=10)
    
    has_stats = False
    metric_labels = {
        'temp': 'Temperature', 
        'hum': 'Humidity', 
        'vib': 'Vibration',
        'pm1': 'PM 1.0',
        'pm25': 'PM 2.5',
        'pm10': 'PM 10'
    }
    
    for key in metricas_escolhidas:
        values = stats_collector.get(key, [])
        if values:
            has_stats = True
            avg_val = statistics.mean(values)
            max_val = max(values)
            min_val = min(values)
            
            label = metric_labels.get(key, key)
            pdf.cell(40, 7, label, 1)
            pdf.cell(30, 7, f"{avg_val:.2f}", 1, 0, 'R')
            pdf.cell(30, 7, f"{max_val}", 1, 0, 'R')
            pdf.cell(30, 7, f"{min_val}", 1, 1, 'R')
            
    if not has_stats:
        pdf.cell(0, 7, "No data found for selected metrics.", 1, 1, 'C')
        
    pdf.ln(10)

    pdf.set_font("Helvetica", 'B', 12)
    pdf.cell(0, 10, "3. Detailed Log", 0, 1)
    
    pdf.set_font("Helvetica", 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    
    pdf.cell(50, 8, "Timestamp", 1, 0, 'C', fill=True)
    pdf.cell(50, 8, "Metric", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "Value", 1, 1, 'C', fill=True)

    pdf.set_font("Helvetica", size=9)
    
    row_count = 0
    max_pdf_rows = 500 

    for row in processed_rows:
        if row_count > max_pdf_rows:
            pdf.cell(140, 6, "... (Truncated for PDF size) ...", 1, 1, 'C')
            break

        pdf.cell(50, 6, row['ts'], 1)
        pdf.cell(50, 6, row['metric'], 1)
        
        if row['alert']:
            pdf.set_text_color(220, 50, 50) # Red
            pdf.set_font("Helvetica", 'B', 9) # Bold
        
        pdf.cell(40, 6, f"{row['val']} {row['unit']}", 1, 1, 'R')

        pdf.set_text_color(0)
        pdf.set_font("Helvetica", size=9)
        row_count += 1

    return pdf.output(dest='S').encode('latin-1')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gerar-relatorio')
def download_report():
    try:
        time_range = request.args.get('dias', default='1d')
        metricas = request.args.getlist('metricas')
        
        if not metricas:
            metricas = ['temp', 'hum', 'pm25']

        pdf_content = gerar_pdf_bytes(time_range, metricas)
        
        filename = f"Report_{time_range}_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        
        return send_file(
            io.BytesIO(pdf_content),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        import traceback
        return f"<h1>Error generating PDF</h1><pre>{traceback.format_exc()}</pre>"

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
