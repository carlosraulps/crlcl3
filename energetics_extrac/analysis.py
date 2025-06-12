
#!/usr/bin/env python3
"""
Traverse all subdirectories under the current directory, parse each OUTCAR for
SCF iterations (TOTEN energies and rms values), and generate two CSVs:
  - convergence_iters_encut.csv  (tests whose directory names end in a number)
  - convergence_iters_other.csv  (all other tests)
"""

import os
import re
import pandas as pd
from pathlib import Path

# -----------------------------------------------------------------------------
# Regex patterns (case‐insensitive)
# -----------------------------------------------------------------------------
_re_energy   = re.compile(r"\bTOTEN\s*=\s*([+\-]?[0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)
_re_rms_tot  = re.compile(r"rms\s*\(\s*total\s*\)\s*=\s*([0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)
_re_rms_bro  = re.compile(r"rms\s*\(\s*broyden\s*\)\s*=\s*([0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)
_re_rms_prec = re.compile(r"rms\s*\(\s*prec\s*\)\s*=\s*([0-9]*\.?[0-9]+(?:[Ee][+\-]?\d+)?)", re.IGNORECASE)

def parse_outcar_iterations(path):
    """
    Reads an OUTCAR and returns four parallel lists:
      energies, rms_total, rms_broyden, rms_prec
    corresponding to each SCF iteration where all four values appear.
    """
    E, rt, rb, rp = [], [], [], []
    with open(path, 'r', errors='ignore') as f:
        for line in f:
            m = _re_energy.search(line)
            if m:
                E.append(float(m.group(1)))
            m = _re_rms_tot.search(line)
            if m:
                rt.append(float(m.group(1)))
            m = _re_rms_bro.search(line)
            if m:
                rb.append(float(m.group(1)))
            m = _re_rms_prec.search(line)
            if m:
                rp.append(float(m.group(1)))
    n = min(len(E), len(rt), len(rb), len(rp))
    return E[:n], rt[:n], rb[:n], rp[:n]

def collect_all_iterations(base_dir=".", other_label="other"):
    """
    Walks all subdirectories under `base_dir`, collects SCF iterations
    from each OUTCAR, and returns two DataFrames:
      - df_encut: tests whose dir name ends in a number
      - df_other: all other tests
    """
    rows_encut = []
    rows_other = []
    for outcar in Path(base_dir).rglob("*/OUTCAR"):
        test_name = outcar.parent.name
        is_encut = test_name.rstrip("/").split("_")[-1].isdigit()
        E, rt, rb, rp = parse_outcar_iterations(outcar)
        if not E:
            continue
        for i, (e, t, b, p) in enumerate(zip(E, rt, rb, rp), start=1):
            row = {
                "test": test_name,
                "iteration": i,
                "energy_eV": e,
                "rms_total": t,
                "rms_broyden": b,
                "rms_prec": p
            }
            (rows_encut if is_encut else rows_other).append(row)
    df_e = pd.DataFrame(rows_encut)
    df_o = pd.DataFrame(rows_other)
    return df_e, df_o

def main():
    df_encut, df_other = collect_all_iterations(".")
    if not df_encut.empty:
        df_encut.sort_values(["test","iteration"], inplace=True)
        df_encut.to_csv("convergence_iters_encut.csv", index=False)
        print("✅ convergence_iters_encut.csv generated.")
    else:
        print("❌ No 'encut'-style data found.")

    if not df_other.empty:
        df_other.sort_values(["test","iteration"], inplace=True)
        df_other.to_csv("convergence_iters_other.csv", index=False)
        print("✅ convergence_iters_other.csv generated.")
    else:
        print("❌ No 'other'-style data found.")

if __name__ == "__main__":
    main()

