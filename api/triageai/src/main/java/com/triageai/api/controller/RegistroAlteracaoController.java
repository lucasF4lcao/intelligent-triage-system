package com.triageai.api.controller;

import com.triageai.api.dto.request.RegistrarAlteracaoRequest;
import com.triageai.api.dto.response.AlteracaoResponse;
import com.triageai.api.service.RegistroAlteracaoService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/analises/{analiseId}/alteracoes")
public class RegistroAlteracaoController {

    private final RegistroAlteracaoService registroAlteracaoService;

    public RegistroAlteracaoController(RegistroAlteracaoService registroAlteracaoService) {
        this.registroAlteracaoService = registroAlteracaoService;
    }

    @PostMapping
    public ResponseEntity<AlteracaoResponse> registrarAlteracao(
            @PathVariable Long analiseId,
            @RequestBody RegistrarAlteracaoRequest request
    ) {
        AlteracaoResponse response = registroAlteracaoService.registrarAlteracao(analiseId, request);
        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<List<AlteracaoResponse>> listarAlteracoes(@PathVariable Long analiseId) {
        List<AlteracaoResponse> response = registroAlteracaoService.listarAlteracoes(analiseId);
        return ResponseEntity.ok(response);
    }
}