# CiberCortex IA — Product Roadmap

**Version:** 0.1.0
**Date:** 2026-03-10
**Metodología:** Fases con criterios de salida definidos. No se avanza de fase sin validar la anterior.

---

## Fase 0 — Fundación (Actual)
**Objetivo:** Entorno técnico listo, arquitectura definida, equipo alineado.

### Entregables
- [x] PROJECT_BRIEF.md
- [x] MVP_SCOPE.md
- [x] SAFETY_GUARDRAILS.md
- [x] ARCHITECTURE.md
- [x] ROADMAP.md
- [ ] Stack instalado y funcionando (Python + FastAPI + PostgreSQL + Redis)
- [ ] Repositorio Git inicializado con estructura de carpetas
- [ ] Docker Compose básico (api + db + redis)
- [ ] Pre-commit hooks (linting, security scanning)

### Criterio de salida
Un desarrollador nuevo puede clonar el repo, ejecutar `docker compose up` y tener la API corriendo con `/health` respondiendo.

---

## Fase 1 — MVP Core
**Objetivo:** Flujo completo registrar → descubrir → evaluar → reportar funcionando.

### Sprint 1 — Auth + Asset Management
- [ ] Modelos de BD: users, assets, audit_log
- [ ] Auth JWT (login, refresh, logout)
- [ ] RBAC básico (Admin, Analyst, Read-Only)
- [ ] CRUD de assets (registro, edición, autorización)
- [ ] Audit log: registro de todas las acciones
- [ ] Tests de integración: auth + assets

### Sprint 2 — Exposure: Discovery + CVE
- [ ] Celery worker configurado
- [ ] Task: `run_nmap_scan` sobre asset autorizado
- [ ] Modelo: scan_jobs, discovered_services
- [ ] NVD API client (rate-limited, cacheado)
- [ ] Task: `correlate_cves` por asset
- [ ] Endpoints: GET /exposure/assets/{id}/services, GET /exposure/assets/{id}/cves
- [ ] Tests: mock de Nmap + NVD API

### Sprint 3 — Hardening: CIS Assessments
- [ ] Definición de 10 CIS Level 1 checks (Linux)
- [ ] Modelos: assessments, check_results, remediation_items
- [ ] Endpoint: POST /hardening/assessments (registrar evaluación)
- [ ] Lógica de scoring: % de checks pasados, ponderado por severidad
- [ ] Endpoint: GET /hardening/assets/{id}/score
- [ ] Vista de remediation list por assessment
- [ ] Tests: scoring engine

### Sprint 4 — Reporting + Frontend Base
- [ ] Report generation service: PDF técnico básico (WeasyPrint)
- [ ] Endpoint: POST /reports/generate
- [ ] Frontend: Layout base, autenticación
- [ ] Frontend: Asset list + asset detail (services + CVEs)
- [ ] Frontend: Assessment detail + score + remediation list
- [ ] Frontend: Botón "Generate Report" + descarga PDF

### Criterio de salida de Fase 1
- Demo completo del flujo: asset → scan → CVEs → assessment → score → PDF
- Audit log captura todas las acciones del demo
- Tests backend ≥ 70% coverage en módulos core
- Zero vulnerabilidades críticas en dependencias (pip-audit + npm audit)

---

## Fase 2 — Expansión de Capacidades
**Objetivo:** Añadir valor a los dos workspaces con features de alto impacto.

### Exposure — Expansión
- [ ] Web Posture Checker: TLS grade, HTTP headers (HSTS, CSP, X-Frame-Options)
- [ ] Attack Surface view: agrupación por riesgo, no por puerto
- [ ] Importación de resultados externos (Nessus XML, básico)
- [ ] Dashboard Exposure: asset overview, top CVEs, surface heatmap

### Hardening — Expansión
- [ ] OpenSCAP integration: importar XCCDF results de scans externos
- [ ] CIS Benchmarks Level 2
- [ ] Tendencia de hardening score: gráfico por asset en el tiempo
- [ ] Re-evaluation tracker: comparar assessments consecutivos
- [ ] Export: XLSX con check results y estado de remediación

### AI Assistant — Primera versión
- [ ] Claude API integration (claude-sonnet-4-6)
- [ ] `/exposure/cve/{id}/explain`: explicación en lenguaje natural de CVE en contexto del asset
- [ ] `/hardening/checks/{id}/explain`: explicación de check fallido + pasos de corrección
- [ ] Rate limiting de llamadas IA por usuario
- [ ] Prompt templates defensivos con system prompt restrictivo

### Reporting — Expansión
- [ ] Template ejecutivo: puntuación global, top riesgos, estado de remediación
- [ ] Reporte DOCX exportable
- [ ] Reporte multi-asset (grupo de hosts)

### Criterio de salida de Fase 2
- AI Advisor funcional con restricciones validadas
- OpenSCAP import probado con al menos 1 perfil real (ssg-rhel9)
- Dashboard con datos reales, no mock

---

## Fase 3 — Enterprise Features
**Objetivo:** Escalar para organizaciones con múltiples equipos y necesidades de cumplimiento.

### Multi-tenancy y Acceso
- [ ] Workspaces de organización (multi-tenant básico)
- [ ] SSO / SAML 2.0 integration
- [ ] API Keys para integraciones programáticas

### Compliance y Reporting Avanzado
- [ ] Mappings CVE → MITRE ATT&CK (defensa, no ataque)
- [ ] Compliance scoring: CIS, NIST CSF, ISO 27001 (parcial)
- [ ] Reporte de tendencias histórico (6 meses)
- [ ] Scheduled reports: generación automática periódica

### Integraciones
- [ ] Jira / GitHub Issues: crear ticket de remediación desde la plataforma
- [ ] Webhook notifications: alertas a Slack/Teams cuando score baja
- [ ] SIEM export: Syslog / CEF format para audit events

### Criterio de salida de Fase 3
- Organización piloto usando la plataforma en producción
- SLA de disponibilidad definido y monitorizado
- Penetration test externo de la plataforma superado

---

## Fase 4 — Madurez y Escala (Visión)
**Objetivo:** Producto maduro, con base de usuarios activos y roadmap guiado por datos de uso.

- [ ] Plugin system para scanners de terceros
- [ ] API pública documentada con versioning
- [ ] SaaS deployment option
- [ ] Advanced analytics: ML-based risk scoring
- [ ] Remediation workflow: aprobaciones, assignees, SLA de resolución

---

## Principios del Roadmap

1. **No se avanzan features ofensivas en ninguna fase.** Si aparece en la lista, es un error.
2. **Cada feature necesita un criterio de aceptación antes de comenzar.**
3. **La calidad de los datos siempre supera la cantidad de features.**
4. **El AI assistant amplifica al analista, no lo reemplaza.**
5. **Un reporte de mala calidad es peor que no tener reporte.**

---

*Roadmap revisado al inicio de cada fase. Los timings son deliberadamente omitidos — la velocidad depende del equipo y el contexto.*
