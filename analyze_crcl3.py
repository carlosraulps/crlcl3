import os
from pymatgen.io.vasp import Vasprun, Outcar
from pymatgen.electronic_structure.plotter import DosPlotter, BSPlotter
from pymatgen.core.structure import Structure
from ase.io import read
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# === PATHS ===
BASE    = "/home/crls/documents/research/abc/crcl3_report_data"
FIG_DIR = os.path.join(BASE, "graphics")
os.makedirs(FIG_DIR, exist_ok=True)

files = {
    "CONTCAR": os.path.join(BASE, "CONTCAR"),
    "OUTCAR":  os.path.join(BASE, "OUTCAR"),
    "vasprun": os.path.join(BASE, "vasprun.xml"),
    "KPOINTS": os.path.join(BASE, "KPOINTS"),
}

# === 1. STRUCTURE ANALYSIS ===
structure = Structure.from_file(files["CONTCAR"])
lat = structure.lattice
print(f"\n📐 Lattice: a={lat.a:.3f} Å, b={lat.b:.3f} Å, c={lat.c:.3f} Å; "
      f"α={lat.alpha:.2f}°, β={lat.beta:.2f}°, γ={lat.gamma:.2f}°")

# Save ASE structure plot
try:
    atoms = read(files["CONTCAR"])
    from ase.visualize.plot import plot_atoms
    ax = plot_atoms(atoms, radii=0.3, rotation=('10x,20y,0z'))  # returns Axes
    fig = ax.figure                                          # parent Figure :contentReference[oaicite:5]{index=5}
    fig.tight_layout()                                       # adjust layout on Figure
    fig.savefig(os.path.join(FIG_DIR, "crcl3_structure.png"), dpi=300)
except Exception as e:
    print("⚠️ Structure plot skipped (ASE error):", e)

# === 2. TOTAL ENERGY ===
energy = Outcar(files["OUTCAR"]).final_energy
print(f"\n⚡ Total Energy (SCF): {energy:.6f} eV")

# === 3. DOS PLOTTING ===
vasp_dos = Vasprun(files["vasprun"],
                   parse_projected_eigen=False,
                   parse_dos=True)
complete_dos = vasp_dos.complete_dos
gap = complete_dos.get_gap()

dos_plotter = DosPlotter(sigma=0.1)

# 1) Add your DOS data first:
dos_plotter.add_dos("Total DOS", complete_dos)
dos_plotter.add_dos_dict(complete_dos.get_element_dos())

# 2) THEN generate the Axes with get_plot:
dos_ax = dos_plotter.get_plot(xlim=[-5, 5])

# 3) Set title and save via the parent Figure:
dos_ax.set_title("Density of States - CrCl₃")
dos_fig = dos_ax.figure
dos_fig.tight_layout()
dos_fig.savefig(os.path.join(FIG_DIR, "crcl3_dos.png"), dpi=300)
print(f"\n📊 Band gap (from DOS): {gap:.2f} eV")

# === 4. BAND STRUCTURE PLOTTING ===

# 1) Extract the Fermi energy from the DOS run (vasp_dos.efermi is set when parse_dos=True)
fermi_level = vasp_dos.efermi                                           # efermi attribute on Vasprun :contentReference[oaicite:0]{index=0}

# 2) Parse only eigenvalues (skip DOS) so we don’t re‐parse DOS
vasp_bs = Vasprun(files["vasprun"], parse_dos=False, parse_eigen=True)

# 3) Pass the known Fermi level into get_band_structure
band = vasp_bs.get_band_structure(
    files["KPOINTS"],
    line_mode=True,
    efermi=fermi_level                                                   # supply efermi manually :contentReference[oaicite:1]{index=1}
)


# === 4. BAND STRUCTURE PLOTTING (spin‐separado, labels manuais) ===
import matplotlib.pyplot as plt
from pymatgen.electronic_structure.core import Spin

# 1) Pega o nível de Fermi já lido em vasp_dos
fermi_level = vasp_dos.efermi

# 2) Re-parse eigenvalues só (ignora DOS)
vasp_bs = Vasprun(files["vasprun"], parse_dos=False, parse_eigen=True)
bs = vasp_bs.get_band_structure(files["KPOINTS"], line_mode=True, efermi=fermi_level)

# 3) Cores e estilos para cada spin
colors = {Spin.up: "tab:red",    Spin.down: "tab:blue"}
styles = {Spin.up: "-",          Spin.down: "--"}

# 4) Distâncias acumuladas e extração de ticks/labels
dists = bs.distance                       # lista de floats
ticks, labels = [], []
for i, kp in enumerate(bs.kpoints):
    if kp.label:                          # só marca k-points especiais
        ticks.append(dists[i])
        labels.append(kp.label)

# 5) Cria figura e plota cada banda, spin por spin
fig, ax = plt.subplots(figsize=(8,5))
for spin, band_list in bs.bands.items():
    for band in band_list:
        ax.plot(dists,
                [e - fermi_level for e in band],
                color=colors[spin],
                linestyle=styles[spin],
                linewidth=1)

# 6) Linhas verticais nos ticks e configuração dos eixos
for x in ticks:
    ax.axvline(x, color="k", linewidth=0.8)
ax.set_xticks(ticks)
ax.set_xticklabels(labels)
ax.set_xlim(min(dists), max(dists))
ax.set_ylim(-5, 5)
ax.set_xlabel("Wave Vector")
ax.set_ylabel("E – E$_f$ (eV)")
ax.set_title("Band Structure – CrCl₃")

# 7) Legenda spin up/down
from matplotlib.lines import Line2D
legend_elems = [
    Line2D([0],[0], color=colors[Spin.up],   ls=styles[Spin.up],   label="Spin up"),
    Line2D([0],[0], color=colors[Spin.down], ls=styles[Spin.down], label="Spin down")
]
ax.legend(handles=legend_elems, loc="upper right")

# 8) Salva a figura
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "crcl3_band_structure.png"), dpi=300)

# 9) Imprime o band gap
bg = bs.get_band_gap()
gap_type = "Direct" if bg["direct"] else "Indirect"
print(f"\n🎶 Band gap (from Band Structure): {bg['energy']:.2f} eV ({gap_type})")
 

# Exportacao de dados

import numpy as np
import pandas as pd
from pymatgen.electronic_structure.core import Spin

# Supondo que você já tenha:
#   complete_dos = Vasprun(...).complete_dos
#   bs          = Vasprun(...).get_band_structure(...)
#   vasp_dos    = Vasprun(...) usado em DOS (para efermi)

OUT_DIR = os.path.join(BASE, "ghapics")
os.makedirs(OUT_DIR, exist_ok=True)

# === 1) EXPORTAR DOS ===
energies = np.array(complete_dos.energies)        # vetor de energias
dens = complete_dos.densities                     # pode ser ndarray ou dict de Spins

# Monta o DataFrame de DOS
if isinstance(dens, dict):
    # spin-polarizado: soma canais para o total e exporta também separado
    up   = np.array(dens[Spin.up])
    down = np.array(dens[Spin.down])
    total = up + down
    df_dos = pd.DataFrame({
        "E": energies,
        "DOS_total": total,
        "DOS_up":    up,
        "DOS_down":  down
    })
else:
    # não-spin: dens já é ndarray
    df_dos = pd.DataFrame({
        "E": energies,
        "DOS_total": np.array(dens)
    })

dos_csv = os.path.join(OUT_DIR, "crcl3_dos.csv")
df_dos.to_csv(dos_csv, index=False)
print(f"✅ DOS exportado em {dos_csv}")

# === 2) EXPORTAR BAND STRUCTURE ===
dists = np.array(bs.distance)   # distâncias acumuladas nos k‐points
data_bs = {"k": dists}

# cada spin e cada banda vira uma coluna
for spin, band_list in bs.bands.items():
    for idx, band in enumerate(band_list):
        # subtrai efemrio para plot em torno de zero
        col = np.array(band) - vasp_dos.efermi
        data_bs[f"band_{spin.name}_{idx}"] = col

df_bs = pd.DataFrame(data_bs)
bs_csv = os.path.join(OUT_DIR, "crcl3_band.csv")
df_bs.to_csv(bs_csv, index=False)
print(f"✅ Band structure exportada em {bs_csv}")
# 2) Dados de banda: distância acumulada vs cada banda e spin
dists = np.array(bs.distance)                        # distâncias k :contentReference[oaicite:2]{index=2}
data_bs = {"k": dists}
for spin, bands in bs.bands.items():
    for i, band in enumerate(bands):
        data_bs[f"band_{spin.name}_{i}"] = np.array(band) - vasp_dos.efermi
pd.DataFrame(data_bs).to_csv("ghapics/crcl3_band.csv", index=False)
