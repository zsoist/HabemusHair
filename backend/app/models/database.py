"""
Modelos de base de datos — El corazon de los datos del sistema.

QUE HACE ESTE ARCHIVO:
Define TODAS las tablas de la base de datos usando SQLAlchemy.
Cada clase aqui se convierte en una tabla en PostgreSQL.

PARA PRINCIPIANTES:
- Una "tabla" es como una hoja de Excel con columnas y filas.
- Cada clase (ej: Patient) es una tabla.
- Cada campo (ej: name) es una columna.
- Cada fila es un registro (ej: un paciente especifico).
- Las "relaciones" conectan tablas entre si (ej: un paciente tiene muchas fotos).

COMO SE USA:
    # Crear un paciente nuevo:
    paciente = Patient(external_id="PAC-001", sex="M", age=35)
    db.add(paciente)
    db.commit()

    # Buscar un paciente:
    paciente = db.query(Patient).filter(Patient.external_id == "PAC-001").first()
"""

import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text,
    ForeignKey, JSON, Enum as SQLEnum, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.sql import func
import enum


# --- Base para todos los modelos ---
class Base(DeclarativeBase):
    """Clase base. Todas las tablas heredan de aqui."""
    pass


# --- Enums (listas de opciones fijas) ---

class SexEnum(str, enum.Enum):
    """Sexo biologico — relevante para patron de alopecia."""
    MALE = "male"
    FEMALE = "female"

class ImageTypeEnum(str, enum.Enum):
    """
    Tipos de foto que capturamos.
    Cada angulo tiene un proposito especifico:
    - frontal: ver la linea del pelo de frente
    - lateral: ver la densidad lateral y temporal peaks
    - top/cenital: ver la corona y midscalp desde arriba
    - occipital: ver la zona donante (atras de la cabeza)
    - trichoscopy: foto microscopica para medir foliculos individuales
    """
    FRONTAL = "frontal"
    LATERAL_LEFT = "lateral_left"
    LATERAL_RIGHT = "lateral_right"
    TOP = "top"
    OCCIPITAL = "occipital"
    TRICHOSCOPY = "trichoscopy"

class QCStatusEnum(str, enum.Enum):
    """
    Estado de control de calidad de una segmentacion.
    - pending: recien generada, nadie la ha revisado
    - approved: el medico la reviso y esta correcta
    - rejected: el medico la reviso y la descarto
    - corrected: el medico la corrigio manualmente
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CORRECTED = "corrected"

class PlanningScenarioEnum(str, enum.Enum):
    """
    Escenarios de planificacion.
    - conservative: menos grafts, prioriza preservar donante
    - balanced: equilibrio entre cobertura y preservacion
    - dense: maxima cobertura posible, usa mas donante
    """
    CONSERVATIVE = "conservative"
    BALANCED = "balanced"
    DENSE = "dense"

class PlanningStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    REVIEWED = "reviewed"
    APPROVED = "approved"
    ARCHIVED = "archived"


# ============================================================
# TABLAS PRINCIPALES
# ============================================================

class Patient(Base):
    """
    TABLA: patients
    Representa un paciente. Un paciente puede tener muchas sesiones de captura,
    muchas sesiones de planificacion y muchos seguimientos.

    NOTA SOBRE PRIVACIDAD:
    - NO almacenamos nombre real aqui (Ley 1581).
    - external_id es un codigo que solo el medico puede vincular con la identidad.
    - Los datos sensibles estan anonimizados.
    """
    __tablename__ = "patients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_id = Column(String(100), unique=True, nullable=False,
                         comment="Codigo del paciente en la clinica (ej: PAC-001)")
    sex = Column(SQLEnum(SexEnum), nullable=False,
                 comment="Sexo biologico — afecta patron de alopecia")
    age = Column(Integer, nullable=False,
                 comment="Edad al momento del registro")
    fitzpatrick = Column(Integer, nullable=True,
                         comment="Escala Fitzpatrick (1-6): tipo de piel. Afecta contraste pelo-piel")
    norwood_ludwig = Column(String(10), nullable=True,
                            comment="Grado de alopecia: Norwood 1-7 (hombres) o Ludwig I-III (mujeres)")
    diagnosis_notes = Column(Text, nullable=True,
                             comment="Notas clinicas del medico")
    medications = Column(Text, nullable=True,
                         comment="Medicamentos actuales (Minoxidil, Finasteride, etc.)")
    consent_data_usage = Column(Boolean, default=False, nullable=False,
                                comment="Tiene consentimiento firmado para uso de datos en ML?")
    consent_date = Column(DateTime, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones — SQLAlchemy crea las conexiones automaticamente
    capture_sessions = relationship("CaptureSession", back_populates="patient")
    planning_sessions = relationship("PlanningSession", back_populates="patient")
    follow_ups = relationship("FollowUp", back_populates="patient")


class CaptureSession(Base):
    """
    TABLA: capture_sessions
    Cada vez que se toman fotos de un paciente es una "sesion de captura".
    Un paciente puede tener varias sesiones (consulta inicial, seguimiento a 6 meses, etc.)
    """
    __tablename__ = "capture_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    date = Column(DateTime, nullable=False, default=func.now(),
                  comment="Cuando se tomaron las fotos")
    device = Column(String(100), nullable=True,
                    comment="Dispositivo usado (ej: iPhone 15, Dino-Lite AM4113)")
    lighting_profile = Column(String(50), nullable=True,
                              comment="Tipo de iluminacion (natural, flash, ring_light)")
    operator = Column(String(100), nullable=True,
                      comment="Quien tomo las fotos (medico, asistente)")
    protocol_version = Column(String(20), default="1.0",
                              comment="Version del protocolo de captura usado")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    patient = relationship("Patient", back_populates="capture_sessions")
    images = relationship("Image", back_populates="capture_session")


class Image(Base):
    """
    TABLA: images
    Cada foto individual. Una sesion de captura tiene multiples fotos
    (frontal, laterales, cenital, occipital, tricoscopias).
    """
    __tablename__ = "images"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    capture_session_id = Column(UUID(as_uuid=True), ForeignKey("capture_sessions.id"), nullable=False)
    image_type = Column(SQLEnum(ImageTypeEnum), nullable=False,
                        comment="Tipo/angulo de la foto")
    filepath = Column(String(500), nullable=False,
                      comment="Ruta en el storage (ej: images/pac001/frontal_20260301.jpg)")
    original_filename = Column(String(255), nullable=True)
    width = Column(Integer, nullable=True, comment="Ancho en pixeles")
    height = Column(Integer, nullable=True, comment="Alto en pixeles")
    file_size_bytes = Column(Integer, nullable=True)

    # Control de calidad automatico
    scale_present = Column(Boolean, nullable=True,
                           comment="Se detecto marcador de escala en la foto?")
    quality_score = Column(Float, nullable=True,
                           comment="Score de calidad 0-1 (blur, exposicion, etc.)")
    blur_score = Column(Float, nullable=True,
                        comment="Score de blur (nitidez). Mas alto = mas nitido")
    exposure_score = Column(Float, nullable=True,
                            comment="Score de exposicion. 0.5 = ideal")

    metadata_json = Column(JSON, nullable=True,
                           comment="Metadata adicional en formato JSON")

    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    capture_session = relationship("CaptureSession", back_populates="images")
    segmentations = relationship("Segmentation", back_populates="image")
    trichoscopy_measurements = relationship("TrichoscopyMeasurement", back_populates="image")


class Segmentation(Base):
    """
    TABLA: segmentations
    Resultado de la segmentacion de una imagen por el modelo de IA.
    La "segmentacion" es dividir la imagen en zonas (frontal, corona, donante, etc.)
    y generar una "mascara" (imagen en blanco y negro) para cada zona.
    """
    __tablename__ = "segmentations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"), nullable=False)
    model_version = Column(String(50), nullable=False,
                           comment="Version del modelo que genero esta segmentacion (ej: unet_v1.2)")
    region_type = Column(String(50), nullable=False,
                         comment="Que zona segmento (frontal, midscalp, crown, donor, loss_area)")
    mask_path = Column(String(500), nullable=False,
                       comment="Ruta a la imagen de mascara")
    area_pixels = Column(Integer, nullable=True,
                         comment="Area de la zona en pixeles")
    area_cm2 = Column(Float, nullable=True,
                      comment="Area en cm2 (requiere calibracion con marcador de escala)")
    confidence = Column(Float, nullable=True,
                        comment="Confianza del modelo 0-1")
    qc_status = Column(SQLEnum(QCStatusEnum), default=QCStatusEnum.PENDING,
                       comment="Estado de revision del medico")
    qc_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    image = relationship("Image", back_populates="segmentations")


class TrichoscopyMeasurement(Base):
    """
    TABLA: trichoscopy_measurements
    Mediciones de una imagen de tricoscopia (foto microscopica).
    Esta tabla contiene los datos mas valiosos clinicamente:
    cuantos foliculos hay por cm2, que tan gruesos son, etc.
    """
    __tablename__ = "trichoscopy_measurements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    image_id = Column(UUID(as_uuid=True), ForeignKey("images.id"), nullable=False)
    model_version = Column(String(50), nullable=False)

    # Mediciones de densidad
    density_hairs_cm2 = Column(Float, nullable=True,
                               comment="Pelos individuales por cm2")
    density_fu_cm2 = Column(Float, nullable=True,
                            comment="Unidades foliculares por cm2 (un FU puede tener 1-4 pelos)")
    avg_hair_diameter_um = Column(Float, nullable=True,
                                  comment="Diametro promedio del pelo en micrometros")

    # Distribucion de unidades foliculares
    fu_1_hair_pct = Column(Float, nullable=True, comment="% de FU con 1 pelo")
    fu_2_hair_pct = Column(Float, nullable=True, comment="% de FU con 2 pelos")
    fu_3_hair_pct = Column(Float, nullable=True, comment="% de FU con 3 pelos")
    fu_4_hair_pct = Column(Float, nullable=True, comment="% de FU con 4 pelos")

    # Indicadores de salud capilar
    terminal_vellus_ratio = Column(Float, nullable=True,
                                   comment="Ratio pelo terminal (grueso) vs vellus (fino). Mas alto = mejor")
    miniaturization_score = Column(Float, nullable=True,
                                   comment="Score de miniaturizacion 0-1. Mas alto = mas perdida")

    calibration_factor = Column(Float, nullable=True,
                                comment="Factor de calibracion pixels/mm basado en marcador de escala")

    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    image = relationship("Image", back_populates="trichoscopy_measurements")


class PlanningSession(Base):
    """
    TABLA: planning_sessions
    Cada vez que el medico crea un plan de trasplante para un paciente.
    Un paciente puede tener varios planes (el medico puede probar escenarios).
    """
    __tablename__ = "planning_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    clinician_id = Column(String(100), nullable=True,
                          comment="ID del medico que creo el plan")
    status = Column(SQLEnum(PlanningStatusEnum), default=PlanningStatusEnum.DRAFT)
    scenario = Column(SQLEnum(PlanningScenarioEnum), default=PlanningScenarioEnum.BALANCED)
    technique = Column(String(50), nullable=True,
                       comment="Tecnica quirurgica planeada (FUE, FUT, DHI, Sapphire)")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relaciones
    patient = relationship("Patient", back_populates="planning_sessions")
    zones = relationship("PlanningZone", back_populates="planning_session")
    graft_estimation = relationship("GraftEstimation", back_populates="planning_session", uselist=False)
    reports = relationship("Report", back_populates="planning_session")


class PlanningZone(Base):
    """
    TABLA: planning_zones
    Cada zona receptora dentro de un plan. El medico define multiples zonas
    con diferentes prioridades y densidades objetivo.

    Ejemplo: Zona frontal con densidad objetivo 45 FU/cm2 (prioridad alta)
             Zona corona con densidad objetivo 35 FU/cm2 (prioridad media)
    """
    __tablename__ = "planning_zones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planning_session_id = Column(UUID(as_uuid=True), ForeignKey("planning_sessions.id"), nullable=False)
    zone_name = Column(String(50), nullable=False,
                       comment="Nombre de la zona (frontal, forelock, midscalp, crown, temporal_left, temporal_right)")
    target_density = Column(Float, nullable=False,
                            comment="Densidad objetivo en FU/cm2")
    current_coverage = Column(Float, nullable=True,
                              comment="Cobertura actual estimada 0-1 (0=calvo, 1=pelo lleno)")
    area_cm2 = Column(Float, nullable=True,
                      comment="Area de la zona en cm2")
    priority_weight = Column(Float, default=1.0,
                             comment="Peso de prioridad (1.0=normal, 2.0=alta prioridad)")

    # Relaciones
    planning_session = relationship("PlanningSession", back_populates="zones")


class GraftEstimation(Base):
    """
    TABLA: graft_estimations
    Resultado del motor de estimacion de grafts.
    Siempre devuelve un RANGO, no un numero unico.

    - min_grafts: el minimo razonable (resultado conservador)
    - recommended_low/high: el rango recomendado
    - aggressive_high: el maximo si el paciente quiere maxima densidad
    """
    __tablename__ = "graft_estimations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planning_session_id = Column(UUID(as_uuid=True), ForeignKey("planning_sessions.id"),
                                 nullable=False, unique=True)

    # Rangos de estimacion
    min_grafts = Column(Integer, nullable=False,
                        comment="Minimo razonable de grafts")
    recommended_low = Column(Integer, nullable=False,
                             comment="Limite inferior del rango recomendado")
    recommended_high = Column(Integer, nullable=False,
                              comment="Limite superior del rango recomendado")
    aggressive_high = Column(Integer, nullable=False,
                             comment="Maximo agresivo (maxima densidad)")

    # Zona donante
    donor_density_cm2 = Column(Float, nullable=True,
                               comment="Densidad de la zona donante en FU/cm2")
    donor_available_grafts = Column(Integer, nullable=True,
                                   comment="Grafts disponibles en zona donante")
    donor_warning = Column(Boolean, default=False,
                           comment="True si la demanda supera la oferta donante")
    donor_warning_message = Column(Text, nullable=True)

    # Explicabilidad
    explanation_json = Column(JSON, nullable=True,
                              comment="Desglose detallado: grafts por zona, factores de correccion, etc.")
    correction_factors_json = Column(JSON, nullable=True,
                                    comment="Factores aplicados: calibre, textura, contraste, etc.")

    # Override medico
    doctor_override = Column(Boolean, default=False,
                             comment="El medico modifico la estimacion manualmente?")
    doctor_final_grafts = Column(Integer, nullable=True,
                                 comment="Numero final de grafts decidido por el medico")
    doctor_override_reason = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    planning_session = relationship("PlanningSession", back_populates="graft_estimation")


class Report(Base):
    """
    TABLA: reports
    Reportes PDF generados para el paciente.
    """
    __tablename__ = "reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    planning_session_id = Column(UUID(as_uuid=True), ForeignKey("planning_sessions.id"), nullable=False)
    pdf_path = Column(String(500), nullable=False)
    disclaimer_version = Column(String(20), default="1.0",
                                comment="Version del texto de disclaimer usado")
    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    planning_session = relationship("PlanningSession", back_populates="reports")


class FollowUp(Base):
    """
    TABLA: follow_ups
    Seguimiento postoperatorio del paciente.
    Esta es la tabla que cierra el loop de aprendizaje:
    si sabemos cuantos grafts se hicieron Y como quedo,
    podemos mejorar las estimaciones futuras.
    """
    __tablename__ = "follow_ups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), ForeignKey("patients.id"), nullable=False)
    months_post_op = Column(Integer, nullable=False,
                            comment="Meses despues de la cirugia (6, 12, 18)")
    actual_grafts_placed = Column(Integer, nullable=True,
                                  comment="Grafts realmente colocados en cirugia")
    satisfaction_score = Column(Integer, nullable=True,
                                comment="Satisfaccion del paciente 1-10")
    density_improvement_pct = Column(Float, nullable=True,
                                     comment="Mejora de densidad medida vs pre-op")
    capture_session_id = Column(UUID(as_uuid=True), ForeignKey("capture_sessions.id"), nullable=True,
                                comment="Sesion de captura del seguimiento (fotos post-op)")
    clinician_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    # Relaciones
    patient = relationship("Patient", back_populates="follow_ups")


class AuditLog(Base):
    """
    TABLA: audit_log
    Registro inmutable de TODA accion clinica.
    Quien hizo que, cuando, sobre que paciente.

    IMPORTANTE PARA:
    - Cumplimiento legal (Ley 1581)
    - Trazabilidad clinica
    - Debugging
    - Gobernanza de ML (que modelo produjo que resultado)
    """
    __tablename__ = "audit_log"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    user_id = Column(String(100), nullable=False, comment="Quien hizo la accion")
    action = Column(String(100), nullable=False,
                    comment="Tipo de accion (view_patient, create_plan, override_estimation, etc.)")
    entity_type = Column(String(50), nullable=True,
                         comment="Tipo de entidad afectada (patient, planning_session, etc.)")
    entity_id = Column(String(100), nullable=True,
                       comment="ID de la entidad afectada")
    details_json = Column(JSON, nullable=True,
                          comment="Detalles adicionales de la accion")
    ip_address = Column(String(45), nullable=True)

    # Index para busquedas rapidas
    __table_args__ = (
        Index("ix_audit_log_user_timestamp", "user_id", "timestamp"),
        Index("ix_audit_log_entity", "entity_type", "entity_id"),
    )


class ModelRegistry(Base):
    """
    TABLA: model_registry
    Registro de todos los modelos de ML usados en el sistema.
    Sin esto, no puedes saber que version del modelo produjo
    cada segmentacion o medicion. Critico para reproducibilidad.
    """
    __tablename__ = "model_registry"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False,
                        comment="Nombre del modelo (ej: scalp_segmentation_unet)")
    version = Column(String(50), nullable=False,
                     comment="Version (ej: v1.2.0)")
    model_type = Column(String(50), nullable=False,
                        comment="Tipo: segmentation, detection, density_estimation")
    weights_path = Column(String(500), nullable=False,
                          comment="Ruta a los pesos del modelo")
    training_dataset = Column(String(200), nullable=True,
                              comment="Nombre/version del dataset de entrenamiento")
    metrics_json = Column(JSON, nullable=True,
                          comment="Metricas de evaluacion (IoU, MAE, etc.)")
    is_active = Column(Boolean, default=False,
                       comment="Es el modelo activo en produccion?")
    notes = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    deployed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_model_registry_active", "model_name", "is_active"),
    )
