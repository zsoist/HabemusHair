"""
MOTOR DE ESTIMACION DE GRAFTS — El corazon clinico del sistema.

=====================================================================
PARA PRINCIPIANTES — LEE ESTO PRIMERO:
=====================================================================

Que es un "graft" (injerto)?
    Un graft es una unidad folicular (FU) que se extrae de la zona
    donante (atras de la cabeza) y se implanta en la zona receptora
    (donde falta pelo). Cada graft puede tener 1, 2, 3 o 4 pelos.

Que hace este motor?
    Calcula CUANTOS grafts necesita un paciente, basado en:
    1. El area de cada zona receptora (en cm2)
    2. La densidad objetivo (cuantos FU/cm2 queremos lograr)
    3. La densidad actual (cuanto pelo ya tiene)
    4. Factores de correccion (tipo de pelo, contraste, etc.)

Por que un RANGO y no un numero exacto?
    Porque la estimacion depende de muchas variables con incertidumbre.
    Dar un numero exacto ("necesitas 2,437 grafts") es clinicamente
    irresponsable. Damos un rango (2,000 - 2,800) con explicacion.

La formula base:
    Grafts por zona = Area_cm2 * (Densidad_objetivo - Densidad_actual) * Factores

    Ejemplo:
    - Zona frontal: 25 cm2
    - Densidad objetivo: 40 FU/cm2
    - Densidad actual: 15 FU/cm2
    - Factor calibre grueso: 0.85
    - Grafts = 25 * (40 - 15) * 0.85 = 531 grafts para esa zona

=====================================================================
"""

from dataclasses import dataclass, field


@dataclass
class ZoneInput:
    """
    Datos de entrada para UNA zona receptora.

    Ejemplo:
        zona_frontal = ZoneInput(
            zone_name="frontal",
            area_cm2=25.0,
            current_density_fu_cm2=15.0,
            target_density_fu_cm2=40.0,
            priority_weight=1.3,  # Zona frontal tiene mas prioridad estetica
        )
    """
    zone_name: str              # Nombre de la zona (frontal, midscalp, crown, etc.)
    area_cm2: float             # Area de la zona en cm2
    current_density_fu_cm2: float  # Densidad actual (FU/cm2) — puede ser 0 si esta calvo
    target_density_fu_cm2: float   # Densidad objetivo (FU/cm2)
    priority_weight: float = 1.0   # Peso de prioridad estetica (1.0 = normal)


@dataclass
class CorrectionFactors:
    """
    Factores de correccion que ajustan la estimacion.

    PARA PRINCIPIANTES:
    No todos los pelos son iguales. Un pelo grueso y rizado cubre
    mas area visual que un pelo fino y lacio. Estos factores ajustan
    la estimacion para reflejar esas diferencias.

    Todos los factores son multiplicadores:
    - < 1.0 = necesitas MENOS grafts (ej: pelo grueso)
    - = 1.0 = sin ajuste
    - > 1.0 = necesitas MAS grafts (ej: pelo fino)
    """
    # Calibre del pelo
    # Pelo grueso (>70um): 0.80-0.90 (necesitas menos para cubrir)
    # Pelo medio (50-70um): 0.95-1.05
    # Pelo fino (<50um): 1.10-1.20 (necesitas mas para cubrir)
    hair_caliber: float = 1.0

    # Textura del pelo
    # Rizado: 0.70-0.85 (cubre mucho mas area)
    # Ondulado: 0.85-0.95
    # Lacio: 1.0 (baseline)
    hair_texture: float = 1.0

    # Contraste piel-pelo
    # Poco contraste (rubio/piel clara, canoso): 0.80-0.90 (se nota menos la perdida)
    # Contraste medio: 0.95-1.05
    # Alto contraste (negro/piel clara): 1.10-1.20 (se nota mas)
    skin_hair_contrast: float = 1.0

    # Proporcion de grafts multi-pelo
    # Si la mayoria de FU son de 3-4 pelos: 0.85-0.95 (menos grafts necesarios)
    # Proporcion normal: 1.0
    # Mayoria de FU de 1 pelo: 1.05-1.15
    multi_hair_ratio: float = 1.0

    # Riesgo de progresion futura
    # Paciente joven (<30) con padre calvo: 1.10-1.20 (reservar donante)
    # Paciente estable >40: 0.95-1.00
    progression_risk: float = 1.0


@dataclass
class DonorAssessment:
    """
    Evaluacion de la zona donante.
    De aqui se extraen los grafts. Si no hay suficientes, hay que avisar.
    """
    donor_area_cm2: float           # Area de la zona donante segura
    donor_density_fu_cm2: float     # Densidad del donante en FU/cm2
    safe_extraction_rate: float = 0.30  # % maximo de extraccion segura (tipico: 25-35%)

    @property
    def total_available(self) -> int:
        """Grafts totales disponibles sin depletar el donante."""
        return int(self.donor_area_cm2 * self.donor_density_fu_cm2 * self.safe_extraction_rate)


@dataclass
class ZoneResult:
    """Resultado de estimacion para UNA zona."""
    zone_name: str
    area_cm2: float
    grafts_conservative: int
    grafts_recommended: int
    grafts_aggressive: int
    priority_weight: float
    explanation: str


@dataclass
class EstimationResult:
    """
    Resultado COMPLETO de la estimacion de grafts.

    COMO LEERLO:
    - min_grafts: escenario conservador, menos agresivo
    - recommended_low a recommended_high: el rango que recomendamos
    - aggressive_high: si el paciente quiere maxima densidad
    - Si donor_warning es True: NO HAY SUFICIENTE DONANTE
    """
    # Rangos totales
    min_grafts: int
    recommended_low: int
    recommended_high: int
    aggressive_high: int

    # Donor
    donor_available: int
    donor_warning: bool
    donor_warning_message: str

    # Desglose por zona
    zones: list[ZoneResult]

    # Metadata
    correction_factors_applied: dict
    technique_note: str


def estimate_grafts(
    zones: list[ZoneInput],
    corrections: CorrectionFactors,
    donor: DonorAssessment,
    technique: str = "FUE",
) -> EstimationResult:
    """
    Funcion principal: estima el rango de grafts necesarios.

    COMO FUNCIONA PASO A PASO:
    1. Para cada zona, calcula los grafts base:
       grafts = area * (densidad_objetivo - densidad_actual)
    2. Aplica los factores de correccion
    3. Genera 3 escenarios (conservador, recomendado, agresivo)
    4. Verifica si el donante alcanza
    5. Genera advertencias si es necesario

    PARAMETROS:
        zones: Lista de zonas receptoras con sus datos
        corrections: Factores de correccion del paciente
        donor: Datos de la zona donante
        technique: Tecnica quirurgica (FUE, FUT, DHI, Sapphire)

    RETORNA:
        EstimationResult con rangos y desglose por zona
    """

    # --- Factor compuesto de correccion ---
    # Multiplicamos todos los factores individuales
    combined_factor = (
        corrections.hair_caliber
        * corrections.hair_texture
        * corrections.skin_hair_contrast
        * corrections.multi_hair_ratio
        * corrections.progression_risk
    )

    # --- Calcular por zona ---
    zone_results: list[ZoneResult] = []
    total_conservative = 0
    total_recommended = 0
    total_aggressive = 0

    for zone in zones:
        # Diferencia de densidad (lo que falta para llegar al objetivo)
        density_gap = max(0, zone.target_density_fu_cm2 - zone.current_density_fu_cm2)

        # Grafts base para esta zona
        base_grafts = zone.area_cm2 * density_gap

        # Aplicar factores de correccion y prioridad
        adjusted_grafts = base_grafts * combined_factor * zone.priority_weight

        # 3 escenarios
        # Conservador: 80% del calculo (menos agresivo)
        conservative = int(adjusted_grafts * 0.80)
        # Recomendado: 100% del calculo
        recommended = int(adjusted_grafts * 1.00)
        # Agresivo: 125% del calculo (maxima densidad)
        aggressive = int(adjusted_grafts * 1.25)

        zone_results.append(ZoneResult(
            zone_name=zone.zone_name,
            area_cm2=zone.area_cm2,
            grafts_conservative=conservative,
            grafts_recommended=recommended,
            grafts_aggressive=aggressive,
            priority_weight=zone.priority_weight,
            explanation=(
                f"{zone.zone_name}: {zone.area_cm2:.1f}cm2, "
                f"densidad actual {zone.current_density_fu_cm2:.0f} FU/cm2, "
                f"objetivo {zone.target_density_fu_cm2:.0f} FU/cm2, "
                f"gap {density_gap:.0f} FU/cm2 -> "
                f"rango {conservative}-{aggressive} grafts"
            ),
        ))

        total_conservative += conservative
        total_recommended += recommended
        total_aggressive += aggressive

    # --- Verificar donante ---
    donor_available = donor.total_available
    donor_warning = total_recommended > donor_available
    donor_msg = ""

    if donor_warning:
        deficit = total_recommended - donor_available
        donor_msg = (
            f"ADVERTENCIA: La demanda recomendada ({total_recommended} grafts) "
            f"excede la oferta donante segura ({donor_available} grafts) "
            f"por {deficit} grafts. "
            f"Considere: reducir densidad objetivo, priorizar zonas, "
            f"o planear multiples sesiones."
        )

    # --- Nota sobre tecnica ---
    technique_notes = {
        "FUE": "FUE: 3,000-4,000+ grafts/sesion posibles. Cicatrices minimas.",
        "FUT": "FUT: Mayor cantidad por sesion pero cicatriz lineal.",
        "DHI": "DHI: Mas lenta (1,500-2,500 grafts/sesion), ideal para precision frontal.",
        "Sapphire": "FUE Sapphire: 3,000-4,000+ grafts/sesion, cuchillas mas finas.",
    }

    return EstimationResult(
        min_grafts=total_conservative,
        recommended_low=total_recommended,
        recommended_high=int(total_recommended * 1.15),  # +15% margen
        aggressive_high=total_aggressive,
        donor_available=donor_available,
        donor_warning=donor_warning,
        donor_warning_message=donor_msg,
        zones=zone_results,
        correction_factors_applied={
            "hair_caliber": corrections.hair_caliber,
            "hair_texture": corrections.hair_texture,
            "skin_hair_contrast": corrections.skin_hair_contrast,
            "multi_hair_ratio": corrections.multi_hair_ratio,
            "progression_risk": corrections.progression_risk,
            "combined_factor": round(combined_factor, 3),
        },
        technique_note=technique_notes.get(technique, f"Tecnica: {technique}"),
    )


# ============================================================
# EJEMPLO DE USO — Ejecuta este archivo directamente para ver
# ============================================================
if __name__ == "__main__":
    # Caso ejemplo: Hombre, 35 anos, Norwood 3, pelo grueso oscuro lacio

    # Definir zonas receptoras
    zonas = [
        ZoneInput(
            zone_name="frontal",
            area_cm2=25.0,
            current_density_fu_cm2=10.0,
            target_density_fu_cm2=40.0,
            priority_weight=1.3,  # Alta prioridad estetica
        ),
        ZoneInput(
            zone_name="midscalp",
            area_cm2=20.0,
            current_density_fu_cm2=25.0,
            target_density_fu_cm2=38.0,
            priority_weight=1.0,
        ),
        ZoneInput(
            zone_name="crown",
            area_cm2=15.0,
            current_density_fu_cm2=20.0,
            target_density_fu_cm2=35.0,
            priority_weight=0.8,  # Menor prioridad
        ),
    ]

    # Factores de correccion para este paciente
    factores = CorrectionFactors(
        hair_caliber=0.85,       # Pelo grueso -> necesita menos
        hair_texture=1.0,        # Lacio -> baseline
        skin_hair_contrast=1.1,  # Negro sobre piel clara -> se nota mas
        multi_hair_ratio=0.95,   # Buena proporcion de multi-hair
        progression_risk=1.1,    # Joven, reservar un poco mas
    )

    # Zona donante
    donante = DonorAssessment(
        donor_area_cm2=120.0,       # 120 cm2 de zona donante segura
        donor_density_fu_cm2=80.0,  # 80 FU/cm2 en el donante
        safe_extraction_rate=0.30,  # Extraer max 30%
    )

    # Ejecutar estimacion
    resultado = estimate_grafts(zonas, factores, donante, technique="FUE")

    # Mostrar resultado
    print("=" * 60)
    print("RESULTADO DE ESTIMACION DE GRAFTS")
    print("=" * 60)
    print(f"\n  Rango conservador:  {resultado.min_grafts} grafts")
    print(f"  Rango recomendado:  {resultado.recommended_low} - {resultado.recommended_high} grafts")
    print(f"  Rango agresivo:     {resultado.aggressive_high} grafts")
    print(f"\n  Donante disponible: {resultado.donor_available} grafts")
    print(f"  Advertencia:        {'SI' if resultado.donor_warning else 'No'}")

    if resultado.donor_warning:
        print(f"\n  {resultado.donor_warning_message}")

    print(f"\n  Tecnica: {resultado.technique_note}")
    print(f"\n  Factores aplicados: {resultado.correction_factors_applied}")

    print("\n--- Desglose por zona ---")
    for z in resultado.zones:
        print(f"  {z.explanation}")
