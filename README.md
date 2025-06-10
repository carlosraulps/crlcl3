## ✅ 1. **Essential Files for the Report**

Here's the curated list of what you **actually need** for report plots and tables:

### 📁 `1_relaxation/`

```bash
1_relaxation/CONTCAR        # Relaxed structure (for structure image/table)
1_relaxation/OUTCAR         # Final energies, lattice vectors
1_relaxation/XDATCAR        # Optional: ionic steps
```

### 📁 `2_sc_calculation/`

```bash
2_sc_calculation/OUTCAR     # SCF total energy
```

### 📁 `3_dos/`

```bash
3_dos/DOSCAR                # Total + projected DOS
3_dos/vasprun.xml           # Needed for plotting with pymatgen/sumo
3_dos/FERMI_ENERGY          # Fermi level
3_dos/PROCAR                # Optional: orbital-resolved DOS
```

### 📁 `4_band_structure/`

```bash
4_band_structure/KPOINTS             # High-symmetry path
4_band_structure/EIGENVAL            # Raw band energies
4_band_structure/vasprun.xml         # Band structure (for pymatgen/sumo)
4_band_structure/FERMI_ENERGY        # Needed to align bands
4_band_structure/BAND.dat            # VASPkit-ready band plot data
4_band_structure/REFORMATTED_BAND_*.dat  # Spin-up/down bands
4_band_structure/KLINES.dat          # For band plot axis
```

---

```

📁 This will download all essential files to your local folder:

```bash
~/projects/crcl3_report_data/
```

---

## 📌 Notes

* Your `gn8` will handle creating the local directory and using the jump host (`bastiao`) to reach `cn08`.
* Make sure your local `~/.ssh/config` has the proper `Host bastiao` and `Host cn08` settings.
* You can always add/remove paths if needed — just keep the last argument as the **local destination**.

---
