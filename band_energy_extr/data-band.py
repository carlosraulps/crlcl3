
from pymatgen.io.vasp.outputs import Vasprun
import pandas as pd
import os

# 1. Checa existência dos arquivos
for fname in ("vasprun.xml", "KPOINTS"):
    if not os.path.isfile(fname):
        raise FileNotFoundError(f"Arquivo '{fname}' não encontrado no diretório atual.")

# 2. Carrega sem parsear POTCAR
vasprun = Vasprun("vasprun.xml",
                  parse_projected_eigen=True,
                  parse_potcar_file=False)

# 3. Extrai banda em Line-Mode, apontando para o KPOINTS
bs = vasprun.get_band_structure(kpoints_filename="KPOINTS",
                                line_mode=True)

# 4. Monta lista de dicionários
band_data = []
for i, kpoint in enumerate(bs.kpoints):
    label = kpoint.label or ""
    dist  = bs.distance[i]
    # bs.bands é um dict: {'up': array, 'down': array}
    for spin, band_array in bs.bands.items():
        for band_idx, energy in enumerate(band_array[:, i], start=1):
            band_data.append({
                "kpoint_index": i,
                "kpoint_label": label,
                "kpoint_distance": dist,
                "band_index": band_idx,
                "energy_eV": energy,
                "spin": spin
            })

# 5. Cria DataFrame e exporta CSV
df = pd.DataFrame(band_data)
df.to_csv("band_structure_data.csv",
          index=False,
          encoding="utf-8",
          lineterminator="\n")

print("✅ Dados exportados para 'band_structure_data.csv'")

