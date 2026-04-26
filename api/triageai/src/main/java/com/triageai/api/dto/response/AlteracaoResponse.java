package com.triageai.api.dto.response;

import com.triageai.api.enums.CorManchester;

import java.time.LocalDateTime;

public record AlteracaoResponse(
        Long id,
        CorManchester corPrevista,
        CorManchester corFinal,
        String motivo,
        LocalDateTime dataAlteracao
) {}