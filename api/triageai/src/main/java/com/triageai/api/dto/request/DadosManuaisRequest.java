package com.triageai.api.dto.request;

import java.math.BigDecimal;

public record DadosManuaisRequest(
        Integer idade,
        Integer frequenciaCardiaca,
        Integer pressaoSistolica,
        Integer pressaoDiastolica,
        Integer saturacaoO2,
        BigDecimal temperatura,
        Integer frequenciaRespiratoria,
        Integer dor
) {}