
#!/bin/bash

# === CONFIGURAÇÕES ===
POTCAR_DIR="$HOME/potpaw_PBE"     # Caminho base onde estão os pseudopotenciais
CRCL3_CONTCAR="CONTCAR"           # Arquivo final de CrCl3 relaxado

# === FUNÇÃO PARA ESCREVER INCAR ===
write_incar() {
    cat > INCAR <<EOF
PREC = Accurate
ENCUT = 500
ISMEAR = 0
SIGMA = 0.05
EDIFF = 1E-6
ISPIN = 2
LCHARG = .FALSE.
LWAVE  = .FALSE.
NSW = 0
IBRION = -1
ISYM = 0
LREAL = .FALSE.
EOF
}

# === FUNÇÃO PARA KPOINTS ===
write_kpoints() {
    local type=$1
    if [[ "$type" == "solid" ]]; then
        cat > KPOINTS <<EOF
Automatic mesh
0
Monkhorst-Pack
6 6 4
0 0 0
EOF
    else
        cat > KPOINTS <<EOF
Gamma-point only
0
Gamma
1 1 1
0 0 0
EOF
    fi
}

# === CRCL3_SOLID ===
mkdir -p crcl3_solid && cd crcl3_solid
cp ../$CRCL3_CONTCAR POSCAR
write_incar
echo "MAGMOM = 2*3.0 6*0.6" >> INCAR
write_kpoints solid
cat $POTCAR_DIR/Cr/POTCAR $POTCAR_DIR/Cl/POTCAR > POTCAR
cd ..

# === CR_BULK ===
mkdir -p cr_bulk && cd cr_bulk
cat > POSCAR <<EOF
Cr bulk bcc
1.0
  2.48  0.00  0.00
  0.00  2.48  0.00
  0.00  0.00  2.48
Cr
1
Direct
0.0 0.0 0.0
EOF
write_incar
echo "MAGMOM = 1*5.0" >> INCAR
write_kpoints solid
cat $POTCAR_DIR/Cr/POTCAR > POTCAR
cd ..

# === CL2_MOLECULE ===
mkdir -p cl2_molecule && cd cl2_molecule
cat > POSCAR <<EOF
Cl2 molecule
1.0
  20.0 0.0 0.0
  0.0 20.0 0.0
  0.0 0.0 20.0
Cl
2
Cartesian
0.0 0.0 0.0
0.0 0.0 1.99
EOF
write_incar
echo "MAGMOM = 2*1.0" >> INCAR
write_kpoints gas
cat $POTCAR_DIR/Cl/POTCAR > POTCAR
cd ..

# === CR_ATOM ===
mkdir -p cr_atom && cd cr_atom
cat > POSCAR <<EOF
Cr atom
1.0
  20.0 0.0 0.0
  0.0 20.0 0.0
  0.0 0.0 20.0
Cr
1
Cartesian
0.0 0.0 0.0
EOF
write_incar
echo "MAGMOM = 1*5.0" >> INCAR
write_kpoints gas
cat $POTCAR_DIR/Cr/POTCAR > POTCAR
cd ..

# === CL_ATOM ===
mkdir -p cl_atom && cd cl_atom
cat > POSCAR <<EOF
Cl atom
1.0
  20.0 0.0 0.0
  0.0 20.0 0.0
  0.0 0.0 20.0
Cl
1
Cartesian
0.0 0.0 0.0
EOF
write_incar
echo "MAGMOM = 1*1.0" >> INCAR
write_kpoints gas
cat $POTCAR_DIR/Cl/POTCAR > POTCAR
cd ..

echo "✅ Diretórios e arquivos criados com sucesso."
