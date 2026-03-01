# RISK_REGISTER — Registro de riesgos del proyecto

## Riesgos activos

| # | Riesgo | Probabilidad | Impacto | Severidad | Mitigacion | Estado |
|---|--------|-------------|---------|-----------|------------|--------|
| R1 | Dataset insuficiente para entrenar modelos | Media | Alto | **Alto** | Alianza con medico partner + scraping Reddit | Mitigado parcialmente |
| R2 | Sesgo por tipo de pelo (modelos entrenados con pelo caucasico) | Alta | Alto | **Alto** | Entrenar con datos colombianos desde dia 1. Evaluar metricas por subgrupo | Pendiente |
| R3 | Simulacion genera expectativas irreales en pacientes | Media | Alto | **Alto** | Disclaimers en UX, no solo texto. Simulacion al final, no al principio | Por disenar |
| R4 | Incumplimiento Ley 1581 (datos personales) | Baja | Muy Alto | **Alto** | Consentimiento explicito, anonimizacion, hosting local | En proceso |
| R5 | Scope creep (intentar hacer todo a la vez) | Alta | Medio | **Medio** | MVP estricto: solo motores 1-2 + reporte. Canvas y simulacion son V2 | Activo |
| R6 | Error en formulas de estimacion de grafts | Media | Alto | **Alto** | Validacion con medico contra 20-30 casos historicos antes de usar en consulta | Pendiente |
| R7 | Calibracion geometrica (pixeles a cm2 en superficie curva) | Media | Medio | **Medio** | Modelo elipsoidal simplificado + marcador de escala como fallback | Pendiente |
| R8 | El medico partner pierde interes | Baja | Muy Alto | **Alto** | Mostrar avances cada 2-3 semanas. MVP usable en semana 12 | Activo |
| R9 | Regulacion INVIMA aplica al software | Baja | Alto | **Medio** | No hacer claims diagnosticos. Lanzar como herramienta de apoyo | Mitigado |
| R10 | Dependencia de un solo desarrollador | Alta | Medio | **Medio** | Documentacion exhaustiva, codigo bien comentado, tests | Activo |

## Criterios de evaluacion

- **Probabilidad:** Baja (<25%), Media (25-50%), Alta (>50%)
- **Impacto:** Bajo (retraso menor), Medio (retraso significativo), Alto (bloquea el proyecto), Muy Alto (mata el proyecto)
- **Severidad:** Probabilidad x Impacto

## Revision

Este registro se revisa cada 2 semanas durante el sprint planning.
