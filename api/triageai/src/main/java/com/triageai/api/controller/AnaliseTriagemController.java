package com.triageai.api.controller;

import com.triageai.api.dto.request.CriarAnaliseRequest;
import com.triageai.api.dto.response.AnaliseTriagemResponse;
import com.triageai.api.service.AnaliseOrchestratorService;
import com.triageai.api.service.AnaliseTriagemService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/analises")
public class AnaliseTriagemController {

    private final AnaliseTriagemService analiseTriagemService;
    private final AnaliseOrchestratorService orchestratorService;

    public AnaliseTriagemController(AnaliseTriagemService analiseTriagemService, AnaliseOrchestratorService orchestratorService) {
        this.analiseTriagemService = analiseTriagemService;
        this.orchestratorService = orchestratorService;
    }

    @PostMapping
    public ResponseEntity<AnaliseTriagemResponse> criarAnalise(@RequestBody CriarAnaliseRequest request) {
        return ResponseEntity.ok(analiseTriagemService.criarAnalise(request));
    }

    @PostMapping("/fhir")
    public ResponseEntity<AnaliseTriagemResponse> criarAnaliseFhir(@RequestBody String bundleJson) {
        return ResponseEntity.ok(orchestratorService.processarFhir(bundleJson));
    }

    @GetMapping("/{id}")
    public ResponseEntity<AnaliseTriagemResponse> buscarPorId(@PathVariable Long id) {
        return ResponseEntity.ok(analiseTriagemService.buscarPorId(id));
    }

    @GetMapping
    public ResponseEntity<List<AnaliseTriagemResponse>> listarAnalises() {
        return ResponseEntity.ok(analiseTriagemService.listarAnalises());
    }
}