import datetime
import os
import time

hostname = "192.168.56.1"

NOME_ARQUIVO_LOG = "access.log"
PORTA_ALVO = 9999


os.system("ping -n 4 " + hostname)

for i in range(110):
    if(i == 100):
        with open(NOME_ARQUIVO_LOG, 'w') as log_file:
            log_file.write(f"--- Log de Tráfego de Rede (IP: {hostname}, Porta: {PORTA_ALVO}) ---\n")
            log_file.write("Mais de 100 requisições detectadas. Possivel DDOS")
        print(f"DDOS detectado no IP: {hostname}, e na porta: {PORTA_ALVO}")
        print(f"IP: {hostname} bloqueado")
        break
    
    os.system("cls")
    os.system("curl " + hostname +":9999 -X POST")
    time.sleep(0.01) #pausa por 0.1 segundo

