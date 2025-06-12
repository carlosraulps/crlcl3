
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
be_graph.py

Gera um gráfico profissional da estrutura de bandas a partir de
band_structure_data.csv, usando Matplotlib + LineCollection
e MathText interno (sem `usetex`) para evitar erros de LaTeX.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib as mpl

# 1) Estilo global (MathText interno)
# Fonte e estilo geral
mpl.rcParams['text.usetex']      = False
mpl.rcParams['mathtext.fontset'] = 'dejavuserif'
mpl.rcParams['font.family']      = 'serif'
mpl.rcParams['font.serif']       = ['Times New Roman','Georgia']

# ↓ Fontes menores para publicação
mpl.rcParams['axes.titlesize']   = 13   # título ↓
mpl.rcParams['axes.labelsize']   = 11   # rótulos ↓
mpl.rcParams['xtick.labelsize']  = 10   # ticks ↓
mpl.rcParams['ytick.labelsize']  = 10
mpl.rcParams['legend.fontsize']  = 10    # legenda ↓

def main():
    # 2) Carrega e prepara dados
    df = pd.read_csv("band_structure_data.csv")
    # Preenche NaN e converte para string para evitar AttributeError :contentReference[oaicite:4]{index=4}
    df['kpoint_label'] = df['kpoint_label'].fillna("").astype(str)  # :contentReference[oaicite:5]{index=5}

    # Extrai pontos de alta simetria
    kp = df[['kpoint_distance','kpoint_label']] \
         .drop_duplicates() \
         .reset_index(drop=True)
    symm = kp[kp['kpoint_label'] != ""] \
           .sort_values('kpoint_distance')

    # Função para LineCollection por spin
    def make_lc(subdf, color, style):
        segs = []
        for b in sorted(subdf['band_index'].unique()):
            tmp = subdf[subdf['band_index']==b]
            pts = np.column_stack((tmp['kpoint_distance'],
                                   tmp['energy_eV']))
            segs.append(pts)
        return LineCollection(segs, colors=color,
                              linestyles=style)

    lc_up   = make_lc(df[df['spin']==1],   'navy',   'solid')
    lc_down = make_lc(df[df['spin']==-1],  'crimson','dashed')

    # 3) Plot
    fig, ax = plt.subplots()
    ax.add_collection(lc_up)
    ax.add_collection(lc_down)
    ax.set_xlim(df['kpoint_distance'].min(),
                df['kpoint_distance'].max())
    ax.set_ylim(df['energy_eV'].min()-1,
                df['energy_eV'].max()+1)

    # Título e rótulos (MathText) :contentReference[oaicite:6]{index=6}
    ax.set_title(r"Estrutura de Bandas do CrCl$_3$", pad=8)
    ax.set_xlabel(r"Distância ao longo do k-path (Å$^{-1}$)")
    ax.set_ylabel(r"Energia (eV)")


    # 4) Eixo X com símbolos sem sobreposição :contentReference[oaicite:7]{index=7}
    ticks  = symm['kpoint_distance'].values
    labels = []
    for lbl in symm['kpoint_label']:
        up = lbl.upper()
        if up == "GAMMA":
            labels.append(r'$\Gamma$')
        else:
            labels.append(f'${up}$')
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)

    # Linhas verticais pontilhadas nos pontos :contentReference[oaicite:8]{index=8}
    for x in ticks:
        ax.axvline(x, color='gray',
                   linestyle=':', linewidth=0.8)

    # Legenda manual
    ax.plot([], [], color='navy',   lw=1.2, label='Spin up')
    ax.plot([], [], color='crimson',lw=1.2,
            ls='--', label='Spin down')
    ax.legend(loc='lower right', frameon=True)

    plt.tight_layout()
    fig.savefig("band_structure.pdf")
    plt.show()

if __name__ == "__main__":
    main()

