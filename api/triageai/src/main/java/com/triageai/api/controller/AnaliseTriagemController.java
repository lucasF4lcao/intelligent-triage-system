package com.triageai.api.controller;

import com.triageai.api.dto.response.AnaliseTriagemResponse;
import com.triageai.api.service.AnaliseOrchestratorService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/analises")
public class AnaliseTriagemController {

    private final AnaliseOrchestratorService orchestratorService;

    public AnaliseTriagemController(AnaliseOrchestratorService orchestratorService) {
        this.orchestratorService = orchestratorService;
    }

    @PostMapping("/fhir")
    public ResponseEntity<AnaliseTriagemResponse> criarAnaliseFhir(@RequestBody String bundleJson) {
        return ResponseEntity.ok(orchestratorService.processarFhir(bundleJson));
    }

}