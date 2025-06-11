"""
Extrai dados de convergência de ENCUT e k-points para o relatório.
Produz dois CSVs: convergencia_encut.csv e convergencia_kpoints.csv.
"""

import os
import glob
import pandas as pd
from pymatgen.io.vasp import Vasprun, Outcar

# Define onde estão os seus diretórios
BASEDIR = os.path.expanduser("./essenciais")
os.chdir(BASEDIR)

def parse_outcar_cpu_time(outcar_path):
    """Extrai o tempo de CPU reportado em OUTCAR."""
    cpu_time = None
    with open(outcar_path, 'r') as f:
        for line in f:
            if "Total CPU time used" in line:
                # Exemplo: "Total CPU time used (sec):  1843.977"
                cpu_time = float(line.split(':')[-1].strip().split()[0])
                break
    return cpu_time

def collect_data(pattern, is_encut=True):
    """
    Coleta dados de cada diretório que casa com `pattern`.
    is_encut: True para encut_*, False para kpoints_*.
    """
    rows = []
    for d in sorted(glob.glob(pattern)):
        xml = os.path.join(d, "vasprun.xml")
        outcar = os.path.join(d, "OUTCAR")
        if not os.path.exists(xml) or not os.path.exists(outcar):
            continue

        # Parse vasprun.xml
        vr = Vasprun(xml, parse_dos=False)
        E = vr.final_energy                      # energia SCF final :contentReference[oaicite:5]{index=5}
        a, b, c = vr.final_structure.lattice.abc  # parâmetros de rede :contentReference[oaicite:6]{index=6}

        # Parse OUTCAR
        oc = Outcar(outcar)
        M = oc.magnetization                      # magnetização total :contentReference[oaicite:7]{index=7}
        CPU = parse_outcar_cpu_time(outcar)       # tempo de CPU :contentReference[oaicite:8]{index=8}:contentReference[oaicite:9]{index=9}

        # Tipo de teste
        if is_encut:
            test = int(d.split('_')[-1])
        else:
            # kpoints_6x6x4 → "6x6x4"
            mesh = d.split('_')[-1]
            test = mesh

        rows.append({
            "teste": test,
            "energia_eV": E,
            "a_ang": a,
            "b_ang": b,
            "c_ang": c,
            "magnetizacao": M,
            "cpu_time_s": CPU
        })

    return pd.DataFrame(rows)

def main():
    # ENCUT scan
    df_encut = collect_data("encut_*", is_encut=True)
    df_encut.sort_values("teste", inplace=True)
    df_encut.to_csv("convergencia_encut.csv", index=False)

    # k-points scan
    df_kpts = collect_data("kpoints_*", is_encut=False)
    # opcional: manter a ordem lógica de meshes
    df_kpts.to_csv("convergencia_kpoints.csv", index=False)

    print("✅ CSVs gerados: convergencia_encut.csv e convergencia_kpoints.csv")

if __name__ == "__main__":
    main()
