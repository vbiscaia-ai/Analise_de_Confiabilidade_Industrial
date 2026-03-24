ETL e Star Schema – Etapa SQL
1️⃣ Descrição da Etapa

Nesta fase do projeto, os dados processados pelo ETL em Python foram carregados no MySQL, criando as tabelas dimensionais e fato para análise.

O objetivo principal desta etapa é estruturar os dados em um Star Schema, permitindo consultas otimizadas para ferramentas de BI como Power BI ou Tableau.

2️⃣ Tabelas Criadas
Tipo	Nome da Tabela	Descrição
Dimensional	Dim_Machine	Contém a lista de máquinas (MachineKey, MachineGroup)
Dimensional	Dim_Date	Contém todas as datas do período analisado com DateKey e atributos de calendário
Dimensional	Dim_AlarmSeverity	Lista de severidades de alarme (AlarmSeverityKey, AlarmSeverityName)
Fato	Fact_Paradas	Registro de paradas/reparos com métricas de MTTR, MTBF e referência às dimensões
KPI	KPI_Por_Maquina	Métricas agregadas por máquina (total de paradas, MTTR médio, MTBF médio, disponibilidade, taxa de falha)
KPI	KPI_Global	Métricas globais agregadas (MTTR, MTBF e total de paradas)

Observação: A tabela Gold_Final ainda não foi criada. Ela será gerada posteriormente para consolidar métricas e fatos em um único dataset pronto para BI.

3️⃣ Montagem do Star Schema

As tabelas foram organizadas seguindo a metodologia Star Schema, com as seguintes relações principais:

Fact_Paradas → Dim_Machine

Fact_Paradas → Dim_Date

Fact_Paradas → Dim_AlarmSeverity

Essas relações permitem consultas eficientes, filtragem por dimensão e cálculos de KPIs.

Exemplo de consulta possível:

SELECT 
    d.MachineGroup,
    f.MTTR_Conservador,
    f.MTBF_Conservador
FROM Fact_Paradas f
JOIN Dim_Machine d ON f.MachineKey = d.MachineKey
JOIN Dim_Date dt ON f.DateKey = dt.DateKey
WHERE dt.Year = 2025;
4️⃣ Benefícios desta Estrutura

Permite análises detalhadas por máquina, por data ou por severidade de alarme.

Estrutura pronta para geração de dashboards e relatórios executivos.

Otimiza consultas de agregação de métricas de confiabilidade industrial (MTTR, MTBF, disponibilidade).

5️⃣ Próximos Passos

Criar a tabela Gold_Final consolidando dados de fato e KPIs.

Normalizar os campos numéricos (MTTR, MTBF) para evitar problemas de importação no MySQL.

Configurar foreign keys entre a tabela Gold e as dimensões/fato (Fact_Paradas, Dim_Machine, Dim_Date, Dim_AlarmSeverity).

Testar consultas de BI para validar integridade e performance.

Futuramente, implementar carga incremental para manter os dados atualizados sem recalcular o histórico completo.