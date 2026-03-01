# CAPTURE_PROTOCOL — Protocolo de captura de imagenes

## Por que importa

Sin fotos consistentes, todo el sistema falla. Si un dia tomas la foto con luz natural y otro dia con flash, el modelo de IA ve cosas diferentes y sus mediciones no son comparables. Este protocolo existe para que TODAS las fotos sean consistentes.

## Angulos requeridos (minimos)

| # | Angulo | Que muestra | Obligatorio |
|---|--------|-------------|-------------|
| 1 | **Frontal** | Linea del pelo, frente, zona temporal | SI |
| 2 | **Lateral izquierdo** | Temporal izquierdo, patron lateral | SI |
| 3 | **Lateral derecho** | Temporal derecho, patron lateral | SI |
| 4 | **Cenital (top)** | Corona, midscalp desde arriba | SI |
| 5 | **Occipital** | Zona donante (atras de la cabeza) | SI |
| 6-10 | **Tricoscopia x3-5** | Foliculos individuales en zonas clave | SI (si hay dermatoscopio) |

## Condiciones de captura

### Iluminacion
- **Ideal:** Ring light o luz difusa uniforme
- **Aceptable:** Luz natural indirecta (ventana, no sol directo)
- **Inaceptable:** Flash directo, contraluz, sombras duras

### Distancia
- **Fotos macro:** 40-60 cm del sujeto, consistente entre tomas
- **Tricoscopia:** Segun el dispositivo (contacto directo o distancia fija)

### Fondo
- **Ideal:** Fondo neutro (blanco, gris claro)
- **Aceptable:** Cualquier fondo sin distracciones
- **Inaceptable:** Fondos complejos que confundan al modelo

### Marcador de escala
- **Para fotos macro:** Una regla o referencia de tamano conocido visible en la foto
- **Para tricoscopia:** El dermatoscopio ya tiene escala integrada (verificar calibracion)

## Flujo de captura en el software

```
1. Seleccionar paciente
2. Iniciar nueva sesion de captura
3. El sistema pide cada angulo en orden:
   [Frontal] -> [Lateral izq] -> [Lateral der] -> [Cenital] -> [Occipital]
4. Para cada foto:
   a. Mostrar guia visual del angulo esperado
   b. Capturar/subir foto
   c. Validacion automatica (blur, exposicion, resolucion)
   d. Si no pasa: advertencia + opcion de retomar
5. Si hay dermatoscopio: capturar tricoscopias en puntos definidos
6. Revision final de todas las imagenes
7. Confirmar sesion
```

## Validaciones automaticas

| Check | Criterio | Accion si falla |
|-------|----------|-----------------|
| Blur | Laplacian variance > umbral | Advertencia: "Foto borrosa, retome" |
| Exposicion | Histograma dentro de rango | Advertencia: "Muy oscura/clara" |
| Resolucion | Minimo 640x480 px | Rechazo: "Resolucion insuficiente" |
| Formato | JPEG o PNG | Rechazo: "Formato no soportado" |
| Tamano | Max 20MB | Rechazo: "Archivo muy grande" |
| Escala | Deteccion de marcador (futuro) | Advertencia: "No se detecto marcador" |

## Puntos de tricoscopia estandar

Si el medico tiene dermatoscopio, tomar tricoscopia en estos puntos:

1. **Frontal** — 2 cm detras de la linea del pelo actual
2. **Midscalp** — Punto medio entre frente y corona
3. **Crown** — Centro de la corona
4. **Temporal** — 1 punto por lado
5. **Donante** — Zona occipital central
