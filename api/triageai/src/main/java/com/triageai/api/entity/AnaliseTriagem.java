package com.triageai.api.entity;

import com.triageai.api.enums.CorManchester;
import com.triageai.api.enums.StatusExecucao;
import com.triageai.api.enums.TipoEntrada;
import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Table(name = "analise_triagem")
@Entity(name = "AnaliseTriagem")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(of = "id")
public class AnaliseTriagem {

    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private LocalDateTime data_criacao;
    private String texto_original;

    @Enumerated(EnumType.STRING)
    private TipoEntrada tipo_entrada;

    @Enumerated(EnumType.STRING)
    private CorManchester cor_prevista;

    private BigDecimal confianca;

    @Enumerated(EnumType.STRING)
    private StatusExecucao status_execucao;
}
