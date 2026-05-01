package com.triageai.api.dto.response;

import com.triageai.api.enums.CorManchester;
import com.triageai.api.enums.StatusExecucao;
import com.triageai.api.enums.TipoEntrada;

import java.math.BigDecimal;
import java.time.LocalDateTime;

public record AnaliseTriagemResponse(
        Long id,
        LocalDateTime dataCriacao,
        TipoEntrada tipoEntrada,
        SinaisVitaisResponse sinaisVitais,
        CorManchester corPrevista,
        BigDecimal confianca,
        StatusExecucao statusExecucao
) {}