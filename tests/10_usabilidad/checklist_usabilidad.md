# Evaluación de Usabilidad — FermentAI
## Heurísticas de Nielsen (10 principios)

**Fecha:** ________________  
**Evaluador:** ________________  
**Versión:** 1.0.0  
**URL:** http://localhost:3000  

### Escala de severidad
| Puntuación | Descripción |
|-----------|-------------|
| **0** | No es un problema de usabilidad |
| **1** | Problema cosmético — corregir si hay tiempo |
| **2** | Problema menor — baja prioridad |
| **3** | Problema mayor — alta prioridad |
| **4** | Problema catastrófico — debe corregirse antes del lanzamiento |

---

## Heurística 1 — Visibilidad del estado del sistema
*El sistema debe informar siempre al usuario sobre lo que está ocurriendo.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 1.1 | Indicador de carga visible durante subida de ZIP | Subir Aporte | | |
| 1.2 | Estado del aporte visible (pendiente/aprobado/rechazado) en Mis Aportes | Mis Aportes | | |
| 1.3 | Notificación badge visible cuando hay notificaciones nuevas | Header/Nav | | |
| 1.4 | Confirmación visual tras subida exitosa | Subir Aporte | | |
| 1.5 | Indicador de sesión activa (nombre de usuario visible) | Header | | |
| 1.6 | Progreso de la subida indicado al usuario | Subir Aporte | | |

**Observaciones heurística 1:**
_______________________________________________

---

## Heurística 2 — Relación entre el sistema y el mundo real
*El sistema debe hablar el idioma del usuario.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 2.1 | Términos científicos (HPLC, glucosa, acidos) usados correctamente | Datasets | | |
| 2.2 | Estados de fermentación comprensibles ("semi fermentado", "fermentado") | Datasets | | |
| 2.3 | Mensajes de error en español claro, sin tecnicismos | Global | | |
| 2.4 | Botones usan verbos de acción (Subir, Aprobar, Rechazar) | Global | | |
| 2.5 | Fechas en formato dd/mm/aaaa o equivalente local | Global | | |

**Observaciones heurística 2:**
_______________________________________________

---

## Heurística 3 — Control y libertad del usuario
*El usuario debe poder salir de estados no deseados.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 3.1 | Botón de cancelación al subir un archivo | Subir Aporte | | |
| 3.2 | Posibilidad de limpiar filtros de búsqueda | Datasets | | |
| 3.3 | Botón "Cerrar sesión" fácilmente accesible | Header/Nav | | |
| 3.4 | Navegación hacia atrás funcional con botón del navegador | Global | | |
| 3.5 | Diálogo de confirmación antes de acciones destructivas | Revisión | | |

**Observaciones heurística 3:**
_______________________________________________

---

## Heurística 4 — Consistencia y estándares
*Los usuarios no deben preguntarse si acciones diferentes significan lo mismo.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 4.1 | Paleta de colores coherente en toda la aplicación | Global | | |
| 4.2 | Tipografía consistente (fuente, tamaños, pesos) | Global | | |
| 4.3 | Iconos consistentes con su función en toda la app | Global | | |
| 4.4 | Posición del botón principal (p.ej. siempre a la derecha) | Formularios | | |
| 4.5 | Comportamiento de los formularios consistente | Login/Registro | | |
| 4.6 | Mensajes de error con el mismo formato en toda la app | Global | | |

**Observaciones heurística 4:**
_______________________________________________

---

## Heurística 5 — Prevención de errores
*El sistema debe diseñarse para evitar que los errores ocurran.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 5.1 | Validación en tiempo real del formulario de login | Login | | |
| 5.2 | Restricción de tipo de archivo en campo de subida (solo .zip) | Subir Aporte | | |
| 5.3 | Instrucciones claras del formato ZIP requerido antes de subir | Subir Aporte | | |
| 5.4 | Confirmación antes de aprobar/rechazar un aporte | Revisión | | |
| 5.5 | Límite de caracteres visible en campo de observaciones | Revisión | | |

**Observaciones heurística 5:**
_______________________________________________

---

## Heurística 6 — Reconocimiento en lugar de recuerdo
*Minimizar la carga de memoria del usuario.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 6.1 | Menú de navegación siempre visible (no oculto) | Global | | |
| 6.2 | La página activa está resaltada en la navegación | Global | | |
| 6.3 | Breadcrumb o indicador de ubicación actual | Dashboard | | |
| 6.4 | Descripciones en los filtros sobre los valores válidos | Datasets | | |
| 6.5 | Ejemplo de código FERM## mostrado como placeholder | Filtros | | |

**Observaciones heurística 6:**
_______________________________________________

---

## Heurística 7 — Flexibilidad y eficiencia de uso
*Atajos para usuarios expertos sin dificultar a novatos.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 7.1 | Tecla Enter funciona para enviar formularios | Login/Registro | | |
| 7.2 | Tecla Enter en campo de búsqueda ejecuta el filtro | Datasets | | |
| 7.3 | Filtros se aplican rápidamente (< 2s) | Datasets | | |
| 7.4 | Drag & drop para subir archivos ZIP | Subir Aporte | | |

**Observaciones heurística 7:**
_______________________________________________

---

## Heurística 8 — Diseño estético y minimalista
*Los diálogos no deben contener información irrelevante.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 8.1 | Diseño limpio sin elementos decorativos innecesarios | Global | | |
| 8.2 | Jerarquía visual clara (títulos, subtítulos, contenido) | Global | | |
| 8.3 | Espaciado adecuado entre elementos | Global | | |
| 8.4 | Cards de datasets con información justa, sin exceso | Datasets | | |
| 8.5 | Sin textos de error innecesariamente técnicos | Global | | |

**Observaciones heurística 8:**
_______________________________________________

---

## Heurística 9 — Ayuda para reconocer, diagnosticar y recuperarse de errores
*Los mensajes de error deben ser claros y sugerir solución.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 9.1 | Mensaje de error de login es específico y orientador | Login | | |
| 9.2 | Error de validación ZIP indica exactamente qué falta | Subir Aporte | | |
| 9.3 | Error de columnas CSV muestra cuáles faltan | Subir Aporte | | |
| 9.4 | Página 404 con enlace de retorno al dashboard | Global | | |
| 9.5 | Error de red con opción de reintentar | Global | | |

**Observaciones heurística 9:**
_______________________________________________

---

## Heurística 10 — Ayuda y documentación
*Aunque sería mejor si no se necesita, la ayuda debe estar disponible.*

| # | Criterio evaluado | Pantalla | Severidad (0-4) | Hallazgo |
|---|-------------------|----------|-----------------|----------|
| 10.1 | Instrucciones del formato ZIP visibles antes de subir | Subir Aporte | | |
| 10.2 | Tooltips o textos de ayuda en campos complejos | Formularios | | |
| 10.3 | Descripción de los roles (colaborador vs investigador) visible | Registro | | |
| 10.4 | Información sobre los 18 campos HPLC accesible | Datasets | | |
| 10.5 | Link a documentación o manual de usuario | Global | | |

**Observaciones heurística 10:**
_______________________________________________

---

## Resumen de Hallazgos

| Heurística | Problemas críticos (3-4) | Problemas menores (1-2) | Promedio severidad |
|------------|--------------------------|------------------------|--------------------|
| 1. Visibilidad estado | | | |
| 2. Lenguaje usuario | | | |
| 3. Control usuario | | | |
| 4. Consistencia | | | |
| 5. Prevención errores | | | |
| 6. Reconocimiento | | | |
| 7. Flexibilidad | | | |
| 8. Diseño minimalista | | | |
| 9. Recuperación errores | | | |
| 10. Ayuda/Documentación | | | |
| **TOTAL** | | | |

---

## Lista de Mejoras Priorizadas

| Prioridad | Heurística | Descripción del problema | Solución propuesta |
|-----------|------------|--------------------------|-------------------|
| Alta | | | |
| Alta | | | |
| Media | | | |
| Media | | | |
| Baja | | | |

---

**Firma del evaluador:** ________________  
**Tiempo de evaluación:** ________________  
