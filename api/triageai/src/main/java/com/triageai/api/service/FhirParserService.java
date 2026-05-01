package com.triageai.api.service;

import ca.uhn.fhir.context.FhirContext;
import ca.uhn.fhir.parser.IParser;
import com.triageai.api.entity.SinaisVitais;
import org.hl7.fhir.r4.model.*;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.Period;
import java.time.ZoneId;

@Service
public class FhirParserService {

    private final FhirContext ctx;
    private final IParser parser;

    public FhirParserService() {
        this.ctx = FhirContext.forR4();
        this.parser = ctx.newJsonParser();
    }

    public SinaisVitais extrairSinaisVitais(String bundleJson) {

        SinaisVitais sinais = new SinaisVitais();

        Bundle bundle = parser.parseResource(Bundle.class, bundleJson);

        if (bundle == null || bundle.getEntry() == null) {
            return sinais;
        }

        for (Bundle.BundleEntryComponent entry : bundle.getEntry()) {

            Resource resource = entry.getResource();
            if (resource == null) continue;

            if (resource instanceof Patient patient) {
                preencherIdade(patient, sinais);
            }

            if (resource instanceof Observation obs) {
                preencherObservacao(obs, sinais);
            }
        }

        return sinais;
    }

    private void preencherIdade(Patient patient, SinaisVitais sinais) {

        if (!patient.hasBirthDate()) return;

        LocalDate birthDate = patient.getBirthDate()
                .toInstant()
                .atZone(ZoneId.systemDefault())
                .toLocalDate();

        int idade = Period.between(birthDate, LocalDate.now()).getYears();

        sinais.setIdade(idade);
    }

    private void preencherObservacao(Observation obs, SinaisVitais sinais) {

        if (!obs.hasCode() || !obs.getCode().hasCoding()) return;

        for (Coding coding : obs.getCode().getCoding()) {

            String code = coding.getCode();

            if (code == null) continue;

            // frequência cardíaca
            if ("8867-4".equals(code) && obs.hasValueQuantity()) {
                sinais.setFrequencia_cardiaca(
                        obs.getValueQuantity().getValue().intValue()
                );
            }

            // saturação O2
            if ("59408-5".equals(code) && obs.hasValueQuantity()) {
                sinais.setSaturacao_o2(
                        obs.getValueQuantity().getValue().intValue()
                );
            }

            // temperatura
            if ("8310-5".equals(code) && obs.hasValueQuantity()) {
                sinais.setTemperatura(
                        obs.getValueQuantity().getValue()
                );
            }

            // frequência respiratória
            if ("9279-1".equals(code) && obs.hasValueQuantity()) {
                sinais.setFrequencia_respiratoria(
                        obs.getValueQuantity().getValue().intValue()
                );
            }

            // pressão arterial
            if ("85354-9".equals(code)) {
                preencherPressao(obs, sinais);
            }
        }
    }

    private void preencherPressao(Observation obs, SinaisVitais sinais) {

        if (!obs.hasComponent()) return;

        for (Observation.ObservationComponentComponent comp : obs.getComponent()) {

            if (!comp.hasCode() || !comp.getCode().hasCoding()) continue;
            if (!comp.hasValueQuantity()) continue;

            for (Coding coding : comp.getCode().getCoding()) {

                String code = coding.getCode();

                if (code == null) continue;

                // sistólica
                if ("8480-6".equals(code)) {
                    sinais.setPressao_sistolica(
                            comp.getValueQuantity().getValue().intValue()
                    );
                }

                // diastólica
                if ("8462-4".equals(code)) {
                    sinais.setPressao_diastolica(
                            comp.getValueQuantity().getValue().intValue()
                    );
                }
            }
        }
    }
}