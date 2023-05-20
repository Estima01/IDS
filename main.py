import subprocess
import json

# Define o nome do arquivo de captura
segunda = 'segunda.tcpdump'
terca = 'terça.tcpdump'
quarta = 'quarta.tcpdump'
quinta = 'quinta.tcpdump'
sexta = 'sexta.tcpdump'

filename = ''
# Define o intervalo de tempo em segundos
interval = 60

# Cria um dicionário vazio para armazenar os dados agrupados
data = {}

# Executa o comando Tshark e processa a saída
for i in range(0,5):
    if i == 0:
        filename = segunda
    elif i == 1:
        filename = terca
    elif i == 2:
        filename = quarta
    elif i == 3: 
        filename = quinta
    elif i == 4:
        filename = sexta

    p = subprocess.Popen(['tshark', '-r', filename, '-T', 'fields', '-e',
       'frame.time_epoch', '-e', 'frame.cap'], stdout=subprocess.PIPE)

        # Analisa a saída do comando Tshark
    for line in iter(p.stdout.readline, b''):
        # Divide a linha em campos
            fields = line.decode().strip().split('\t')

        # Obtém o tempo da captura e arredonda para o intervalo de tempo definido
            timestamp = float(fields[0])
            interval_start = int(timestamp // interval * interval)

        # Obtém o comprimento do pacote
            packet_len = int(fields[1])

        # Adiciona os dados ao dicionário
            if interval_start not in data:
                data[interval_start] = {
                    'count': 0,
                    'total_len': 0
                                        }
            data[interval_start]['count'] += 1
            data[interval_start]['total_len'] += packet_len

        # Calcula a média do comprimento dos pacotes em cada intervalo
    for interval_start in data:
            count = data[interval_start]['count']
            total_len = data[interval_start]['total_len']
            if count > 0:
                data[interval_start]['avg_len'] = total_len / count

        # Converte o dicionário em JSON
    
json_data = json.dumps(data)

        # # Imprime o JSON resultante
        # print(json_data)

with open('semana.json', 'w') as f:
    f.write(json_data)