package com.triageai.api.service;

import com.triageai.api.dto.request.CriarAnaliseRequest;
import com.triageai.api.dto.response.AnaliseTriagemResponse;
import com.triageai.api.dto.response.SinaisVitaisResponse;
import com.triageai.api.entity.AnaliseTriagem;
import com.triageai.api.entity.SinaisVitais;
import com.triageai.api.enums.StatusExecucao;
import com.triageai.api.enums.TipoEntrada;
import com.triageai.api.repository.AnaliseTriagemRepository;
import com.triageai.api.repository.SinaisVitaisRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class AnaliseTriagemService {

    private final AnaliseTriagemRepository analiseTriagemRepository;
    private final SinaisVitaisRepository sinaisVitaisRepository;

    public AnaliseTriagemService(
            AnaliseTriagemRepository analiseTriagemRepository,
            SinaisVitaisRepository sinaisVitaisRepository
    ) {
        this.analiseTriagemRepository = analiseTriagemRepository;
        this.sinaisVitaisRepository = sinaisVitaisRepository;
    }

    public AnaliseTriagemResponse criarAnalise(CriarAnaliseRequest request) {

        AnaliseTriagem analise = new AnaliseTriagem();
        analise.setData_criacao(LocalDateTime.now());
        analise.setTipo_entrada(request.tipoEntrada());
        analise.setStatus_execucao(StatusExecucao.SUCESSO);

        if (request.tipoEntrada() == TipoEntrada.TEXTO) {
            analise.setTexto_original(request.textoOriginal());
        } else {
            analise.setTexto_original(null);
        }

        analise = analiseTriagemRepository.save(analise);

        SinaisVitais sinaisVitais = new SinaisVitais();
        sinaisVitais.setAnaliseTriagem(analise);

        if (request.tipoEntrada() == TipoEntrada.MANUAL && request.dadosManuais() != null) {
            sinaisVitais.setIdade(request.dadosManuais().idade());
            sinaisVitais.setFrequencia_cardiaca(request.dadosManuais().frequenciaCardiaca());
            sinaisVitais.setPressao_sistolica(request.dadosManuais().pressaoSistolica());
            sinaisVitais.setPressao_diastolica(request.dadosManuais().pressaoDiastolica());
            sinaisVitais.setSaturacao_o2(request.dadosManuais().saturacaoO2());
            sinaisVitais.setTemperatura(request.dadosManuais().temperatura());
            sinaisVitais.setFrequencia_respiratoria(request.dadosManuais().frequenciaRespiratoria());
            sinaisVitais.setDor(request.dadosManuais().dor());
        }

        sinaisVitaisRepository.save(sinaisVitais);

        return mapToResponse(analise, sinaisVitais);
    }

    public AnaliseTriagemResponse buscarPorId(Long id) {
        AnaliseTriagem analise = analiseTriagemRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Análise não encontrada"));

        SinaisVitais sinaisVitais = sinaisVitaisRepository.findByAnaliseTriagem_Id(analise.getId())
                .orElse(null);

        return mapToResponse(analise, sinaisVitais);
    }

    public List<AnaliseTriagemResponse> listarAnalises() {
        return analiseTriagemRepository.findAll().stream()
                .map(analise -> {
                    SinaisVitais sinaisVitais = sinaisVitaisRepository
                            .findByAnaliseTriagem_Id(analise.getId())
                            .orElse(null);

                    return mapToResponse(analise, sinaisVitais);
                })
                .toList();
    }

    private AnaliseTriagemResponse mapToResponse(AnaliseTriagem analise, SinaisVitais sinaisVitais) {

        SinaisVitaisResponse sinaisResponse = null;

        if (sinaisVitais != null) {
            sinaisResponse = new SinaisVitaisResponse(
                    sinaisVitais.getIdade(),
                    sinaisVitais.getFrequencia_cardiaca(),
                    sinaisVitais.getPressao_sistolica(),
                    sinaisVitais.getPressao_diastolica(),
                    sinaisVitais.getSaturacao_o2(),
                    sinaisVitais.getTemperatura(),
                    sinaisVitais.getFrequencia_respiratoria(),
                    sinaisVitais.getDor()
            );
        }

        return new AnaliseTriagemResponse(
                analise.getId(),
                analise.getData_criacao(),
                analise.getTipo_entrada(),
                analise.getTexto_original(),
                sinaisResponse,
                analise.getCor_prevista(),
                analise.getConfianca(),
                analise.getStatus_execucao()
        );
    }
}