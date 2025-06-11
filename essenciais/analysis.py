
#!/usr/bin/env python3
import os, glob, re, pandas as pd
from pymatgen.io.vasp import Vasprun, Outcar
from xml.etree.ElementTree import ParseError

BASEDIR = os.path.expanduser(".")
os.chdir(BASEDIR)

def parse_outcar_cpu_time(outcar_path):
    with open(outcar_path) as f:
        for line in f:
            if "Total CPU time used" in line:
                return float(line.split(':')[-1].strip().split()[0])
    return None

def parse_outcar_energy(outcar_path):
    pat = re.compile(r"free energy.*TOTEN\s*=\s*([-\d\.]+)")
    last = None
    with open(outcar_path) as f:
        for line in f:
            m = pat.search(line)
            if m:
                last = float(m.group(1))
    return last

def parse_outcar_scf_and_mixing(outcar_path):
    """Retorna scf_steps, rms_total, rms_broyden, rms_prec."""
    scf_steps = None
    rms_total = None
    rms_broyden = None
    rms_prec   = None
    with open(outcar_path) as f:
        text = f.read()
        # SCF cycles: número dentro de parênteses em 'Iteration   1(  30)'
        iters = re.findall(r"Iteration\s+\d+\(\s*(\d+)\)", text)
        if iters:
            scf_steps = int(iters[-1])
        # rms(total) = 0.36196E-04
        m = re.findall(r"rms\(total\)\s*=\s*([-\d\.E+]+)", text)
        if m:
            rms_total = float(m[-1])
        # rms(broyden)= 0.36189E-04
        m = re.findall(r"rms\(broyden\)\s*=\s*([-\d\.E+]+)", text)
        if m:
            rms_broyden = float(m[-1])
        # rms(prec ) = 0.44527E-04
        m = re.findall(r"rms\(prec\)\s*=\s*([-\d\.E+]+)", text)
        if m:
            rms_prec = float(m[-1])
    return scf_steps, rms_total, rms_broyden, rms_prec

def collect_data(pattern, is_encut=True):
    rows = []
    for d in sorted(glob.glob(pattern)):
        outcar = os.path.join(d, "OUTCAR")
        if not os.path.exists(outcar):
            continue

        label = d.split('_')[-1]
        test = int(label) if is_encut else label

        # 1) Energia e rede via XML ou OUTCAR
        E = None; a=b=c=None
        xml = os.path.join(d, "vasprun.xml")
        if os.path.exists(xml) and os.path.getsize(xml)>100 and "</modeling>" in open(xml).read():
            try:
                vr = Vasprun(xml, parse_dos=False, exception_on_bad_xml=False)
                E = vr.final_energy
                a,b,c = vr.final_structure.lattice.abc
            except ParseError:
                pass
        if E is None:
            E = parse_outcar_energy(outcar)

        # 2) Magnetização e CPU
        try:
            M = Outcar(outcar).magnetization
        except:
            M = None
        CPU = parse_outcar_cpu_time(outcar)

        # 3) Novos campos: SCF steps e mixing RMS
        scf_steps, rms_tot, rms_bro, rms_pre = parse_outcar_scf_and_mixing(outcar)

        rows.append({
            "teste": test,
            "energia_eV": E,
            "a_ang": a, "b_ang": b, "c_ang": c,
            "magnetizacao": M,
            "cpu_time_s": CPU,
            "scf_steps": scf_steps,
            "rms_total": rms_tot,
            "rms_broyden": rms_bro,
            "rms_prec": rms_pre
        })

    return pd.DataFrame(rows)

def main():
    df_encut = collect_data("encut_*", is_encut=True)
    if not df_encut.empty:
        df_encut.sort_values("teste", inplace=True)
        df_encut.to_csv("convergencia_encut.csv", index=False)
        print("✅ convergencia_encut.csv gerado.")
    else:
        print("⚠️ Nenhum dado de ENCUT coletado.")

    df_kpts = collect_data("kpoints_*", is_encut=False)
    if not df_kpts.empty:
        df_kpts.to_csv("convergencia_kpoints.csv", index=False)
        print("✅ convergencia_kpoints.csv gerado.")
    else:
        print("⚠️ Nenhum dado de k-points coletado.")

if __name__ == "__main__":
    main()

