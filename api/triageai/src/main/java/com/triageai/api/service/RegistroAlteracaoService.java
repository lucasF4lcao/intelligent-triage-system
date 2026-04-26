package com.triageai.api.service;

import com.triageai.api.dto.request.RegistrarAlteracaoRequest;
import com.triageai.api.dto.response.AlteracaoResponse;
import com.triageai.api.entity.AnaliseTriagem;
import com.triageai.api.entity.RegistroAlteracao;
import com.triageai.api.repository.AnaliseTriagemRepository;
import com.triageai.api.repository.RegistroAlteracaoRepository;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
public class RegistroAlteracaoService {

    private final RegistroAlteracaoRepository registroAlteracaoRepository;
    private final AnaliseTriagemRepository analiseTriagemRepository;

    public RegistroAlteracaoService(
            RegistroAlteracaoRepository registroAlteracaoRepository,
            AnaliseTriagemRepository analiseTriagemRepository
    ) {
        this.registroAlteracaoRepository = registroAlteracaoRepository;
        this.analiseTriagemRepository = analiseTriagemRepository;
    }

    public AlteracaoResponse registrarAlteracao(Long analiseId, RegistrarAlteracaoRequest request) {

        AnaliseTriagem analise = analiseTriagemRepository.findById(analiseId)
                .orElseThrow(() -> new RuntimeException("Análise não encontrada"));

        RegistroAlteracao alteracao = new RegistroAlteracao();
        alteracao.setAnaliseTriagem(analise);
        alteracao.setCor_prevista(analise.getCor_prevista());
        alteracao.setCor_final(request.corFinal());
        alteracao.setMotivo(request.motivo());
        alteracao.setData_alteracao(LocalDateTime.now());

        alteracao = registroAlteracaoRepository.save(alteracao);

        return mapToResponse(alteracao);
    }

    public List<AlteracaoResponse> listarAlteracoes(Long analiseId) {

        List<RegistroAlteracao> alteracoes = registroAlteracaoRepository.findByAnaliseTriagem_Id(analiseId);

        return alteracoes.stream()
                .map(this::mapToResponse)
                .toList();
    }

    private AlteracaoResponse mapToResponse(RegistroAlteracao alteracao) {
        return new AlteracaoResponse(
                alteracao.getId(),
                alteracao.getCor_prevista(),
                alteracao.getCor_final(),
                alteracao.getMotivo(),
                alteracao.getData_alteracao()
        );
    }
}