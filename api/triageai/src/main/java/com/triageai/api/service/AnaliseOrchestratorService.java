package com.triageai.api.service;

import com.triageai.api.dto.response.AnaliseTriagemResponse;
import com.triageai.api.dto.response.ClassificacaoResponse;
import com.triageai.api.entity.AnaliseTriagem;
import com.triageai.api.entity.SinaisVitais;
import com.triageai.api.enums.CorManchester;
import com.triageai.api.enums.StatusExecucao;
import com.triageai.api.enums.TipoEntrada;
import com.triageai.api.repository.AnaliseTriagemRepository;
import com.triageai.api.repository.SinaisVitaisRepository;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Service
public class AnaliseOrchestratorService {

    private final FhirParserService fhirParserService;
    private final ClassificacaoService classificacaoService;
    private final AnaliseTriagemRepository analiseRepository;
    private final SinaisVitaisRepository sinaisRepository;

    public AnaliseOrchestratorService(
            FhirParserService fhirParserService,
            ClassificacaoService classificacaoService,
            AnaliseTriagemRepository analiseRepository,
            SinaisVitaisRepository sinaisRepository
    ) {
        this.fhirParserService = fhirParserService;
        this.classificacaoService = classificacaoService;
        this.analiseRepository = analiseRepository;
        this.sinaisRepository = sinaisRepository;
    }

    public AnaliseTriagemResponse processarFhir(String bundleJson) {

        SinaisVitais sinais = fhirParserService.extrairSinaisVitais(bundleJson);

        ClassificacaoResponse classificacao;

        try {
            classificacao = classificacaoService.classificar(sinais);
        } catch (Exception e) {
            classificacao = new ClassificacaoResponse("VERMELHO", 0.0);
        }

        AnaliseTriagem analise = new AnaliseTriagem();
        analise.setData_criacao(LocalDateTime.now());
        analise.setTipo_entrada(TipoEntrada.FHIR);
        analise.setStatus_execucao(StatusExecucao.SUCESSO);

        analise.setCor_prevista(CorManchester.valueOf(classificacao.corPrevista().toUpperCase()));

        analise.setConfianca(BigDecimal.valueOf(classificacao.confianca()));

        analise = analiseRepository.save(analise);

        sinais.setAnaliseTriagem(analise);
        sinaisRepository.save(sinais);

        return mapToResponse(analise, sinais);
    }

    private AnaliseTriagemResponse mapToResponse(AnaliseTriagem analise, SinaisVitais sinais) {

        var sinaisResponse = new com.triageai.api.dto.response.SinaisVitaisResponse(
                sinais.getIdade(),
                sinais.getFrequencia_cardiaca(),
                sinais.getPressao_sistolica(),
                sinais.getPressao_diastolica(),
                sinais.getSaturacao_o2(),
                sinais.getTemperatura(),
                sinais.getFrequencia_respiratoria(),
                sinais.getDor()
        );

        return new AnaliseTriagemResponse(
                analise.getId(),
                analise.getData_criacao(),
                analise.getTipo_entrada(),
                sinaisResponse,
                analise.getCor_prevista(),
                analise.getConfianca(),
                analise.getStatus_execucao()
        );
    }
}