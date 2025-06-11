
#!/usr/bin/env python3
"""
Extrai iterações SCF de OUTCAR (todas as energias TOTEN e rms) e gera:
  - convergencia_iters_encut.csv
  - convergencia_iters_kpoints.csv
"""

import os
import glob
import re
import pandas as pd

# 1) Ajuste a base para onde estão os diretórios
BASEDIR = os.path.expanduser(".")
os.chdir(BASEDIR)

# 2) Compilação de padrões mais tolerantes (re.IGNORECASE)
_re_energy   = re.compile(r"\bTOTEN\s*=\s*([+\-]?[0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)  # :contentReference[oaicite:0]{index=0}
_re_rms_tot  = re.compile(r"rms\s*\(\s*total\s*\)\s*=\s*([0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)
_re_rms_bro  = re.compile(r"rms\s*\(\s*broyden\s*\)\s*=\s*([0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)
_re_rms_prec = re.compile(r"rms\s*\(\s*prec\s*\)\s*=\s*([0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)

def parse_outcar_iterations(outcar_path):
    """
    Lê o OUTCAR e devolve quatro listas paralelas:
    - energias TOTEN (float)
    - rms_total, rms_broyden, rms_prec (floats)
    Cada i-ésimo elemento corresponde à i-ésima iteração SCF.
    """
    energies, rt_list, rb_list, rp_list = [], [], [], []
    with open(outcar_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # free energy TOTEN
            m = _re_energy.search(line)
            if m:
                energies.append(float(m.group(1)))
            # rms(total)
            m = _re_rms_tot.search(line)
            if m:
                rt_list.append(float(m.group(1)))
            # rms(broyden)
            m = _re_rms_bro.search(line)
            if m:
                rb_list.append(float(m.group(1)))
            # rms(prec)
            m = _re_rms_prec.search(line)
            if m:
                rp_list.append(float(m.group(1)))
    # Garante mesmo número de pontos
    n = min(len(energies), len(rt_list), len(rb_list), len(rp_list))
    return energies[:n], rt_list[:n], rb_list[:n], rp_list[:n]

def collect_iterations(pattern, is_encut):
    """
    Para cada diretório casando com `pattern`, lê o OUTCAR e monta
    um DataFrame long com:
      teste, iteracao, energia_eV, rms_total, rms_broyden, rms_prec
    """
    rows = []
    dirs = sorted(glob.glob(pattern))
    for d in dirs:
        outcar = os.path.join(d, "OUTCAR")
        if not os.path.isfile(outcar):
            continue
        # rótulo: número para encut, string para kpoints
        label = d.split('_')[-1]
        teste = int(label) if is_encut else label

        # extrai listas
        E_list, rt, rb, rp = parse_outcar_iterations(outcar)
        if not E_list:
            continue

        # monta linhas
        for i, (E, t, b, p) in enumerate(zip(E_list, rt, rb, rp), start=1):
            rows.append({
                "teste": teste,
                "iteracao": i,
                "energia_eV": E,
                "rms_total": t,
                "rms_broyden": b,
                "rms_prec": p
            })

    return pd.DataFrame(rows)

def main():
    # 1) ENCUT
    df_e = collect_iterations("encut_*", True)
    if not df_e.empty:
        df_e.sort_values(["teste","iteracao"], inplace=True)
        df_e.to_csv("convergencia_iters_encut.csv", index=False)
        print("✅ convergencia_iters_encut.csv gerado.")
    else:
        print("❌ Nenhum dado de ENCUT coletado.")

    # 2) k-points
    df_k = collect_iterations("kpoints_*", False)
    if not df_k.empty:
        df_k.sort_values(["teste","iteracao"], inplace=True)
        df_k.to_csv("convergencia_iters_kpoints.csv", index=False)
        print("✅ convergencia_iters_kpoints.csv gerado.")
    else:
        print("❌ Nenhum dado de k-points coletado.")

if __name__ == "__main__":
    main()

