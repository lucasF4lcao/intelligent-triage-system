CREATE TABLE analise_triagem (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    data_criacao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    texto_original TEXT NOT NULL,

    tipo_entrada ENUM('TEXTO', 'MANUAL') NOT NULL DEFAULT 'TEXTO',

    cor_prevista ENUM('VERMELHO', 'LARANJA', 'AMARELO', 'VERDE', 'AZUL') NULL,

    confianca DECIMAL(5,2) NULL,

    status_execucao ENUM('SUCESSO', 'ERRO') NOT NULL DEFAULT 'SUCESSO'
);

CREATE TABLE sinais_vitais (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    analise_triagem_id BIGINT NOT NULL UNIQUE,

    idade INT NULL,
    frequencia_cardiaca INT NULL,
    pressao_sistolica INT NULL,
    pressao_diastolica INT NULL,
    saturacao_o2 INT NULL,
    temperatura DECIMAL(4,1) NULL,
    frequencia_respiratoria INT NULL,
    dor INT NULL,

    CONSTRAINT fk_sinais_vitais_analise
        FOREIGN KEY (analise_triagem_id)
        REFERENCES analise_triagem(id)
        ON DELETE CASCADE
);

CREATE TABLE registro_alteracao (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,

    analise_triagem_id BIGINT NOT NULL,

    cor_prevista ENUM('VERMELHO', 'LARANJA', 'AMARELO', 'VERDE', 'AZUL') NOT NULL,
    cor_final ENUM('VERMELHO', 'LARANJA', 'AMARELO', 'VERDE', 'AZUL') NOT NULL,

    motivo VARCHAR(255) NULL,

    data_alteracao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_registro_alteracao_analise
        FOREIGN KEY (analise_triagem_id)
        REFERENCES analise_triagem(id)
        ON DELETE CASCADE
);

CREATE INDEX idx_analise_data_criacao ON analise_triagem(data_criacao);
CREATE INDEX idx_alteracao_data ON registro_alteracao(data_alteracao);