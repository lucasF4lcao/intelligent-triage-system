package com.triageai.api.dto.request;

import com.triageai.api.enums.CorManchester;

public record RegistrarAlteracaoRequest(
        CorManchester corFinal,
        String motivo
) {}