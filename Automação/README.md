## 🏗️ scripts-infra-python

Automações em Python para ambientes corporativos Windows e Linux. Scripts voltados para redes, servidores e monitoramento, desenvolvidos como parte dos estudos em infraestrutura de TI.

## 📂 Estrutura  
scripts-infra/    
├── redes/ ## Testes e análise de rede    
├── servidores/ ## Inventário e automações de servidor    
├── monitoramento/ ## Monitoramento de recursos e disco    
├── automacao/ ## Limpeza e tarefas automatizadas    
└── README.md    

## 🔧 Principais Funcionalidades  

## 🌐 Redes & Conectividade  
Verificação de conectividade (ping em múltiplos hosts)  
Teste de portas abertas em IPs e hostnames  
Geração de relatórios de rede em .txt  

## 🖥️ Servidores & Inventário  
Coleta de CPU, RAM, disco e sistema operacional  
Exportação de inventário em .csv  
Scripts de backup automatizado com compressão .zip e rotação de arquivos  

## 📊 Monitoramento  
Monitoramento de uso de disco por partição  
Alertas configuráveis para limites de armazenamento  

## 🧹 Automação  
Limpeza de arquivos antigos baseada em X dias  
Modo de simulação (dry-run) para testes seguros  
Geração automática de logs de execução  

## 🚀 Como utilizar
git clone https://github.com/ericluanz/scripts-infra.git  
cd scripts-infra  
Instale as dependências necessárias:  
pip install psutil  
Execute o script desejado  

## ⚠️ Observação: execute conforme sua necessidade e ajuste as configurações no início de cada script.  

## 📋 Pré-requisitos  
Python 3.8+  
Sistema Windows ou Linux  
Biblioteca psutil (para scripts de sistema)  

## ⚠️ Aviso
Este repositório contém scripts de automação e diagnóstico.  

✔️ Utilize apenas em ambientes autorizados  
✔️ Teste antes de executar em produção  
✔️ Ajuste os parâmetros conforme seu ambiente  

## 🛠️ Boas práticas
✔️ Mantenha backups antes de automações críticas  
✔️ Use o modo simulação quando disponível  
✔️ Revise permissões de execução  
✔️ Evite executar scripts em produção sem validação  
