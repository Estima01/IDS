import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import json
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Read data from json file
with open('semana.json') as f:
    data = json.load(f)

# Convert data to pandas DataFrame
df = pd.DataFrame.from_dict(data, orient='index')
df = df.sort_index()
df = df.reset_index()
df.columns = ['time', 'count', 'total_len', 'avg_len']

# Convert timestamp to Brazilian date format
df['time'] = pd.to_datetime(df['time'], unit='s')

# Calculate EMA with a window of 10 minutes
df['EMA'] = df['total_len'].ewm(span=10, adjust=False).mean()

# Mark points as anomalies if their size is greater than 2 * EMA
df['anomaly'] = df['total_len'] > 2 * df['EMA']

# Calculate the deviation from the EMA
df['deviation'] = df['total_len'] / df['EMA']

# Define fuzzy variables
deviation = ctrl.Antecedent(np.arange(0, 3, 0.1), 'deviation')
potential = ctrl.Consequent(np.arange(0, 1, 0.1), 'potential')

# Define fuzzy membership functions
deviation['low'] = fuzz.trimf(deviation.universe, [0, 0.5, 1])
deviation['medium'] = fuzz.trimf(deviation.universe, [0.5, 1, 1.5])
deviation['high'] = fuzz.trimf(deviation.universe, [1, 1.5, 2])
deviation['very_high'] = fuzz.trimf(deviation.universe, [1.5, 2, 3])

potential['low'] = fuzz.trimf(potential.universe, [0, 0.2, 0.4])
potential['medium'] = fuzz.trimf(potential.universe, [0.3, 0.5, 0.7])
potential['high'] = fuzz.trimf(potential.universe, [0.6, 0.8, 1])
potential['very_high'] = fuzz.trimf(potential.universe, [0.8, 1, 1])

# Define fuzzy rules
rule1 = ctrl.Rule(deviation['low'], potential['low'])
rule2 = ctrl.Rule(deviation['medium'], potential['medium'])
rule3 = ctrl.Rule(deviation['high'], potential['high'])
rule4 = ctrl.Rule(deviation['very_high'], potential['very_high'])

# Create control system
potential_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4])
potential_sim = ctrl.ControlSystemSimulation(potential_ctrl)

# Apply fuzzy logic to each point
potential_values = []
for dev in df['deviation']:
    potential_sim.input['deviation'] = dev
    potential_sim.compute()
    potential_values.append(potential_sim.output['potential'])

df['potential'] = potential_values

# Calculate NMSE error metric
erro_NMSE = df['avg_len'].values - df['total_len'].values 
erro_NMSE = np.square(erro_NMSE)
erro_NMSE = np.sum(erro_NMSE)
erro_NMSE = erro_NMSE / len(df['avg_len'].values)
erro_NMSE = np.sqrt(erro_NMSE)
erro_NMSE = erro_NMSE / np.mean(df['total_len'].values)
erro_NMSE = round(erro_NMSE, 2)

# Calculate MAPE error metric
erro_MAPE = df['avg_len'].values - df['total_len'].values
erro_MAPE = np.abs(erro_MAPE)
erro_MAPE = erro_MAPE / df['total_len'].values
erro_MAPE = np.sum(erro_MAPE)
erro_MAPE = erro_MAPE / len(df['avg_len'].values)
erro_MAPE = erro_MAPE * 100
erro_MAPE = round(erro_MAPE, 2)

# Plot data
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(df['time'], df['total_len'], label='Comprimento total')
ax.plot(df['time'], df['EMA'], label='EMA')

# Mark anomalies with red dots
ax.plot(df.loc[df['anomaly'], 'time'], df.loc[df['anomaly'], 'total_len'], 'ro', label='Anomalia')

# Plot potential of becoming an anomaly
sc = ax.scatter(df['time'], df['total_len'], c=df['potential'], cmap='viridis', label='Potencial de anomalia')
plt.colorbar(sc, label='Potencial de anomalia')

# Display number of anomalies and error metrics
ax.text(0.5, 0.85, 'Anomalias = ' + str(df['anomaly'].sum()), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)

# Display error metrics
ax.text(0.5, 0.95, 'NMSE = ' + str(erro_NMSE) + '\nMAPE = ' + str(erro_MAPE) + '%', horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
ax.legend()
plt.show()
