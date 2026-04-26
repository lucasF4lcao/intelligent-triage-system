package com.triageai.api.entity;

import jakarta.persistence.*;
import lombok.*;

import java.math.BigDecimal;

@Table(name = "sinais_vitais")
@Entity(name = "SinaisVitais")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(of = "id")
public class SinaisVitais {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne(optional = false)
    @JoinColumn(name = "analise_triagem_id")
    private AnaliseTriagem analiseTriagem;
    private Integer idade;
    private Integer frequencia_cardiaca;
    private Integer pressao_sistolica;
    private Integer pressao_diastolica;
    private Integer saturacao_o2;
    private BigDecimal temperatura;
    private Integer frequencia_respiratoria;
    private Integer dor;

}
