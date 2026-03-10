# CiberCortex IA — MVP Scope Definition

**Version:** 0.1.0
**Date:** 2026-03-10
**Decisión:** Este documento es un contrato de alcance. Nada entra al MVP sin aprobación explícita.

---

## Principio del MVP

> El MVP de CiberCortex IA debe ser **útil, correcto y seguro**, no completo.
> Validamos el flujo completo: registrar → descubrir → evaluar → reportar.
> No validamos escala, integración enterprise, ni autonomía de IA todavía.

---

## ✅ ENTRA en el MVP

### Workspace: Exposure

| Feature | Descripción | Criterio de Aceptación |
|---|---|---|
| Registro de activos | Formulario CRUD para registrar IP/hostname, tipo, owner, scope de autorización | Asset guardado en BD con estado "authorized" |
| Service Discovery | Ejecución de Nmap TCP SYN scan sobre asset autorizado | Lista de puertos abiertos + servicios detectados guardada |
| CVE Lookup | Consulta a NVD API por CPE o software+versión detectados | Lista de CVEs asociados con CVSS score |
| Exposure Summary | Vista por asset: servicios + CVEs correlacionados | Página de detalle del asset funcional |
| Reporte PDF básico | Exportación de un asset o un grupo con servicios + CVEs | PDF generado con datos correctos |

### Workspace: Hardening

| Feature | Descripción | Criterio de Aceptación |
|---|---|---|
| CIS Check Input | Formulario o script para registrar resultados de 10 checks CIS Level 1 (Linux) | Checks guardados con pass/fail/not-applicable |
| Hardening Score | Cálculo de score porcentual por asset (checks pasados / total) | Score visible en UI y exportable |
| Remediation List | Lista de checks fallidos con recomendación textual incluida | Por cada fail, texto de corrección visible |
| Re-evaluation log | Registro de fecha/score en cada evaluación para ver tendencia | Histórico de al menos 2 evaluaciones comparables |

### Core / Transversal

| Feature | Descripción | Criterio de Aceptación |
|---|---|---|
| Autenticación JWT | Login con usuario/contraseña, token JWT con expiración | Login funcional, endpoints protegidos |
| RBAC básico | Roles: Admin, Analyst, Read-Only | Cada rol sólo puede ejecutar sus acciones permitidas |
| Audit Log | Toda acción de scan/modificación guardada con user+timestamp | Log consultable en UI |
| API REST documentada | FastAPI con OpenAPI auto-generado | Swagger UI accesible en /docs |

---

## ❌ NO ENTRA en el MVP

### Features pospuestas a Fase 2

| Feature | Razón de exclusión |
|---|---|
| AI Advisory (Claude API) | Requiere prompt engineering + contexto de asset; validar flujo base primero |
| OpenSCAP automatizado | Integración compleja con SCAP Security Guide, post-MVP |
| Dashboard ejecutivo con gráficos | Primero validar datos, luego visualizarlos con calidad |
| Web Posture checker (TLS, headers) | Módulo separado, Fase 2 |
| Notificaciones / alertas | Requiere sistema de eventos, Fase 2 |
| Importación de resultados externos (Nessus, Qualys CSV) | Parsers complejos, Fase 2 |
| Scoring multi-activo / tendencias org | Requiere datos acumulados, Fase 3 |

### Features que nunca entran

| Feature | Razón |
|---|---|
| Explotación de CVEs | Fuera del alcance ético y de producto |
| Auto-remediation sin supervisión humana | Riesgo operacional, requiere aprobación manual siempre |
| Escaneo de activos no autorizados | Violación de límites de uso |
| Integración C2 / payloads | Prohibido por design |
| Brute force / credential testing | Prohibido por design |

---

## Definición de "Done" para el MVP

El MVP se considera completo cuando:

1. Un analista puede registrar un activo y ejecutar un scan de servicios.
2. Los CVEs del activo se correlacionan correctamente con el NVD.
3. Un admin puede registrar checks CIS y ver el hardening score.
4. Se puede exportar un reporte PDF con los hallazgos de un activo.
5. Todas las acciones quedan en el audit log.
6. La autenticación JWT protege todos los endpoints.
7. Los tests de integración principales pasan.

---

## Métricas de Validación del MVP

| Métrica | Target |
|---|---|
| Assets registrables | ≥ 50 sin degradación de performance |
| Tiempo de scan TCP (host único) | < 60 segundos |
| CVE lookup latencia | < 3 segundos por consulta NVD |
| Generación reporte PDF | < 30 segundos |
| Cobertura de tests backend | ≥ 70% en módulos core |
| Zero vulnerabilidades críticas en dependencias | Verificado con pip-audit / npm audit |

---

## Criterios Anti-Scope-Creep

Antes de añadir cualquier feature al MVP, debe cumplir **los tres criterios**:

1. **¿Bloquea el flujo principal?** Si no, es Fase 2.
2. **¿Lo han pedido al menos 2 usuarios objetivo?** Si no, es hipotético.
3. **¿Puede construirse en < 1 sprint sin nueva deuda técnica?** Si no, espera.

---

*Este documento se revisa al inicio de cada sprint. Todo cambio requiere aprobación del product owner.*
