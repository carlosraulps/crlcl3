
import pandas as pd
import matplotlib.pyplot as plt

# Read the CSVs
df_encut = pd.read_csv('convergencia_iters_encut.csv')
df_kpts = pd.read_csv('convergencia_iters_kpoints.csv')

# Plot Energy vs Iteration for ENCUT
plt.figure()
for teste, group in df_encut.groupby('teste'):
    plt.plot(group['iteracao'], group['energia_eV'], marker='o', label=f'ENCUT {teste}')
plt.xlabel('Iteration SCF')
plt.ylabel('Energy (eV)')
plt.title('Convergence of SCF Energy per ENCUT')
plt.legend()
plt.tight_layout()
plt.savefig('energy_vs_iter_encut.png')

# Plot RMS(total) vs Iteration for ENCUT
plt.figure()
for teste, group in df_encut.groupby('teste'):
    plt.plot(group['iteracao'], group['rms_total'], marker='o', label=f'ENCUT {teste}')
plt.xlabel('Iteration SCF')
plt.ylabel('RMS(total)')
plt.title('Convergence of RMS(total) per ENCUT')
plt.legend()
plt.tight_layout()
plt.savefig('rms_total_vs_iter_encut.png')

# Plot Energy vs Iteration for k-points
plt.figure()
for teste, group in df_kpts.groupby('teste'):
    plt.plot(group['iteracao'], group['energia_eV'], marker='o', label=f'k-points {teste}')
plt.xlabel('Iteration SCF')
plt.ylabel('Energy (eV)')
plt.title('Convergence of SCF Energy per k-points')
plt.legend()
plt.tight_layout()
plt.savefig('energy_vs_iter_kpts.png')

# Plot RMS(total) vs Iteration for k-points
plt.figure()
for teste, group in df_kpts.groupby('teste'):
    plt.plot(group['iteracao'], group['rms_total'], marker='o', label=f'k-points {teste}')
plt.xlabel('Iteration SCF')
plt.ylabel('RMS(total)')
plt.title('Convergence of RMS(total) per k-points')
plt.legend()
plt.tight_layout()
plt.savefig('rms_total_vs_iter_kpts.png')

# Show plots
plt.show()

