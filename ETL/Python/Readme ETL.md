📄 ETL de Alarmes e Métricas de Confiabilidade
1️⃣ Descrição do Projeto

Este ETL processa dados de eventos de alarmes industriais, transformando-os em métricas de manutenção e confiabilidade para análise em BI (Power BI, Tableau, etc.).

O pipeline gera métricas de MTTR, MTBF, total de paradas, KPIs por máquina e indicadores globais, estruturando os dados em um Star Schema e uma Gold Table final, pronta para consumo executivo.

O ETL agora inclui também a Dim_AlarmSeverity, permitindo padronização das severidades dos alarmes com chave numérica, para relacionamentos consistentes nas tabelas fato.

2️⃣ Estrutura de Entrada

Arquivo CSV com eventos de alarme.

Campos principais utilizados:

datetime → Data e hora do evento

assetid → Identificador do ativo

state → Estado do equipamento (N2A, A2N, etc.)

stage, alarmseverityname, transactionmessage → Metadados adicionais

O ETL detecta automaticamente o primeiro arquivo CSV na mesma pasta do script.

3️⃣ Transformações e Regras de Negócio
🔹 Padronização

Colunas padronizadas (lowercase + underscores)

Datas convertidas para datetime

Remoção de duplicados

🔹 Machine Key

Agrupa ativos em MachineGroup (ex.: ACON-VAVU)

Cada grupo recebe MachineKey sequencial

🔹 Ordenação de Eventos

Eventos ordenados por máquina e horário

Criação de colunas auxiliares: prev_state, prev_time, next_state, next_time

🔹 AlarmSeverity

Criada a dimensão Dim_AlarmSeverity com:

AlarmSeverityKey → chave numérica única

AlarmSeverityName → severidade do alarme

Atualiza tabelas fato e Gold Table com a chave AlarmSeverityKey

4️⃣ Cálculos Principais
🔹 MTTR (Mean Time to Repair)

Conservador: A2N onde prev_state == N2A

Amplo: qualquer A2N

🔹 MTBF (Mean Time Between Failures)

Conservador: tempo entre A2N atual e próximo N2A

Amplo: tempo entre A2N e próximo evento, independente do estado

5️⃣ Paradas

Todas as paradas (state == A2N) são registradas

Possíveis melhorias futuras:

Classificação de paradas:

Corretiva → resultado de falha inesperada

Programada / Preventiva → manutenção ou teste planejado

Heurísticas futuras podem usar:

Padrões de horários

Duração repetitiva

Alarmes de teste ou stage

Integração com Work Orders / SAP PM

6️⃣ Star Schema

O ETL gera tabelas para facilitar BI:

Tabela	Descrição
Dim_Machine.csv	Lista de máquinas (MachineKey, MachineGroup)
Dim_Date.csv	Datas do período de análise (Date, DateKey, Year, Month, Day, Weekday)
Dim_AlarmSeverity.csv	Lista de severidades de alarmes (AlarmSeverityKey, AlarmSeverityName)
Fact_Paradas.csv	Eventos de reparo (MTTR, MTBF, MachineKey, DateKey, AlarmSeverityKey)
Tabela_Paradas.csv	Histórico detalhado de paradas
KPI_Por_Maquina.csv	MTTR, MTBF e total de paradas por máquina
KPI_Global.csv	Métricas agregadas globais
Gold_Final_Completa.csv	Consolidação de fatos e KPIs, pronta para BI
7️⃣ Métricas Geradas

MTTR (Conservador e Amplo)

MTBF (Conservador e Amplo)

Total de Paradas

KPIs por Máquina:

Total de Paradas

MTTR médio (Conservador / Amplo)

MTBF médio (Conservador / Amplo)

Disponibilidade (MTBF / (MTBF + MTTR))

Taxa de falha (1 / MTBF)

KPI Global:

Total de paradas

MTTR global

MTBF global

8️⃣ Possíveis Melhorias Futuras

Classificação de paradas programadas / corretivas usando Work Orders, horários fixos ou heurísticas de duração

Análise de confiabilidade avançada:

Distribuição Weibull

Curva de sobrevivência por máquina

Hazard function

Criticidade das máquinas

Score de risco baseado em MTTR, MTBF e frequência de falha

Versão industrial pronta para produção: logging, alertas, tratamento de erros e arquivos faltantes

Disponibilidade e OEE calculadas por período (dia, turno, semana)

Comparação de modelos MTTR / MTBF (Conservador vs Amplo)

9️⃣ Estrutura de Exportação

Todas as tabelas são exportadas na mesma pasta do script CSV:

Dim_Machine.csv

Dim_Date.csv

Dim_AlarmSeverity.csv

Fact_Paradas.csv

Tabela_Paradas.csv

KPI_Por_Maquina.csv

KPI_Global.csv

Gold_Final_Completa.csv

1️⃣0️⃣ Benefícios do Modelo

Métricas alinhadas com RCM e engenharia de confiabilidade

Permite análise executiva e operacional

Estrutura otimizada para Power BI

Base para futuras evoluções em manutenção preditiva

Defensável tecnicamente em auditorias ou relatórios internos

1️⃣1️⃣ Observações Técnicas

Modelo determinístico, baseado apenas em estados N2A → A2N

Paradas preventivas ainda não são identificadas automaticamente

Inclui Dim_AlarmSeverity com chave numérica, garantindo integridade e suporte a Star Schema

Compatível com operações industriais reais (papel, celulose, mineração, energia)

Estrutura pronta para integrar com SQL ou ETL incremental no futuro