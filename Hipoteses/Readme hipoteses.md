README — Integração SQL → Power BI
Etapa: Extração, Modelagem Analítica e Integração com BI

Nesta etapa do projeto foi realizada a extração dos dados do banco MySQL e sua preparação para análise no Power BI, com foco em manutenção industrial orientada à decisão.

A abordagem adotada separa claramente:

Camada de dados (SQL) → preparação e estruturação

Camada analítica (Power BI / DAX) → métricas e visualização

Além disso, foram aplicadas técnicas avançadas de SQL como:

CTEs (Common Table Expressions)

Window Functions

Agregações analíticas

Essas técnicas permitiram gerar insights mais robustos sem perder a granularidade dos dados.

🧠 Uso de CTE (Common Table Expressions)

As CTEs foram utilizadas para estruturar consultas complexas de forma modular e legível.

📌 Por que usar CTE?

Melhora a legibilidade do código

Permite dividir problemas complexos em etapas

Facilita manutenção e evolução das análises

✅ Exemplo aplicado: Base para análise por máquina
WITH Base AS (
    SELECT 
        MachineKey,
        COUNT(ParadaID) AS Falhas,
        SUM(MTTR_Amplo) / 60 AS Horas_Parada
    FROM Fact_Paradas
    GROUP BY MachineKey
)
SELECT * FROM Base;

👉 Aqui a CTE cria uma camada intermediária reutilizável, que pode ser usada para múltiplas análises.

⚙️ Uso de Window Functions

As Window Functions foram essenciais para análises comparativas e cumulativas, sem perder o nível de detalhe dos dados.

📊 Exemplo: Curva de Pareto (80/20)
SUM(Horas_Parada) OVER() 

👉 Calcula o total geral sem precisar agrupar tudo

SUM(Horas_Parada) OVER(ORDER BY Horas_Parada DESC)

👉 Gera o acumulado → base para Pareto

💡 Aplicação prática no projeto
ROUND(
    SUM(Horas_Parada) OVER(ORDER BY Horas_Parada DESC)
    / SUM(Horas_Parada) OVER() * 100, 2
) AS Percentual_Acumulado

👉 Permitiu identificar:

Máquinas responsáveis por 80% do impacto

Prioridades de manutenção

🔍 Uso de Normalização de Métricas

Para garantir consistência nas análises, as métricas foram padronizadas utilizando:

SUM(MTTR_Amplo) / COUNT(*) / 60 AS MTTR_horas
SUM(MTBF_Amplo) / COUNT(*) / 60 AS MTBF_horas
🎯 Benefícios:

Evita distorções por média simples

Garante comparabilidade entre máquinas

Representa melhor o comportamento real dos dados

🧮 Construção de Score de Criticidade

Foi desenvolvido um modelo de priorização baseado em múltiplos fatores:

Frequência de falhas

Tempo total de parada

Disponibilidade

📌 Lógica aplicada:
(Score_Parada * 0.5 +
 Score_Falhas * 0.3 +
 Score_Disponibilidade * 0.2)
💡 Interpretação

Maior peso → impacto operacional

Peso intermediário → frequência

Peso menor → disponibilidade

👉 Resultado: priorização mais realista para manutenção

🔄 Integração com Power BI

Após o processamento no SQL, os dados foram carregados no Power BI mantendo o nível granular.

📥 Estratégia adotada

Importação da tabela fato sem agregação

Uso de query nativa para otimização de performance

Criação de métricas via DAX

🎯 Exemplo de medidas no Power BI
Falhas = COUNT(Fact_Paradas[ParadaID])

MTTR = DIVIDE(SUM(Fact_Paradas[MTTR_Amplo]), [Falhas]) / 60

MTBF = DIVIDE(SUM(Fact_Paradas[MTBF_Amplo]), [Falhas]) / 60
🚀 Resultado da Etapa

Essa etapa permitiu:

✔ Estruturar dados para análise escalável
✔ Aplicar lógica analítica diretamente no SQL
✔ Criar base confiável para dashboards
✔ Identificar padrões de falha e impacto operacional

💣 DIFERENCIAL DO PROJETO

A utilização combinada de:

CTEs

Window Functions

Modelagem analítica

Integração com BI

demonstra uma abordagem próxima à utilizada em ambientes corporativos, indo além de análises descritivas simples.