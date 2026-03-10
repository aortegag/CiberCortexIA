# CiberCortex IA — Project Brief

**Version:** 0.1.0
**Date:** 2026-03-10
**Status:** Pre-development / Strategic Definition
**Classification:** Internal — Confidential

---

## 1. Descripción del Producto

CiberCortex IA es una plataforma de ciberseguridad defensiva orientada a organizaciones que necesitan gestionar, evaluar y mejorar su postura de seguridad de forma estructurada, trazable y asistida por inteligencia artificial.

La plataforma no es una herramienta ofensiva ni de pentesting automatizado. Es una herramienta de **visibilidad, evaluación y remediación asistida** sobre activos explícitamente autorizados.

---

## 2. Problema que Resuelve

| Problema | Descripción |
|---|---|
| Inventario opaco | Las organizaciones no saben qué activos tienen expuestos |
| CVEs sin contexto | Se conocen vulnerabilidades pero no su impacto real en el entorno |
| Hardening inconsistente | Los servidores no siguen un estándar auditable (CIS, STIGs) |
| Remediación sin priorización | Se parchea lo urgente, no lo importante |
| Reporting manual | Los informes consumen tiempo y carecen de estandarización |

---

## 3. Propuesta de Valor

> **"Saber qué tienes expuesto, cuán débil está configurado, y qué hacer primero."**

- Inventario de activos gestionado, con metadatos de negocio
- Surface analysis contextualizado (no raw ports, sino riesgo real)
- Hardening scoring basado en CIS Benchmarks y OpenSCAP
- Priorización de remediación por impacto + facilidad de corrección
- Reportes técnicos y ejecutivos generados automáticamente
- Asesor IA para explicar vulnerabilidades y guiar correcciones

---

## 4. Usuarios Objetivo

| Perfil | Necesidad Principal |
|---|---|
| Security Engineer | Visibilidad técnica, datos de CVEs, detalle de configuración |
| CISO / Security Manager | Scoring de postura, tendencias, reportes ejecutivos |
| SysAdmin | Guía de hardening, pasos de remediación concretos |
| Auditor | Evidencias trazables, exportación estandarizada |

---

## 5. Workspaces del Producto

### A) Exposure
Orientado a conocer la superficie de ataque autorizada de la organización.

| Módulo | Función |
|---|---|
| Asset Inventory | Registro y gestión de activos autorizados |
| Service Discovery | Descubrimiento seguro de servicios en activos registrados |
| Attack Surface | Análisis de exposición: puertos, protocolos, servicios identificados |
| CVE Correlation | Correlación de versiones de software con CVEs del NVD |
| Web Posture | Revisión de cabeceras HTTP, TLS, configuración web básica |
| Exposure Reporting | Generación de informes técnicos y ejecutivos |

### B) Hardening
Orientado a evaluar y mejorar la configuración de seguridad de los sistemas.

| Módulo | Función |
|---|---|
| CIS Assessment | Evaluación automatizada basada en CIS Benchmarks |
| OpenSCAP Integration | Ejecución e importación de resultados SCAP/XCCDF |
| Hardening Score | Scoring de bastionado por activo, grupo y organización |
| Remediation Advisor | Recomendaciones específicas con pasos de corrección |
| AI Assistant | Explicación contextual de riesgos y medidas correctivas (Claude API) |
| Re-evaluation Tracker | Seguimiento del progreso de remediación en el tiempo |

---

## 6. Principios de Diseño

1. **Autorización explícita**: Ninguna acción de escaneo se ejecuta sin que el activo esté registrado y autorizado en la plataforma.
2. **Trazabilidad total**: Toda acción queda registrada en audit log inmutable.
3. **Separación de concerns**: Descubrir ≠ Evaluar ≠ Priorizar ≠ Reportar.
4. **Modularidad**: Cada módulo puede funcionar de forma independiente.
5. **Enterprise-grade UX**: La interfaz debe parecer profesional y confiable, no un script con UI.
6. **No scope creep ofensivo**: La plataforma no implementará técnicas de explotación, evasión ni movimiento lateral.

---

## 7. Fuera de Alcance (siempre)

- Autopwn o explotación automática de vulnerabilidades
- Phishing, ingeniería social o campañas de ataque
- Movimiento lateral o persistencia en sistemas comprometidos
- Evasión de controles de seguridad (AV, EDR, firewall bypass)
- Robo o extracción de credenciales
- Escaneo de activos no registrados/no autorizados
- C2 (Command & Control) frameworks o listeners

---

## 8. Stack Tecnológico (propuesto)

| Capa | Tecnología | Justificación |
|---|---|---|
| Backend API | Python + FastAPI | Ecosistema rico en seguridad, tipado fuerte, async nativo |
| Base de datos | PostgreSQL | ACID, JSON support, historial de versiones |
| Cache / Queue | Redis + Celery | Tasks asíncronas para scans largos |
| Frontend | Next.js + TypeScript | SSR, componentes enterprise, ecosistema amplio |
| UI Components | shadcn/ui + Tailwind | Diseño limpio, accesible, customizable |
| Contenedores | Docker + Compose | Portabilidad, entornos reproducibles |
| Auth | OAuth2 / JWT + RBAC | Estándar, auditable, extensible a SSO |
| Scanning | Nmap (autorizado) + NVD API | Descubrimiento y correlación |
| Hardening | OpenSCAP / SCAP Security Guide | Estándar NIST, compatible CIS/STIG |
| IA | Anthropic Claude API | Explicación contextual, no autonomía de escaneo |
| Reporting | WeasyPrint / ReportLab | PDF técnicos y ejecutivos |

---

## 9. Métricas de Éxito del Producto

| Métrica | Objetivo MVP |
|---|---|
| Activos registrables | ≥ 100 por instancia |
| Tiempo de discovery | < 5 min para un /24 autorizado |
| Cobertura CIS | ≥ 10 checks Level 1 en MVP |
| Generación de reporte | < 30 segundos desde solicitud |
| Audit trail | 100% de acciones registradas |

---

*Documento mantenido por el equipo de producto de CiberCortex IA.*
