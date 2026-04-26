package com.triageai.api.repository;

import com.triageai.api.entity.SinaisVitais;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface SinaisVitaisRepository extends JpaRepository<SinaisVitais, Long> {

    Optional<SinaisVitais> findByAnaliseTriagem_Id(Long analiseId);

}