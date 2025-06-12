
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib as mpl

# 1) Estilo geral
mpl.rcParams.update({
    'text.usetex': False,
    'mathtext.fontset': 'dejavuserif',
    'font.family': 'serif',
    'font.serif': ['Times New Roman','Georgia'],
    'figure.dpi': 300,
    'figure.figsize': (10, 4),    # largura maior para duas colunas
    'lines.linewidth': 1.5,
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.alpha': 0.3,
})

# 2) Carrega dados e prepara labels
df = pd.read_csv("band_structure_data.csv")
df['kpoint_label'] = df['kpoint_label'].fillna("").astype(str)

# Extraímos distâncias e labels de alta simetria
kp = df[['kpoint_distance','kpoint_label']].drop_duplicates()
symm = kp[kp['kpoint_label']!=""].sort_values('kpoint_distance')
xt = symm['kpoint_distance'].values
xl = [r'$\Gamma$' if lbl.upper()=="GAMMA" else f'${lbl.upper()}$'
      for lbl in symm['kpoint_label']]

# Função que retorna um LineCollection para um spin
def make_lc(spin, color, style):
    sub = df[df['spin']==spin]
    segs = []
    for b in sorted(sub['band_index'].unique()):
        tmp = sub[sub['band_index']==b]
        pts = np.column_stack((tmp['kpoint_distance'], tmp['energy_eV']))
        segs.append(pts)
    return LineCollection(segs, colors=color, linestyles=style)

# 3) Cria subplots
fig, (ax_up, ax_dn) = plt.subplots(ncols=2, sharey=True)

# 4) Adiciona as coleções
ax_up.add_collection(make_lc(1, 'navy',   'solid'))
ax_dn.add_collection(make_lc(-1,'firebrick','solid'))

# 5) Ajusta limites
ymin, ymax = df['energy_eV'].min()-1, df['energy_eV'].max()+1
ax_up.set_ylim(ymin, ymax)
ax_dn.set_ylim(ymin, ymax)
xmin, xmax = df['kpoint_distance'].min(), df['kpoint_distance'].max()
for ax in (ax_up, ax_dn):
    ax.set_xlim(xmin, xmax)
    ax.set_xticks(xt)
    ax.set_xticklabels(xl, fontsize=9)
    for x in xt:
        ax.axvline(x, color='gray', linestyle=':', linewidth=0.8)

# 6) Rótulos e títulos
ax_up.set_title("Spin up",   fontsize=11)
ax_dn.set_title("Spin down", fontsize=11)
ax_up.set_ylabel("Energia (eV)", fontsize=9)
ax_up.set_xlabel("k-path (Å$^{-1}$)", fontsize=9)
ax_dn.set_xlabel("k-path (Å$^{-1}$)", fontsize=9)

# 7) Melhor layout e salvamento
fig.tight_layout()
fig.savefig("band_spin_comparison.pdf")
plt.show()

