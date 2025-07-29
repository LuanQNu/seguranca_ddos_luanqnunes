import pyshark
import datetime

# --- CONFIGURAÇÕES QUE VOCÊ PRECISA AJUSTAR ---
MEU_IP = "192.168.56.1" 
PORTA_ALVO = 9999
INTERFACE_DE_REDE = None
NUM_PACOTES = 10

# --- Nome do arquivo de saída (formato de texto) ---
NOME_ARQUIVO_LOG = "access.log"
# -----------------------------------------------

display_filter = f"(ip.src == {MEU_IP} or ip.dst == {MEU_IP}) and (tcp.port == {PORTA_ALVO} or udp.port == {PORTA_ALVO})"

print(f"Iniciando captura para IP: {MEU_IP} e Porta: {PORTA_ALVO}")
print(f"Filtro de exibição usado: {display_filter}")
print(f"Salvando tráfego formatado em: {NOME_ARQUIVO_LOG}")
print(f"Capturando {NUM_PACOTES if NUM_PACOTES else 'indefinidamente'} pacotes...")
print("Pressione Ctrl+C para parar a captura a qualquer momento se NUM_PACOTES for None.")

try:
    # Usamos only_summaries=True para obter uma versão mais leve do pacote,
    # que é boa para logs simples, mas nem todos os campos estarão disponíveis.
    # Se precisar de mais detalhes, remova only_summaries=True.
    capture = pyshark.LiveCapture(
        interface=INTERFACE_DE_REDE,
        display_filter=display_filter,
        only_summaries=True # Pega apenas um resumo para um log mais leve
    )

    # Abre o arquivo de log para escrita
    with open(NOME_ARQUIVO_LOG, 'w') as log_file:
        log_file.write(f"--- Log de Tráfego de Rede (IP: {MEU_IP}, Porta: {PORTA_ALVO}) ---\n")
        log_file.write(f"Início da Captura: {datetime.datetime.now()}\n\n")
        
        # Define uma função de callback para processar cada pacote
        # Isso é útil para processar pacotes um a um sem armazenar tudo na memória
        def process_packet(packet):
            log_entry = ""
            try:
                timestamp = packet.sniff_time.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] # Formata a hora
                
                # Tenta extrair informações comuns
                ip_src = packet.ip.src if 'IP' in packet else 'N/A'
                ip_dst = packet.ip.dst if 'IP' in packet else 'N/A'
                
                protocol = packet.highest_layer
                
                src_port = 'N/A'
                dst_port = 'N/A'
                if 'TCP' in packet:
                    src_port = packet.tcp.srcport
                    dst_port = packet.tcp.dstport
                    protocol = "TCP"
                elif 'UDP' in packet:
                    src_port = packet.udp.srcport
                    dst_port = packet.udp.dstport
                    protocol = "UDP"
                elif 'ICMP' in packet:
                    protocol = "ICMP"
                # Adicione mais protocolos conforme necessário

                length = packet.length if hasattr(packet, 'length') else 'N/A' # Comprimento do pacote
                info = packet.info if hasattr(packet, 'info') else 'N/A' # Informações resumidas do protocolo

                log_entry = (
                    f"[{timestamp}] "
                    f"Proto: {protocol}, Len: {length}, "
                    f"Src: {ip_src}:{src_port} -> Dst: {ip_dst}:{dst_port}, "
                    f"Info: {info}\n"
                )
            except AttributeError:
                # Alguns pacotes podem não ter todos os atributos esperados
                log_entry = f"[{timestamp}] Malformed/Unexpected Packet - Full Packet: {packet}\n"
            except Exception as e:
                log_entry = f"[{timestamp}] Error processing packet: {e} - Raw: {packet}\n"
            
            log_file.write(log_entry)
            print(f"Logado: {log_entry.strip()}") 


        capture.apply_on_packets(process_packet, packet_count=NUM_PACOTES)

        log_file.write(f"\nFim da Captura: {datetime.datetime.now()}\n")
    
    print(f"\n--- Captura Concluída ---")
    print(f"Tráfego salvo em formato de log textual em: {NOME_ARQUIVO_LOG}")

except pyshark.tshark.tshark.TSharkNotFoundException:
    print("\nERRO: TShark não foi encontrado. Certifique-se de que o Wireshark (com TShark) está instalado e no seu PATH.")
except Exception as e:
    print(f"\nOcorreu um erro durante a captura ou escrita do log: {e}")
    print("Verifique permissões do arquivo, nome da interface, ou tráfego de rede.")
finally:
    if 'capture' in locals() and capture:
        capture.close()
        print("\nCaptura finalizada e recursos liberados.")