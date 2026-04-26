package com.triageai.api.dto.request;

import com.triageai.api.enums.TipoEntrada;

public record CriarAnaliseRequest(
        TipoEntrada tipoEntrada,
        String textoOriginal,
        DadosManuaisRequest dadosManuais
) {}