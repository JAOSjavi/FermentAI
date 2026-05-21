# Pruebas Exploratorias — FermentAI

**Fecha:** ________________  
**Tester:** ________________  
**Versión:** 1.0.0  
**Entorno:** [ ] Local  [ ] Staging  [ ] Producción  
**URL Frontend:** http://localhost:3000  
**URL Backend:** http://localhost:8000  

---

## Criterios de aceptación
- **PASS**: Comportamiento esperado confirmado  
- **FAIL**: Comportamiento incorrecto o error visible  
- **N/A**: No aplica en este entorno  
- **BLOCKER**: Impide continuar otras pruebas  

---

## 1. Inicio de Sesión y Registro

| # | Escenario | Resultado | Notas |
|---|-----------|-----------|-------|
| 1.1 | Navegar a `/` redirige a `/login` si no hay sesión | | |
| 1.2 | Login con `jesus.coral@ucc.edu.co` / `investigador123` — éxito | | |
| 1.3 | Login con email inexistente — mensaje de error claro | | |
| 1.4 | Login con contraseña incorrecta — mensaje de error claro | | |
| 1.5 | Login con campos vacíos — validación del formulario | | |
| 1.6 | Registro de nuevo colaborador con datos válidos — éxito | | |
| 1.7 | Registro con email ya existente — error informativo | | |
| 1.8 | Registro con contraseña muy corta — validación | | |
| 1.9 | Botón "Cerrar sesión" — redirige a `/login` | | |
| 1.10 | Acceder a `/dashboard` sin sesión — redirige a `/login` | | |

---

## 2. Dashboard Principal

| # | Escenario | Resultado | Notas |
|---|-----------|-----------|-------|
| 2.1 | Dashboard carga tras login — sin errores en consola | | |
| 2.2 | Nombre del usuario visible en el header/sidebar | | |
| 2.3 | Rol del usuario visible (Investigador / Colaborador) | | |
| 2.4 | Menú de navegación completo y funcional | | |
| 2.5 | Responsividad en ventana reducida a 768px | | |
| 2.6 | Responsividad en ventana reducida a 375px (móvil) | | |

---

## 3. Subida de Aportes (Colaborador)

| # | Escenario | Resultado | Notas |
|---|-----------|-----------|-------|
| 3.1 | Formulario de subida visible para colaboradores | | |
| 3.2 | Subir ZIP válido (estructura FERM##/imagenes + CSV) — éxito | | |
| 3.3 | Subir archivo que no es .zip — error informativo | | |
| 3.4 | Subir ZIP sin carpeta FERM## — error con detalle | | |
| 3.5 | Subir ZIP sin CSV de metadatos — error con detalle | | |
| 3.6 | Subir ZIP con CSV que tiene columnas faltantes — error | | |
| 3.7 | Subir ZIP con imágenes sin nombre válido — error | | |
| 3.8 | Indicador de progreso durante la subida | | |
| 3.9 | Mensaje de confirmación tras subida exitosa | | |
| 3.10 | Límite de 5 subidas/hora: la 6ª devuelve error 429 | | |

---

## 4. Mis Aportes

| # | Escenario | Resultado | Notas |
|---|-----------|-----------|-------|
| 4.1 | Lista de aportes propios visible | | |
| 4.2 | Estado de cada aporte visible (pendiente/aprobado/rechazado) | | |
| 4.3 | Aporte rechazado muestra observaciones del investigador | | |
| 4.4 | Sin aportes — mensaje vacío informativo | | |

---

## 5. Revisión de Aportes (Investigador)

| # | Escenario | Resultado | Notas |
|---|-----------|-----------|-------|
| 5.1 | Lista de aportes pendientes visible para investigador | | |
| 5.2 | Botón "Aprobar" visible y funcional | | |
| 5.3 | Botón "Rechazar" requiere campo de observaciones | | |
| 5.4 | Rechazar sin observaciones — error de validación | | |
| 5.5 | Aporte aprobado desaparece de la cola de revisión | | |
| 5.6 | Colaborador recibe notificación tras aprobación | | |
| 5.7 | Colaborador recibe notificación tras rechazo | | |
| 5.8 | Ruta de revisión oculta para colaboradores | | |

---

## 6. Datasets Aprobados

| # | Escenario | Resultado | Notas |
|---|-----------|-----------|-------|
| 6.1 | Página `/dashboard/datasets` carga correctamente | | |
| 6.2 | Solo aparecen datasets con estado "aprobado" | | |
| 6.3 | Filtro por código FERM## funciona | | |
| 6.4 | Filtro por estado de fermentación funciona | | |
| 6.5 | Imágenes de los datasets se muestran correctamente | | |
| 6.6 | Botón "Ver más imágenes" expande el card | | |
| 6.7 | Enlace externo de imagen abre en nueva pestaña | | |
| 6.8 | Sin resultados — mensaje informativo | | |

---

## 7. Notificaciones

| # | Escenario | Resultado | Notas |
|---|-----------|-----------|-------|
| 7.1 | Página de notificaciones carga | | |
| 7.2 | Notificaciones no leídas marcadas visualmente | | |
| 7.3 | Marcar notificación como leída funciona | | |
| 7.4 | Sin notificaciones — estado vacío informativo | | |

---

## 8. Control de Acceso por Roles

| # | Escenario | Resultado | Notas |
|---|-----------|-----------|-------|
| 8.1 | Colaborador no puede acceder a `/dashboard/revisar` | | |
| 8.2 | API `POST /api/revisar/{id}/aprobar` con token colaborador → 403 | | |
| 8.3 | API `GET /api/fermentaciones` sin token → 401 | | |
| 8.4 | Token expirado/inválido → redirige a login | | |

---

## 9. Observaciones Generales

| # | Aspecto | Observación |
|---|---------|-------------|
| 9.1 | Mensajes de error claros y en español | |
| 9.2 | Tiempos de carga aceptables (< 3 s) | |
| 9.3 | Sin errores en consola del navegador | |
| 9.4 | Formularios con placeholder informativos | |
| 9.5 | Paleta de colores coherente con la identidad del proyecto | |
| 9.6 | Iconografía coherente | |
| 9.7 | Favicon presente | |
| 9.8 | Título de pestaña descriptivo en cada página | |

---

## Bugs encontrados durante exploración

| # | Descripción | Severidad | Pasos para reproducir |
|---|-------------|-----------|----------------------|
| | | | |
| | | | |

---

**Firma del tester:** ________________  
**Tiempo invertido:** ________________  
