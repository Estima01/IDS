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

# Plot data

fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df['time'], df['total_len'], label='Comprimento total')
ax.plot(df['time'], df['EMA'], label='EMA')

#descrição do erro no cantor superior direito
ax.text(0.5, 0.95, 'NMSE = ' + str(erro_NMSE) + '\nMAPE = ' + str(erro_MAPE) + '%', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
ax.legend()
plt.show()
