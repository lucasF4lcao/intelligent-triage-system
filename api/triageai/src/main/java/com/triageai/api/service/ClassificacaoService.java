package com.triageai.api.service;

import com.triageai.api.dto.response.ClassificacaoResponse;
import com.triageai.api.entity.SinaisVitais;
import org.springframework.stereotype.Service;

@Service
public class ClassificacaoService {

    private final ModeloIaClient modeloIaClient;

    public ClassificacaoService(ModeloIaClient modeloIaClient) {
        this.modeloIaClient = modeloIaClient;
    }

    public ClassificacaoResponse classificar(SinaisVitais sinais) {
        try {
            return modeloIaClient.classificar(sinais);
        } catch (Exception e) {
            throw new RuntimeException("Erro ao classificar", e);
        }
    }
}