package com.triageai.api.dto.response;

public record ClassificacaoResponse(
        String corPrevista,
        Double confianca
) {}
