
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D   # <<< importe aqui
import matplotlib as mpl

# Estilo geral
mpl.rcParams.update({
    'text.usetex': False,
    'mathtext.fontset': 'dejavuserif',
    'font.family': 'serif',
    'font.serif': ['Times New Roman','Georgia'],
    'figure.dpi': 200,
    'lines.linewidth': 1.2,
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.alpha': 0.3,
})

# Carrega dados
df = pd.read_csv("band_structure_data.csv")
df['kpoint_label'] = df['kpoint_label'].fillna("").astype(str)

# Janelas de energia
windows = [(5,0),(0,-5),(-5,-10),(-10,-15),(-15,-20)]
n = len(windows)

# 1) Cria o grid de subplots ANTES de usar legend()
fig, axes = plt.subplots(nrows=n, ncols=2, sharex=True,
                         figsize=(6, 2.5*n))

# 2) Define handles e labels para a legenda
handles = [
    Line2D([], [], color='navy',      linestyle='-', linewidth=1.2),
    Line2D([], [], color='firebrick', linestyle='--', linewidth=1.2)
]
labels = ['Spin up', 'Spin down']

# 3) Loop de plotagem
for i, (top, bot) in enumerate(windows):
    for col, spin in enumerate([1, -1]):
        ax = axes[i, col]

        # Gera nova LineCollection para cada Axes
        segs = []
        sub = df[df['spin']==spin]
        for b in sorted(sub['band_index'].unique()):
            tmp = sub[sub['band_index']==b]
            pts = np.column_stack((tmp['kpoint_distance'],
                                   tmp['energy_eV']))
            segs.append(pts)
        lc = LineCollection(
            segs,
            colors='navy'    if spin==1 else 'firebrick',
            linestyles='solid' if spin==1 else 'dashed'
        )
        ax.add_collection(lc)

        # Eixos e limites
        ax.set_ylim(bot, top)
        ax.set_xlim(df['kpoint_distance'].min(),
                    df['kpoint_distance'].max())
        ax.set_ylabel(f"{top}→{bot} eV", fontsize=8)

        # Título na primeira linha
        if i==0:
            ax.set_title("Spin up" if spin==1 else "Spin down",
                         fontsize=9)

        # Marcações na última linha
        if i==n-1:
            kp = df[['kpoint_distance','kpoint_label']].drop_duplicates()
            symm = kp[kp['kpoint_label']!=""]
            xt = symm['kpoint_distance']
            xl = [r'$\Gamma$' if lbl.upper()=="GAMMA"
                  else f'${lbl.upper()}$'
                  for lbl in symm['kpoint_label']]
            ax.set_xticks(xt)
            ax.set_xticklabels(xl, fontsize=7)
            for x in xt:
                ax.axvline(x, color='gray',
                           linestyle=':', linewidth=0.8)

# 4) Legenda na posição desejada
axes[0,1].legend(handles=handles,
                 labels=labels,
                 loc='upper right',
                 fontsize=7)

# 5) Rótulos finais
axes[-1,0].set_xlabel("k-path (Å$^{-1}$)", fontsize=8)

fig.tight_layout(h_pad=1.0)
fig.savefig("band_slices.pdf")
plt.show()
