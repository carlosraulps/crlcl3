
#!/usr/bin/env bash
set -euo pipefail

# 1) Mata todos os processos VASP (SIGTERM suave, depois SIGKILL se necessário)
echo "🛑 Encerrando processos VASP..."
pkill -f vasp_std                               # envia SIGTERM a todos os comandos contendo “vasp_std” :contentReference[oaicite:0]{index=0}  
sleep 5                                         # aguarda 5 s para desligamento gracioso  
pkill -9 -f vasp_std                            # envia SIGKILL para forçar término, se algum persistir :contentReference[oaicite:1]{index=1}  

# 2) Itera sobre cada pasta de teste e marca com tag
echo "🏷️ Tagueando diretórios..."
for d in encut_* kpoints_*; do
  # verifica se vasprun.xml existe E está completo (fechamento de tag </modeling>)
  if [[ ! -f "$d/vasprun.xml" ]] || ! grep -q "</modeling>" "$d/vasprun.xml"; then
    touch "$d/FAILED.tag"                        # cria arquivo indicando falha ou truncamento :contentReference[oaicite:2]{index=2}  
  else
    touch "$d/DONE.tag"                          # cria arquivo indicando sucesso :contentReference[oaicite:3]{index=3}  
  fi
done

echo "✅ Processos encerrados e diretórios tagueados."
