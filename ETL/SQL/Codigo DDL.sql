CREATE database alarmes_industriais2;
USE alarmes_industriais2;

-- 1️⃣ Tabela Dim_Machine
-- ===================================================
CREATE TABLE Dim_Machine (
    MachineKey INT PRIMARY KEY AUTO_INCREMENT,
    MachineGroup VARCHAR(50) NOT NULL
);

-- ===================================================
-- 2️⃣ Tabela Dim_Date
-- ===================================================
CREATE TABLE Dim_Date (
    DateKey INT PRIMARY KEY,          -- YYYYMMDD
    Date DATE NOT NULL,
    Year INT,
    Month INT,
    Day INT,
    Weekday VARCHAR(10)
);

-- ===================================================
-- 3️⃣ Tabela Dim_AlarmSeverity (exemplo)
-- ===================================================
CREATE TABLE Dim_AlarmSeverity (
    AlarmSeverityKey INT PRIMARY KEY AUTO_INCREMENT,
    AlarmSeverityName VARCHAR(50) NOT NULL
);

-- ===================================================
-- 4️⃣ Tabela Fact_Paradas
-- ===================================================
CREATE TABLE Fact_Paradas (
    ParadaID BIGINT PRIMARY KEY AUTO_INCREMENT,
    MachineKey INT NOT NULL,
    DateKey INT NOT NULL,
    AlarmSeverityKey INT NULL,
    MTTR_Conservador DOUBLE,
    MTTR_Amplo DOUBLE,
    MTBF_Conservador DOUBLE,
    MTBF_Amplo DOUBLE,
    Tipo_Parada VARCHAR(50),

    -- Chaves estrangeiras
    CONSTRAINT FK_Fact_Machine FOREIGN KEY (MachineKey) REFERENCES Dim_Machine(MachineKey),
    CONSTRAINT FK_Fact_Date FOREIGN KEY (DateKey) REFERENCES Dim_Date(DateKey),
    CONSTRAINT FK_Fact_AlarmSeverity FOREIGN KEY (AlarmSeverityKey) REFERENCES Dim_AlarmSeverity(AlarmSeverityKey)
);

--
