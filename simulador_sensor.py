import time
import random
from datetime import datetime

OUTPUT_FILE = "sensor_data.txt"

print(f"A simular sensor em: {OUTPUT_FILE}")
print("Pressiona Ctrl+C para parar.")

try:
    while True:
        # 1.gerar dados normais na maioria das vezes
        temp = round(random.uniform(20.0, 30.0), 2)
        hum = round(random.uniform(40.0, 60.0), 2)

        # 2.a cada 10 ciclos, gera um valor alarmante para testar alarmística
        if random.randint(1, 10) == 10:
            temp = round(random.uniform(55.0, 80.0), 2)
            print(">>> GERADO VALOR DE ALERTA! <<<")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        linha = f"{timestamp};{temp};{hum}\n"

       
        with open(OUTPUT_FILE, "a") as f:
            f.write(linha)

        print(f"[SENSOR] Escreveu: {linha.strip()}")
        
        #espera 2 segundos entre leituras
        time.sleep(2)

except KeyboardInterrupt:
    print("\nSimulação terminada.")
