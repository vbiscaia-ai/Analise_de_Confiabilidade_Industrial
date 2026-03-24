1. As máquinas mais críticas (Pareto 80/20)

Pergunta:
Quais máquinas concentram a maior parte do tempo de parada?

WITH Base AS (
    SELECT 
        MachineKey,
        SUM(MTTR_Amplo) / 60 AS Horas_Parada
    FROM Fact_Paradas
    GROUP BY MachineKey
)

SELECT
    MachineKey,
    ROUND(Horas_Parada, 2) AS Horas_Parada,
    
    ROUND(
        Horas_Parada / SUM(Horas_Parada) OVER() * 100, 2
    ) AS Percentual,

    ROUND(
        SUM(Horas_Parada) OVER(ORDER BY Horas_Parada DESC)
        / SUM(Horas_Parada) OVER() * 100, 2
    ) AS Percentual_Acumulado,

    CASE
        WHEN SUM(Horas_Parada) OVER(ORDER BY Horas_Parada DESC)
             / SUM(Horas_Parada) OVER() <= 0.80 THEN 'A'
        WHEN SUM(Horas_Parada) OVER(ORDER BY Horas_Parada DESC)
             / SUM(Horas_Parada) OVER() <= 0.95 THEN 'B'
        ELSE 'C'
    END AS Classe

FROM Base
ORDER BY Horas_Parada DESC;
⚙️ 2. Relação entre falhas e tempo de parada

Pergunta:
As máquinas param muito por frequência ou por duração?

WITH Analise_Maquina AS (
    SELECT
        MachineKey,
        COUNT(ParadaID) AS Falhas,

        SUM(MTTR_Amplo) / 60 AS Horas_Parada,

        SUM(MTTR_Amplo) / COUNT(ParadaID) / 60 AS MTTR,
        SUM(MTBF_Amplo) / COUNT(ParadaID) / 60 AS MTBF

    FROM Fact_Paradas
    GROUP BY MachineKey
)

SELECT
    MachineKey,
    Falhas,
    ROUND(Horas_Parada, 2) AS Horas_Parada,
    ROUND(MTTR, 2) AS MTTR,
    ROUND(MTBF, 2) AS MTBF
FROM Analise_Maquina
ORDER BY Falhas DESC;
🧠 3. Score de criticidade (priorização de manutenção)

Pergunta:
Quais máquinas devem ser priorizadas na manutenção?

WITH Base AS (
    SELECT
        MachineKey,
        COUNT(ParadaID) AS Falhas,
        SUM(MTTR_Amplo) / 60 AS Horas_Parada,
        SUM(MTTR_Amplo) / COUNT(ParadaID) / 60 AS MTTR,
        SUM(MTBF_Amplo) / COUNT(ParadaID) / 60 AS MTBF
    FROM Fact_Paradas
    GROUP BY MachineKey
    HAVING COUNT(ParadaID) >= 3
),

Score AS (
    SELECT
        *,
        (Falhas * 1.0 / MAX(Falhas) OVER()) AS Score_Falhas,
        (Horas_Parada / MAX(Horas_Parada) OVER()) AS Score_Parada,
        (1 - (MTBF / (MTBF + MTTR))) AS Score_Disponibilidade
    FROM Base
)

SELECT
    MachineKey,
    Falhas,
    ROUND(Horas_Parada, 2) AS Horas_Parada,

    ROUND(
        (Score_Parada * 0.5 +
         Score_Falhas * 0.3 +
         Score_Disponibilidade * 0.2),
        3
    ) AS Criticidade

FROM Score
ORDER BY Criticidade DESC;
🔁 4. Frequência de falhas por máquina

Pergunta:
Quais máquinas falham com maior frequência?

SELECT
    MachineKey,
    COUNT(*) AS Falhas
FROM Fact_Paradas
GROUP BY MachineKey
ORDER BY Falhas DESC;
⏱️ 5. Tempo total de parada (impacto operacional)

Pergunta:
Quais máquinas geram maior impacto em horas paradas?

SELECT
    MachineKey,
    ROUND(SUM(MTTR_Amplo) / 60, 2) AS Horas_Parada
FROM Fact_Paradas
GROUP BY MachineKey
ORDER BY Horas_Parada DESC;
⚡ 6. Máquinas que quebram mais rápido (MTBF baixo)

Pergunta:
Quais máquinas têm menor tempo entre falhas?

SELECT
    MachineKey,
    ROUND(SUM(MTBF_Amplo) / COUNT(*) / 60, 2) AS MTBF_horas
FROM Fact_Paradas
GROUP BY MachineKey
ORDER BY MTBF_horas ASC;
🟢 7. Disponibilidade por máquina

Pergunta:
Quais máquinas estão menos disponíveis?

SELECT
    MachineKey,
    ROUND(
        AVG(MTBF_Amplo / (MTBF_Amplo + MTTR_Amplo)) * 100,
        2
    ) AS Disponibilidade_pct
FROM Fact_Paradas
GROUP BY MachineKey
ORDER BY Disponibilidade_pct ASC;
🎯 8. Scatter Plot (visão completa de performance)

Pergunta:
Como se comportam MTTR, MTBF e falhas por máquina?

SELECT
    MachineKey,
    COUNT(*) AS Falhas,

    ROUND(SUM(MTTR_Amplo) / COUNT(*) / 60, 2) AS MTTR_horas,
    ROUND(SUM(MTBF_Amplo) / COUNT(*) / 60, 2) AS MTBF_horas

FROM Fact_Paradas
GROUP BY MachineKey
HAVING COUNT(*) >= 3;
🧩 9. Classificação operacional das máquinas

Pergunta:
Quais máquinas são gargalo, críticas ou saudáveis?

WITH Base AS (
    SELECT
        MachineKey,
        COUNT(*) AS Falhas,
        SUM(MTTR_Amplo) / 60 AS Horas_Parada,
        SUM(MTTR_Amplo) / COUNT(*) / 60 AS MTTR
    FROM Fact_Paradas
    GROUP BY MachineKey
)

SELECT
    MachineKey,
    Falhas,
    ROUND(Horas_Parada, 2) AS Horas_Parada,
    ROUND(MTTR, 2) AS MTTR,

    CASE
        WHEN MTTR > 3 THEN 'Gargalo'
        WHEN Falhas > 20 THEN 'Crítico'
        ELSE 'Saudável'
    END AS Classificacao

FROM Base
ORDER BY Horas_Parada DESC;