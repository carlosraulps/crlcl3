
#!/usr/bin/env python3
"""
Lê os CSVs de convergência e exporta figuras em TikZ/PGFPlots usando 'coordinates',
com:
  - legend columns=2
  - label style=\small
  - tick label style=\scriptsize
  - title style=\small\bfseries
  - linha de convergência no valor final mínimo
"""
import os
import pandas as pd
import re

# Ajuste conforme necessário
BASEDIR = "."
os.chdir(BASEDIR)

# Regex para capturar energia TOTEN
_re_energy = re.compile(r"\bTOTEN\s*=\s*([+\-]?[0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)

def parse_outcar_energies(outcar_path):
    """Retorna lista de energias TOTEN em ordem de iteração SCF."""
    energies = []
    with open(outcar_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            m = _re_energy.search(line)
            if m:
                energies.append(float(m.group(1)))
    return energies

def generate_tikz(df, scan_label, csv_file):
    # calcula referência de convergência: mínimo do último ponto de cada teste
    last = df.groupby('teste')['energia_eV'].last()
    conv_ref = last.min()
    # encontra primeiro e último índice de iteração
    first_it = int(df['iteracao'].min())
    last_it  = int(df['iteracao'].max())

    out = []
    out.append(r"\begin{figure}[htbp]")
    out.append(r"  \centering")
    out.append(r"  \begin{tikzpicture}")
    out.append(r"    \begin{axis}[")
    out.append(r"      width=0.8\textwidth,")
    out.append(r"      height=0.5\textwidth,")
    out.append(r"      xlabel={Iteração SCF},")
    out.append(r"      ylabel={Energia total (eV)},")
    out.append(r"      legend style={")
    out.append(r"        at={(0.5,-0.15)},")
    out.append(r"        anchor=north,")
    out.append(r"        legend columns=2")
    out.append(r"      },")
    out.append(r"      label style={font=\small},")
    out.append(r"      tick label style={font=\scriptsize},")
    out.append(r"      title={" + f"Convergência de Energia vs. Iteração ({scan_label})" + r"},")
    out.append(r"      title style={font=\small\bfseries},")
    out.append(r"      grid=major")
    out.append(r"    ]")

    # uma curva por teste
    for teste, group in df.groupby('teste'):
        out.append(r"      \addplot+[mark=o] coordinates {")
        for _, row in group.iterrows():
            out.append(f"        ({int(row['iteracao'])}, {row['energia_eV']:.6f})")
        out.append(r"      };")
        out.append(r"      \addlegendentry{" + f"{scan_label} {teste}" + r"}")

    # linha de convergência
    out.append(r"      \addplot[dashed, thick, red] coordinates {")
    out.append(f"        ({first_it}, {conv_ref:.6f}) ({last_it}, {conv_ref:.6f})")
    out.append(r"      };")
    out.append(r"      \addlegendentry{Convergência (E$_\mathrm{final}$)}")

    out.append(r"    \end{axis}")
    out.append(r"  \end{tikzpicture}")
    out.append(r"  \caption[Convergência de Energia (" + scan_label +
               r"); ref.: " + f"{conv_ref:.6f} eV" + r"]" )
    out.append(r"    {Curva de convergência da energia total em cada iteração do SCF para varredura de " +
               scan_label +
               r". A linha tracejada vermelha indica o valor de energia final convergido (mínimo).}")
    out.append(r"  \label{fig:conv_" + scan_label.lower().replace('×','x') + r"}")
    out.append(r"\end{figure}")
    return "\n".join(out)

def main():
    # Carrega CSVs
    df_encut = pd.read_csv("convergencia_iters_encut.csv")
    df_kpts  = pd.read_csv("convergencia_iters_kpoints.csv")

    # Gera e imprime TikZ para ENCUT
    print("% --- Figura ENCUT ---")
    print(generate_tikz(df_encut, "ENCUT", "convergencia_iters_encut.csv"))
    print("\n% --- Figura k-points ---")
    print(generate_tikz(df_kpts, "k-points", "convergencia_iters_kpoints.csv"))

if __name__ == "__main__":
    main()

