# 🛠️ Scripts de Infraestrutura — Python

Automações do dia a dia para ambientes corporativos Windows. Desenvolvidos como parte dos meus estudos em infraestrutura de TI.

---

## Scripts disponíveis

| Script | Área | Descrição |
|---|---|---|
| `verificador_conectividade.py` | Redes | Testa ping e porta em lista de servidores e gera relatório `.txt` |
| `scanner_portas.py` | Redes | Verifica portas abertas em um IP ou hostname |
| `inventario_maquina.py` | Servidores | Coleta CPU, RAM, disco e SO — exporta em `.csv` |
| `backup_automatizado.py` | Servidores | Compacta pastas em `.zip` com timestamp e rotação automática |
| `alerta_disco.py` | Monitoramento | Monitora partições e alerta quando uso ultrapassar o limite |
| `limpeza_arquivos_antigos.py` | Automação | Remove ou move arquivos com mais de X dias de uma pasta |

---

## Pré-requisitos

- Python 3.8+
- Biblioteca `psutil` (necessária para `inventario_maquina.py` e `alerta_disco.py`)

```bash
pip install psutil
```

Os demais scripts usam apenas bibliotecas padrão do Python.

---

## Como usar

1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/scripts-infra.git
cd scripts-infra
```

2. Edite as configurações no topo de cada script conforme seu ambiente

3. Execute o script desejado
```bash
python nome_do_script.py
```

---

## Estrutura do repositório

```
scripts-infra/
├── redes/
│   ├── verificador_conectividade.py
│   └── scanner_portas.py
├── servidores/
│   ├── inventario_maquina.py
│   └── backup_automatizado.py
├── monitoramento/
│   └── alerta_disco.py
├── automacao/
│   └── limpeza_arquivos_antigos.py
└── README.md
```

---

## Observações

- O `scanner_portas.py` deve ser usado apenas em equipamentos e redes que você tem permissão para auditar.
- O `limpeza_arquivos_antigos.py` possui um **modo simulação** (ativado por padrão) que lista o que seria removido sem alterar nada.
- Todos os scripts geram arquivos de log na mesma pasta de execução.
