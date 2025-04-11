import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("Data/03-4_Minerals-Categorization_Cleaned-dataset.csv")

# Rock-forming mineral groups + gemstones
rock_forming_and_gems = [
    'QUARTZ', 'FELDSPAT', 'GLIMMER', 'AMPHIBOLE', 'PYROXENE',
    'CALCIT', 'GRANAT', 'CHLORIT', 'SERPENTIN', 'TITANIT',
    'RUTIL', 'DOLOMIT', 'EDELSTEINE'
]

# Zähle Häufigkeiten
category_counts = df['Category'].value_counts()

# Split in zwei Gruppen
rock_group_counts = category_counts[category_counts.index.isin(rock_forming_and_gems)].sort_values()
chem_group_counts = category_counts[~category_counts.index.isin(rock_forming_and_gems)].sort_values()

# Gemeinsames x-Limit definieren (max Wert von beiden Gruppen, leicht aufgerundet)
common_max = int(np.ceil(max(rock_group_counts.max(), chem_group_counts.max()) / 100.0)) * 100

# Farben
colors = plt.cm.tab20.colors

# Vertikale Balkendiagramme nebeneinander
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Vertikales Balkendiagramm 1: Rock-forming + Gems
axes[0].bar(rock_group_counts.index, rock_group_counts.values, color=colors[:len(rock_group_counts)])
for i, value in enumerate(rock_group_counts.values):
    axes[0].text(i, value + 10, str(int(value)), ha='center', fontsize=9, color='black')

axes[0].set_ylim(0, common_max)
axes[0].set_title('Rock-forming Mineral Groups and Gemstones')
axes[0].set_xlabel('Category')
axes[0].set_ylabel('Count')

# Vertikales Balkendiagramm 2: Chemical Categories
axes[1].bar(chem_group_counts.index, chem_group_counts.values, color=colors[len(rock_group_counts):len(rock_group_counts)+len(chem_group_counts)])
for i, value in enumerate(chem_group_counts.values):
    axes[1].text(i, value + 10, str(int(value)), ha='center', fontsize=9, color='black')

axes[1].set_ylim(0, common_max)
axes[1].set_title('Chemical–Crystallographic Categories')
axes[1].set_xlabel('Category')
axes[1].set_ylabel('Count')

# Drehung der x-Achsen-Ticks und manuelle Positionierung
for ax in axes:
    ax.tick_params(axis='x', rotation=45)  # Drehung der Labels
    ax.set_xticks(range(len(ax.get_xticklabels())))  # Manuelles Setzen der Ticks an die richtige Position
    ax.set_xticklabels(ax.get_xticklabels(), ha='right')  # Textausrichtung ändern, um Überlappung zu vermeiden

# Platz für die Ticks schaffen, falls nötig
plt.subplots_adjust(bottom=0.2)

plt.tight_layout()
plt.show()
