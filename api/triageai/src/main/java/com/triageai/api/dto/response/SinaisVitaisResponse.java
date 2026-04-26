package com.triageai.api.dto.response;

import java.math.BigDecimal;

public record SinaisVitaisResponse(
        Integer idade,
        Integer frequenciaCardiaca,
        Integer pressaoSistolica,
        Integer pressaoDiastolica,
        Integer saturacaoO2,
        BigDecimal temperatura,
        Integer frequenciaRespiratoria,
        Integer dor
) {}