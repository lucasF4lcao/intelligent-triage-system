package com.triageai.api.controller;

import com.triageai.api.dto.request.CriarAnaliseRequest;
import com.triageai.api.dto.response.AnaliseTriagemResponse;
import com.triageai.api.service.AnaliseTriagemService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/analises")
public class AnaliseTriagemController {

    private final AnaliseTriagemService analiseTriagemService;

    public AnaliseTriagemController(AnaliseTriagemService analiseTriagemService) {
        this.analiseTriagemService = analiseTriagemService;
    }

    @PostMapping
    public ResponseEntity<AnaliseTriagemResponse> criarAnalise(
            @RequestBody CriarAnaliseRequest request
    ) {
        AnaliseTriagemResponse response = analiseTriagemService.criarAnalise(request);
        return ResponseEntity.ok(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<AnaliseTriagemResponse> buscarPorId(@PathVariable Long id) {
        AnaliseTriagemResponse response = analiseTriagemService.buscarPorId(id);
        return ResponseEntity.ok(response);
    }

    @GetMapping
    public ResponseEntity<List<AnaliseTriagemResponse>> listarAnalises() {
        List<AnaliseTriagemResponse> response = analiseTriagemService.listarAnalises();
        return ResponseEntity.ok(response);
    }
}