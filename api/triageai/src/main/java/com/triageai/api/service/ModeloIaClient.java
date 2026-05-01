package com.triageai.api.service;

import com.triageai.api.dto.response.ClassificacaoResponse;
import com.triageai.api.entity.SinaisVitais;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;

@Service
public class ModeloIaClient {

    private final WebClient webClient;

    public ModeloIaClient(WebClient webClient) {
        this.webClient = webClient;
    }

    public ClassificacaoResponse classificar(SinaisVitais sinaisVitais) {

        try {
            return webClient.post()
                    .uri("/classificar")
                    .bodyValue(sinaisVitais)
                    .retrieve()
                    .bodyToMono(ClassificacaoResponse.class)
                    .block();

        } catch (Exception e) {
            throw new RuntimeException("Erro ao chamar modelo de IA", e);
        }
    }
}