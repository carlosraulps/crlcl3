
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'

echo "📋 Analisando diretórios de convergência..."
cd ~/crcl3/convergencia

output_csv="convergencia_resultados.csv"
echo "dir,encut,kpoints,energy_eV,magnetization,scf_steps,cpu_time" > "$output_csv"

for dir in encut_* kpoints_*; do
  OUTCAR="$dir/OUTCAR"
  if [[ ! -f $OUTCAR ]]; then
    echo "⚠️ $dir: OUTCAR não encontrado." >&2
    continue
  fi

  # 1) Última energia livre (TOTEN)
  ENERGY=$(grep -i "free energy.*TOTEN" "$OUTCAR" | tail -n1 | awk '{print $(NF-1)}')
  if [[ -z $ENERGY ]]; then
    echo "⚠️ $dir: falha ao extrair energia" >&2
    ENERGY="NA"
  fi

  # 2) Última magnetização total (última linha contendo "number of electron")
  MAG=$(grep -i "number of electron" "$OUTCAR" | tail -n1 | awk '{print $NF}')
  if [[ -z $MAG ]]; then
    echo "⚠️ $dir: falha ao extrair magnetização" >&2
    MAG="NA"
  fi

  # 3) Número de passos SCF (contagem de "DAV:")
  SCF=$(grep -c "DAV:" "$OUTCAR" || echo 0)

  # 4) Último tempo de CPU (linha "EDDAV:" → cpu time <CPU> : real time <RT>)
  CPU_TIME=$(grep -i "EDDAV:.*cpu time" "$OUTCAR" | tail -n1 | awk '{print $4}')
  if [[ -z $CPU_TIME ]]; then
    echo "⚠️ $dir: falha ao extrair CPU time" >&2
    CPU_TIME="NA"
  fi

  # 5) Tipo de teste (encut vs kpoints)
  if [[ $dir == encut_* ]]; then
    ENCUT=$(awk '/^ENCUT/ {print $3; exit}' "$dir/INCAR")
    KPT="default"
  else
    ENCUT="520"
    # 4a) mesh: pega a linha após "Monkhorst-Pack"
    KPT=$(awk '/Monkhorst-Pack/{getline; print $1"x"$2"x"$3; exit}' "$dir/KPOINTS")
  fi

  printf '%s,%s,%s,%s,%s,%s,"%s"\n' \
    "$dir" "$ENCUT" "$KPT" "$ENERGY" "$MAG" "$SCF" "$CPU_TIME" \
    >> "$output_csv"
done

echo "✅ Dados salvos em $output_csv"
