package com.triageai.api.entity;

import com.triageai.api.enums.CorManchester;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Table(name = "registro_alteracao")
@Entity(name = "RegistroAlteracao")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@EqualsAndHashCode(of = "id")
public class RegistroAlteracao {
    @Id @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne(optional = false)
    @JoinColumn(name = "analise_triagem_id")
    private AnaliseTriagem analiseTriagem;
    @Enumerated(EnumType.STRING)
    private CorManchester cor_prevista;
    @Enumerated(EnumType.STRING)
    private CorManchester cor_final;
    private String motivo;
    private LocalDateTime data_alteracao;

}
