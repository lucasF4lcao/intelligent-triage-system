package com.triageai.api.repository;

import com.triageai.api.entity.RegistroAlteracao;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface RegistroAlteracaoRepository extends JpaRepository<RegistroAlteracao, Long> {
    List<RegistroAlteracao> findByAnaliseTriagem_Id(Long analiseId);
}