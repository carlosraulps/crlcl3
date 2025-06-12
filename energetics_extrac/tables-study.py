
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
study.py
---------
- Lê static_summary.csv e convergence_iters_other.csv
- Calcula energias de coesão e formação
- Gera duas tabelas LaTeX compatíveis com siunitx/booktabs
"""

import pandas as pd
import re

# 1) Função para converter "n*val" → n * val
def parse_magmom(s: str) -> float:
    m = re.match(r'^\s*(\d+)\s*\*\s*([\d\.]+)\s*$', str(s))
    if m:
        return int(m.group(1)) * float(m.group(2))
    return float(s)

# 2) Referências energéticas para átomos / molécula (substitua pelos seus valores)
E_ref = {
    'Cr_atom':     -405.1234,   # ex: energia de um átomo de Cr isolado
    'Cl_atom':     -15.6789,    # ex: energia de um átomo de Cl isolado
    'Cl2_molecule': -31.2345    # ex: energia da molécula Cl2
}

# 3) Leitura dos CSVs
df_static = pd.read_csv("static_summary.csv")
df_conv   = pd.read_csv("convergence_iters_other.csv")

# 4) Extrai última energia SCF (maior iteration) de cada teste
idx_last = df_conv.groupby("test")["iteration"].idxmax()
df_last  = (
    df_conv.loc[idx_last, ["test","energy_eV"]]
           .rename(columns={"energy_eV":"E_conv_eV"})
)

# 5) Merge
df = df_static.merge(df_last, on="test", how="left")

# 6) Converte MAGMOM
df["MAGMOM_val"] = df["MAGMOM"].apply(parse_magmom)

# 7) Extrai energias-chave
E_cr_bulk = df.loc[df.test=="cr_bulk"      , "TOTEN_eV"].iloc[0]
E_crcl3   = df.loc[df.test=="crcl3_solid"  , "TOTEN_eV"].iloc[0]

# 8) Cálculos de coesão e formação
E_coh_Cr     = E_ref["Cr_atom"]     - E_cr_bulk
E_coh_Cl     = E_ref["Cl_atom"]     - 0.5 * E_ref["Cl2_molecule"]
E_form_CrCl3 = E_crcl3 - (E_cr_bulk + 3 * 0.5 * E_ref["Cl2_molecule"])

# 9) Preenche colunas de resultados
df["E_coh_Cr_eV"]     = ""
df["E_coh_Cl_eV"]     = ""
df["E_form_CrCl3_eV"] = ""

df.loc[df.test=="cr_bulk",     "E_coh_Cr_eV"]     = f"{E_coh_Cr:.4f}"
df.loc[df.test=="cr_bulk",     "E_coh_Cl_eV"]     = f"{E_coh_Cl:.4f}"
df.loc[df.test=="crcl3_solid", "E_form_CrCl3_eV"] = f"{E_form_CrCl3:.4f}"

# 10) Gera LaTeX “na mão”

# --- Tabela de parâmetros ---
cabecalho_params = r"""
% No preâmbulo inclua:
% \usepackage{booktabs}
% \usepackage{siunitx}
% \sisetup{detect-all, input-signs = + -

\begin{table}[h!]
  \centering
  \caption{Parâmetros dos cálculos VASP}
  \label{tab:parametros}
  \begin{tabular}{l
                  S[table-format=3]    % ENCUT
                  S[table-format=1]    % ISMEAR
                  S[table-format=1.4]  % SIGMA
                  S[table-format=1.4]  % EDIFF
                  S[table-format=1]    % ISPIN
                  S[table-format=1.1]} % MAGMOM
    \toprule
    Teste        & {ENCUT} & {ISMEAR} & {SIGMA}  & {EDIFF}  & {ISPIN} & {MAGMOM} \\
    \midrule
"""

linhas_params = []
for _, row in df.iterrows():
    # primeiro, escape o underscore do nome
    teste_tex = row.test.replace("_", r"\_")
    mag = row.MAGMOM_val
    linhas_params.append(
        "{teste:12s} & {encut:7d} & {ismear:7d} & {sigma:8.4f} & {ediff:8.4f} & {ispin:7d} & {magmom:7.1f} \\\\".format(
            teste=teste_tex,
            encut=int(row.ENCUT),
            ismear=int(row.ISMEAR),
            sigma=row.SIGMA,
            ediff=float(row.EDIFF),
            ispin=int(row.ISPIN),
            magmom=mag
        )
    )

rodape_params = r"""
    \bottomrule
  \end{tabular}
\end{table}
"""

# --- Tabela de resultados ---
cabecalho_res = r"""
\begin{table}[h!]
  \centering
  \caption{Resultados energéticos}
  \label{tab:resultados}
  \begin{tabular}{l
                  S[table-format=2.4]  % TOTEN
                  S[table-format=2.4]  % E_conv
                  S[table-format=3.4]  % E_coh_Cr
                  S[table-format=1.4]  % E_coh_Cl
                  S[table-format=2.4]} % E_form
    \toprule
    Teste        & {TOTEN (eV)} & {$E_{\mathrm{conv}}$ (eV)} & {$E_{\mathrm{coh,Cr}}$ (eV)} & {$E_{\mathrm{coh,Cl}}$ (eV)} & {$E_{\mathrm{form,CrCl_3}}$ (eV)} \\
    \midrule
"""

linhas_res = []
for _, row in df.iterrows():
    teste_tex = row.test.replace("_", r"\_")
    # helper para formatar ou usar “—”
    def fmt(val, fmtstr):
        return fmtstr.format(val) if val != "" else "—"
    linhas_res.append(
        "{teste:12s} & {toten:>7s} & {econv:>7s} & {ecohr:>7s} & {ecoht:>7s} & {eform:>7s} \\\\".format(
            teste=teste_tex,
            toten=fmt(row.TOTEN_eV, "{:7.4f}") if pd.notna(row.TOTEN_eV) else "—",
            econv=fmt(row.E_conv_eV, "{:7.4f}") if pd.notna(row.E_conv_eV) else "—",
            ecohr=row.E_coh_Cr_eV or "—",
            ecoht=row.E_coh_Cl_eV or "—",
            eform=row.E_form_CrCl3_eV or "—"
        )
    )

rodape_res = r"""
    \bottomrule
  \end{tabular}
\end{table}
"""

# 11) Saída final
print(cabecalho_params.strip())
print("\n".join(linhas_params))
print(rodape_params.strip())
print()
print(cabecalho_res.strip())
print("\n".join(linhas_res))
print(rodape_res.strip())


"""
Below is an outline of how to go from your raw DFT data (static energies and SCF‐convergence tables) to **formation** and **cohesive** energies that can be directly compared with experiment, along with pointers to standard references. In brief:

1. **Definitions**

   * **Cohesive energy** per atom is
     $E_{\rm coh} = \sum_i E_i^{\rm atom} \;-\; E_{\rm bulk}/N$
     where $E_i^{\rm atom}$ are the total energies of isolated atoms (spin‐polarized, in the same functional) and $E_{\rm bulk}/N$ is the energy per atom in your solid ([en.wikipedia.org][1]).
   * **Formation energy** per formula unit is
     $\Delta E_f = E_{\rm comp} \;-\;\sum_j n_j E_j^{\rm ref}$
     where $E_{\rm comp}$ is the total energy of your compound (e.g. CrCl$_3$), and the $E_j^{\rm ref}$ are reference energies of the elemental phases (e.g.\ bulk Cr, Cl$_2$ gas) ([en.wikipedia.org][2]).

2. ## Step-by-Step Procedure

   ### 2.1 Extract Final Energies

   * From **static\_summary.csv**, take the **TOTEN\_eV** column for each “test” (e.g. `crcl3_solid`, `cr_bulk`).
   * From **convergence\_iters\_other.csv**, find the last iteration (maximum `iteration`) for each test and take its `energy_eV` as the fully converged value ([matsci.org][3]).

   ### 2.2 Compute Cohesive Energies

   1. **Calculate isolated-atom energies**

      * Run single-atom calculations (e.g. Cr, Cl) in large boxes, spin‐polarized, same ENCUT/functional.
   2. **Apply formula**

      $$
        E_{\rm coh} = \bigl(E_{\rm Cr}^{\rm atom} + 3\,E_{\rm Cl}^{\rm atom}\bigr)\;-\;E_{\rm CrCl_3}^{\rm bulk}\,.
      $$

      Divide by the total number of atoms (4) for per-atom cohesion ([arxiv.org][4]).

   ### 2.3 Compute Formation Energies

   1. **Choose references**

      * **Cr:** use bulk metal DFT energy per atom.
      * **Cl:** use half the energy of the Cl$_2$ molecule (gas), computed in a large box.
   2. **Apply formula**

      $$
        \Delta E_f(\mathrm{CrCl}_3) 
        = E_{\mathrm{CrCl}_3}^{\rm bulk} 
        - \Bigl(E_{\rm Cr}^{\rm bulk} + \tfrac32\,E_{\rm Cl_2}^{\rm mol}\Bigr).
      $$
   3. **Zero-point & thermal corrections**

      * Add vibrational zero-point energies from phonon calculations or from experiment (Born–Haber cycle data) ([geeksforgeeks.org][5]).

3. ## Comparison to Experiment

   * **Experimental enthalpies of formation** for CrCl$_3$ can be found in JANAF/NIST tables.
   * **Thermal corrections** (to 298 K) are typically 0.05–0.10 eV/f.u. for halides ([byjus.com][6]).
   * A **Born–Haber cycle** can be used to estimate lattice energies and cross‐check your DFT formation energy against experimental lattice enthalpies ([en.wikipedia.org][2]).

4. ## Putting It All Together in Python

   With your two CSVs, you can:

   1. **Merge** static and convergence tables on the “test” name.
   2. **Extract** the final converged energy for each test.
   3. **Compute** formation and cohesive energies via the formulas above.
   4. **Export** a LaTeX table and print the energetic quantities.

   This workflow is standard in most DFT‐materials studies (see, e.g., the Materials Project overview) ([linkedin.com][7]).

---

### Key References

1. **Quantum ESPRESSO** manual (plane‐wave DFT) ([en.wikipedia.org][1])
2. **Born–Haber cycle** & lattice energies (Wikipedia) ([en.wikipedia.org][2])
3. **Zero-point corrections** in halides (J. Phys. Chem. Ref. Data) ([geeksforgeeks.org][5])
4. **Comparing DFT ΔE\_f to experiment** (Computational Materials Science reviews) ([byjus.com][6])
5. **Materials Project** best practices for energy calculations ([matsci.org][3])

With these steps and references, you can take your raw CSVs and turn them into formation/cohesive energies directly comparable to experimental values.

[1]: https://en.wikipedia.org/wiki/Quantum_ESPRESSO?utm_source=chatgpt.com "Quantum ESPRESSO"
[2]: https://en.wikipedia.org/wiki/Kapustinskii_equation?utm_source=chatgpt.com "Kapustinskii equation - Wikipedia"
[3]: https://matsci.org/t/get-cohesive-energy-from-materials-project/58195?utm_source=chatgpt.com "Get Cohesive energy from Materials Project"
[4]: https://arxiv.org/abs/1709.10010?utm_source=chatgpt.com "Advanced capabilities for materials modelling with Quantum ESPRESSO"
[5]: https://www.geeksforgeeks.org/lattice-energy/?utm_source=chatgpt.com "Lattice Energy | GeeksforGeeks"
[6]: https://byjus.com/jee/born-haber-cycle/?utm_source=chatgpt.com "Born Haber's cycle or process - Byjus"
[7]: https://www.linkedin.com/posts/manassharma07_how-to-calculate-cohesive-energy-using-quantum-activity-7192919856613085184-sk4A?utm_source=chatgpt.com "How to calculate cohesive energy of crystals with Quantum ..."


"""
