# DATA_DICTIONARY — Diccionario de datos

## Para que sirve este documento

Define CADA dato que maneja el sistema: que es, de donde viene, en que unidades esta y por que importa. Si no entiendes un campo de la base de datos, buscalo aqui.

---

## Datos del paciente

| Campo | Tipo | Ejemplo | Que es | Por que importa |
|-------|------|---------|--------|-----------------|
| external_id | texto | "PAC-001" | Codigo del paciente en la clinica | Anonimizacion: no usamos nombre real |
| sex | enum | "male" | Sexo biologico | El patron de alopecia es diferente en hombres (Norwood) y mujeres (Ludwig) |
| age | entero | 35 | Edad al registro | Afecta la progresion esperada de la alopecia |
| fitzpatrick | entero 1-6 | 3 | Tipo de piel (escala Fitzpatrick) | Afecta el contraste pelo-piel, que impacta la percepcion visual de densidad |
| norwood_ludwig | texto | "NW3" | Grado de alopecia | Norwood 1-7 para hombres, Ludwig I-III para mujeres. Define la severidad |
| medications | texto | "Minoxidil 5%, Finasteride 1mg" | Medicamentos actuales | Algunos medicamentos estabilizan la perdida; es dato clinico relevante |

---

## Datos de imagen

| Campo | Tipo | Ejemplo | Que es | Por que importa |
|-------|------|---------|--------|-----------------|
| image_type | enum | "frontal" | Angulo de la foto | Cada angulo muestra zonas diferentes del cuero cabelludo |
| quality_score | float 0-1 | 0.85 | Score compuesto de calidad | Imagenes de baja calidad producen mediciones poco confiables |
| blur_score | float | 0.92 | Nitidez de la imagen (Laplacian) | Fotos borrosas no sirven para medir foliculos |
| exposure_score | float 0-1 | 0.65 | Calidad de la exposicion | Sub/sobre-exposicion distorsiona colores y contrastes |
| scale_present | bool | true | Se detecto marcador de escala | Sin escala, no podemos convertir pixeles a cm2 |

---

## Datos de segmentacion

| Campo | Tipo | Ejemplo | Que es | Por que importa |
|-------|------|---------|--------|-----------------|
| region_type | texto | "frontal" | Zona anatomica segmentada | Cada zona tiene diferente prioridad estetica y densidad objetivo |
| area_pixels | entero | 125000 | Area de la zona en pixeles | Dato crudo antes de calibracion |
| area_cm2 | float | 35.5 | Area en centimetros cuadrados | Dato calibrado, necesario para calcular grafts |
| confidence | float 0-1 | 0.89 | Confianza del modelo de IA | Si es baja, el medico debe revisar manualmente |
| qc_status | enum | "approved" | Estado de revision medica | El medico valida que la segmentacion sea correcta |

### Zonas anatomicas

| Zona | Codigo | Descripcion |
|------|--------|-------------|
| Frontal | frontal | Zona delantera, visible de frente |
| Forelock | forelock | Copete, area central frontal |
| Midscalp | midscalp | Zona media del cuero cabelludo |
| Corona | crown | Parte superior-trasera, la "coronilla" |
| Temporal izquierdo | temporal_left | Pico temporal izquierdo |
| Temporal derecho | temporal_right | Pico temporal derecho |
| Donante | donor | Zona occipital: de aqui se extraen los grafts |
| Zona no segura | unsafe | Areas del donante que no deben tocarse |
| Area de perdida | loss_area | Zonas con perdida visible de pelo |

---

## Datos de tricoscopia

| Campo | Tipo | Ejemplo | Que es | Por que importa |
|-------|------|---------|--------|-----------------|
| density_hairs_cm2 | float | 185.0 | Pelos individuales por cm2 | Medida directa de densidad capilar |
| density_fu_cm2 | float | 95.0 | Unidades foliculares por cm2 | Un FU puede tener 1-4 pelos. Mas relevante que pelos individuales para cirujia |
| avg_hair_diameter_um | float | 68.5 | Diametro promedio del pelo en micrometros | Pelo grueso (>70um) = mas cobertura visual por graft. Pelo fino (<50um) = menos |
| fu_1_hair_pct | float | 25.0 | % de FU con 1 pelo | Distribucion de FU. Mas grafts de 3-4 pelos = mejor resultado por graft |
| fu_2_hair_pct | float | 40.0 | % de FU con 2 pelos | |
| fu_3_hair_pct | float | 30.0 | % de FU con 3 pelos | |
| fu_4_hair_pct | float | 5.0 | % de FU con 4 pelos | |
| terminal_vellus_ratio | float | 4.5 | Ratio pelo terminal vs vellus | Terminal = pelo grueso normal. Vellus = pelo finito/miniaturizado. Ratio alto = sano |
| miniaturization_score | float 0-1 | 0.35 | Score de miniaturizacion | Mas alto = mas perdida. Indica progresion de alopecia androgenetica |
| calibration_factor | float | 12.5 | Factor pixels/mm | Derivado del marcador de escala. Sin esto, las medidas en cm2 no son confiables |

---

## Datos de estimacion de grafts

| Campo | Tipo | Ejemplo | Que es | Por que importa |
|-------|------|---------|--------|-----------------|
| min_grafts | entero | 1800 | Minimo razonable | Escenario conservador: menos agresivo, preserva mas donante |
| recommended_low | entero | 2200 | Inicio del rango recomendado | El "sweet spot" segun las formulas |
| recommended_high | entero | 2800 | Fin del rango recomendado | |
| aggressive_high | entero | 3500 | Maximo agresivo | Maxima densidad, usa mas donante. Mayor riesgo a largo plazo |
| donor_warning | bool | false | Alerta por donante insuficiente | Si la demanda supera lo disponible, el medico DEBE saberlo |
| doctor_override | bool | true | El medico cambio la estimacion | Datos de override son oro: nos dicen donde el modelo falla |
| doctor_final_grafts | entero | 2500 | Numero final decidido por medico | El "ground truth" para calibrar el motor |

### Factores de correccion

| Factor | Rango | Efecto | Ejemplo |
|--------|-------|--------|---------|
| Calibre del pelo | 0.7-1.3 | Pelo grueso necesita menos grafts | Pelo grueso: factor 0.85 (necesitas 15% menos) |
| Textura/rizo | 0.7-1.0 | Pelo rizado cubre mas area | Pelo muy rizado: factor 0.75 |
| Contraste piel-pelo | 0.8-1.2 | Poco contraste disimula la perdida | Pelo rubio en piel clara: factor 0.85 |
| Densidad remanente | 0.5-1.0 | Mas pelo existente = menos grafts necesarios | 50% cobertura existente: factor 0.6 |
| Prioridad estetica | 0.8-1.5 | Zona frontal tiene mas prioridad | Frontal: factor 1.3 |

---

## Unidades de medida

| Unidad | Abreviatura | Donde se usa |
|--------|-------------|-------------|
| Centimetros cuadrados | cm2 | Area de zonas anatomicas |
| Micrometros | um | Diametro del pelo |
| Foliculos/cm2 | FU/cm2 | Densidad de unidades foliculares |
| Pelos/cm2 | hairs/cm2 | Densidad de pelos individuales |
| Grafts | grafts | Unidades foliculares a trasplantar |
| Pixeles | px | Mediciones crudas de imagen |
| Pixeles/milimetro | px/mm | Factor de calibracion de escala |
