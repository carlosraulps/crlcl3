
import re
from pathlib import Path

# --------------------------------------------------------------------
# Patterns for “static” values
# --------------------------------------------------------------------
_re_incar = {
    'ENCUT': re.compile(r'^\s*ENCUT\s*=\s*([0-9]+(?:\.[0-9]*)?)', re.IGNORECASE),
    'ISMEAR': re.compile(r'^\s*ISMEAR\s*=\s*([0-9\-]+)', re.IGNORECASE),
    'SIGMA':  re.compile(r'^\s*SIGMA\s*=\s*([0-9]+(?:\.[0-9]*)?)', re.IGNORECASE),
    'EDIFF':  re.compile(r'^\s*EDIFF\s*=\s*([0-9Ee\-\+\.]+)', re.IGNORECASE),
    'ISPIN':  re.compile(r'^\s*ISPIN\s*=\s*([0-9]+)', re.IGNORECASE),
    'MAGMOM': re.compile(r'^\s*MAGMOM\s*=\s*(\S+)', re.IGNORECASE),
}

_re_final_energy = re.compile(r'FREE ENERGIE OF THE ION-ELECTRON SYSTEM.*?TOTEN\s*=\s*([+\-]?[0-9]*\.?[0-9]+)', re.IGNORECASE | re.DOTALL)
_re_cpu_time    = re.compile(r'Total CPU time used \(sec\):\s*([0-9]+(?:\.[0-9]*)?)')
_re_wall_time   = re.compile(r'Elapsed time \(sec\):\s*([0-9]+(?:\.[0-9]*)?)')

def parse_outcar_static(path):
    """
    Parse an OUTCAR for:
      - INCAR settings
      - final TOTEN
      - total CPU & elapsed times
    Returns a dict.
    """
    data = {k: None for k in ('ENCUT','ISMEAR','SIGMA','EDIFF','ISPIN','MAGMOM',
                               'TOTEN_eV','CPU_sec','Elapsed_sec')}
    text = path.read_text(errors='ignore')
    # 1) INCAR entries
    #    only scan from top down until we leave the INCAR block
    for line in text.splitlines():
        if line.strip().startswith('POTCAR'):
            break
        for key, patt in _re_incar.items():
            m = patt.match(line)
            if m:
                data[key] = m.group(1)
    # 2) final free energy (first match in the FREE ENERGIE block)
    m = _re_final_energy.search(text)
    if m:
        data['TOTEN_eV'] = m.group(1)
    # 3) timings (take last occurrences)
    for patt, fld in ((_re_cpu_time,'CPU_sec'), (_re_wall_time,'Elapsed_sec')):
        for m in patt.finditer(text):
            data[fld] = m.group(1)
    return data

def collect_all_static(base_dir='.', out_csv='static_summary.csv'):
    """
    Walk every OUTCAR, parse static info, and write a summary CSV.
    """
    import pandas as pd
    rows = []
    for outcar in Path(base_dir).rglob("*/OUTCAR"):
        info = parse_outcar_static(outcar)
        info['test'] = outcar.parent.name
        rows.append(info)
    df = pd.DataFrame(rows)
    df.to_csv(out_csv, index=False)
    print(f"✅ {out_csv} written with {len(df)} entries.")

if __name__ == "__main__":
    collect_all_static()
