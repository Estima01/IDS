import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json



# Read data from json file
with open('semana.json') as f:
    data = json.load(f)

# Convert data to pandas DataFrame
df = pd.DataFrame.from_dict(data, orient='index')
df = df.sort_index()
df = df.reset_index()
df.columns = ['time', 'count', 'total_len', 'avg_len']

#timestamp para data brasileira
df['time'] = pd.to_datetime(df['time'], unit='s')

#metricas de avaliação de erro com NMSE
erro_NMSE = df['avg_len'].values - df['total_len'].values 
erro_NMSE = np.square(erro_NMSE)
erro_NMSE = np.sum(erro_NMSE)
erro_NMSE = erro_NMSE/len(df['avg_len'].values)
erro_NMSE = np.sqrt(erro_NMSE)
erro_NMSE = erro_NMSE/np.mean(df['total_len'].values)
#casas decimais
erro_NMSE = round(erro_NMSE, 2)

#metricas de avaliação de erro com MAPE
erro_MAPE = df['avg_len'].values - df['total_len'].values
erro_MAPE = np.abs(erro_MAPE)
erro_MAPE = erro_MAPE/df['total_len'].values
erro_MAPE = np.sum(erro_MAPE)
erro_MAPE = erro_MAPE/len(df['avg_len'].values)
erro_MAPE = erro_MAPE*100
#casas decimais
erro_MAPE = round(erro_MAPE, 2)

# calcular EMA numa janela de 10 minutos
df['EMA'] = df['total_len'].ewm(span=10, adjust=False).mean()

#arredondar para inteiro
df['EMA'] = df['EMA'].round().astype(int)

# calcula a diferença entre o real e o estimado
df['diferença'] = df['total_len'] - df['EMA']
df['%'] = round((abs(df['total_len'] - df['EMA']) * 100) / df['total_len']).astype(int)

#marcar com um ponto vermelho pacotes com tamanho maior que 2 * EMA (anomalia)
df['anomaly-up'] = df['total_len'] > 2 * df['EMA'] 


# Plot data
fig, ax = plt.subplots(figsize=(12, 6))

#todos os dados de uma vez
def plot(view_tolerance=True):
    ax.clear()  # Limpar o gráfico antes de cada iteração
    ax.plot(df['time'], df['total_len'], label='Comprimento total')
    ax.plot(df['time'], df['EMA'], label='EMA')

    #marcar com um ponto vermelho pacotes com tamanho maior que 2 * EMA (anomalia)
    ax.plot(df.loc[df['anomaly'], 'time'], df.loc[df['anomaly'], 'total_len'], 'ro', label='Anomalia')

    #numero de anomalias
    ax.text(0.5, 0.85, 'Anomalias = ' + str(df['anomaly'].sum()), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    # Plotar a Tolerancia
    if view_tolerance:
        # Calcular teto e piso da Tolerancia para a janela atual
        teto = df['total_len'] * (1 + margem)
        piso = df['total_len'] * (1- margem)
        ax.fill_between(df['time'], teto, piso, alpha=0.5, color='lightgreen', label='Tolerancia')

    #descrição do erro no cantor superior direito
    ax.text(0.5, 0.95, 'NMSE = ' + str(erro_NMSE) + '\nMAPE = ' + str(erro_MAPE) + '%', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.legend()
    plt.show()  


#todos os dados de uma vez
def plot_up():
    ax.clear()  # Limpar o gráfico antes de cada iteração
    ax.plot(df['time'], df['total_len'], label='Comprimento total')
    ax.plot(df['time'], df['EMA'], label='EMA')

    #marcar com um ponto vermelho pacotes com tamanho maior que 2 * EMA (anomalia)
    ax.plot(df.loc[df['anomaly-up'], 'time'], df.loc[df['anomaly-up'], 'total_len'], 'ro', label='Anomalia')

    #numero de anomalias
    ax.text(0.5, 0.85, 'Anomalias = ' + str(df['anomaly-up'].sum()), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    #descrição do erro no cantor superior direito
    ax.text(0.5, 0.95, 'NMSE = ' + str(erro_NMSE) + '\nMAPE = ' + str(erro_MAPE) + '%', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.legend()
    plt.show()  

# plota controlando limite inferior e superior
def plot_limites(margem,view_tolerance=True):
    ax.clear()  # Limpar o gráfico antes de cada iteração
    ax.plot(df['time'], df['total_len'], label='Comprimento total')
    ax.plot(df['time'], df['EMA'], label='EMA')

    #marcar com um ponto vermelho pacotes
    ax.plot(df.loc[df['anomaly'], 'time'], df.loc[df['anomaly'], 'total_len'], 'ro', label='Anomalia')

    #numero de anomalias
    ax.text(0.5, 0.85, 'Anomalias = ' + str(df['anomaly'].sum()), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

    # Plotar a Tolerancia
    if view_tolerance:
        # Calcular teto e piso da Tolerancia para a janela atual
        teto =  df['total_len'] + (df['total_len'] * margem['superior'])
        piso = df['total_len'] - (df['total_len'] * margem['inferior'])
        ax.fill_between(df['time'], teto, piso, alpha=0.5, color='lightgreen', label='Tolerancia')

    #descrição do erro no cantor superior direito
    ax.text(0.5, 0.95, 'NMSE = ' + str(erro_NMSE) + '\nMAPE = ' + str(erro_MAPE) + '%', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
    ax.legend()
    plt.show()  


# do inicio ao fim dos dados
def plot_all(time=0.5,margem=0.5,view_tolerance=True):
    if time==0:
        plot(view_tolerance)
    else:
        
        for index in range(0, len(df)):

            window_df = df.iloc[0:index]  # DataFrame da janela atual

            ax.clear()  # Limpar o gráfico antes de cada iteração

            # Plotar os dados da janela atual
            ax.plot(window_df['time'], window_df['total_len'], label='Comprimento total')
            ax.plot(window_df['time'], window_df['EMA'], label='EMA')

            #marcar com um ponto
            ax.plot(window_df.loc[window_df['anomaly'], 'time'], window_df.loc[window_df['anomaly'], 'total_len'], 'ro', label='Anomalia')

            # número de anomalias na janela atual
            num_anomalies = window_df['anomaly'].sum()
            ax.text(0.5, 0.85, 'Anomalias = ' + str(num_anomalies), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

            # Calcular teto e piso da Tolerancia para a janela atual
            teto = window_df['total_len'] * (1 + margem)
            piso = window_df['total_len'] * (1- margem)

            # Plotar a Tolerancia
            if view_tolerance:
                ax.fill_between(window_df['time'], teto, piso, alpha=0.5, color='lightgreen', label='Tolerancia')

            # Descrição do erro no canto superior direito
            ax.text(0.5, 0.95, 'NMSE = ' + str(erro_NMSE) + '\nMAPE = ' + str(erro_MAPE) + '%', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

            ax.legend()

            plt.pause(time)
        
# vai mostrando baseado numa janela  
def plot_window(time=1,margem=0.5,zoom=100,view_tolerance=True):
    end_window = 1
    anomalias_atual = 0
    for start_index in range(0, len(df), zoom):
        end_window =  start_index 
        end_index = start_index + zoom  # Índice final da janela
        while end_window < end_index:
            window_df = df.iloc[start_index:end_window]  # DataFrame da janela atual

            ax.clear()  # Limpar o gráfico antes de cada iteração

            # Plotar os dados da janela atual
            ax.plot(window_df['time'], window_df['total_len'], label='Comprimento total')
            ax.plot(window_df['time'], window_df['EMA'], label='EMA')

            #marcar com um ponto
            ax.plot(window_df.loc[window_df['anomaly'], 'time'], window_df.loc[window_df['anomaly'], 'total_len'], 'ro', label='Anomalia')

            # número de anomalias na janela atual
            num_anomalies = window_df['anomaly'].sum()

            
            ax.text(0.5, 0.85, 'Anomalias = ' + str(anomalias_atual + num_anomalies), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
           

            # Calcular teto e piso da Tolerancia para a janela atual
            teto = window_df['total_len'] * (1 + margem)
            piso = window_df['total_len'] * (1- margem)

            if view_tolerance:
                # Plotar a Tolerancia
                ax.fill_between(window_df['time'], teto, piso, alpha=0.5, color='lightgreen', label='Tolerancia')

            # Descrição do erro no canto superior direito
            ax.text(0.5, 0.95, 'NMSE = ' + str(erro_NMSE) + '\nMAPE = ' + str(erro_MAPE) + '%', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

            ax.legend()
            plt.pause(time) 
            end_window = end_window + 1
        anomalias_atual += num_anomalies

    # printa o grafico completo
    plot(view_tolerance)
        
def start_window(time,margem,zoom,view_tolerance=True):
    #Classifica se é anomalia ou não baseado na Tolerancia
    df['anomaly'] = df['%'] > (margem*100)
    plot_window(time,margem,zoom,view_tolerance)

def start_all(time,margem,view_tolerance=True):
    #Classifica se é anomalia ou não baseado na Tolerancia
    df['anomaly'] = df['%'] > (margem*100)
    plot_all(time,margem,view_tolerance)


def start_limites(margem,view_tolerance=True):

    print(margem)

    teto =  df['total_len'] + (df['total_len'] * margem['superior'])
    piso = df['total_len'] - (df['total_len'] * margem['inferior'])

    df['limite-superior'] = teto
    df['limite-inferior'] = piso

    #Classifica se é anomalia ou não baseado na Tolerancia
    df['outside-superior'] = df['EMA'] >  teto
    df['outside-inferior'] = df['EMA'] <  piso
    df['anomaly'] = df['outside-superior'] | df['outside-inferior'] 

    print(df)

    plot_limites(margem,view_tolerance)


op = input('1 - Mostrar todos os dados\n2 - Mostrar por janela\n3- Mostrar dados somente maiores que o esperado.\n4- Mostrar dados controlando limites superiores e inferiores\n')
if op == '1':
    time = float(input('Taxa de atualização: '))
    margem = float(input('Tolerancia: ')) / 100
    view_tolerance = input('Mostrar Tolerancia? (S/N): ')
    view_tolerance = view_tolerance.lower()
    view_tolerance = True if view_tolerance == 's' else False


    start_all(time,margem,view_tolerance)
elif op == '2':
    time = float(input('Taxa de atualização: '))
    margem = float(input('Tolerancia: ')) / 100

    view_tolerance = input('Mostrar Tolerancia? (S/N): ')
    view_tolerance = view_tolerance.lower()
    view_tolerance = True if view_tolerance == 's' else False

    zoom = int(input('Tamanho da janela (Zoom): '))
    start_window(time,margem,zoom,view_tolerance)
elif op == '3':
    plot_up()
elif op == '4':
    limite_superior = float(input('Limite superior: ')) / 100
    limite_inferior = float(input('Limite inferior: ')) / 100
    
    view_tolerance = input('Mostrar Tolerancia? (S/N): ')
    view_tolerance = view_tolerance.lower()
    view_tolerance = True if view_tolerance == 's' else False

    margem = {'superior': limite_superior, 'inferior': limite_inferior}
    start_limites(margem,view_tolerance)