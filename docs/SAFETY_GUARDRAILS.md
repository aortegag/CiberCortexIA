# CiberCortex IA — Safety Guardrails

**Version:** 0.1.0
**Date:** 2026-03-10
**Tipo:** Documento normativo — no negociable por decisión de producto

---

## Propósito

Este documento define los límites éticos, técnicos y funcionales del producto CiberCortex IA. Es vinculante para todo el equipo de desarrollo, diseño y producto. Ninguna funcionalidad que viole estas restricciones debe ser implementada, aunque exista demanda de usuario.

---

## 1. Principios Fundamentales

### 1.1 Activos Autorizados Únicamente

**TODA** acción activa (scan, discovery, evaluación) se ejecuta **exclusivamente** sobre activos que:
- Están registrados en la base de datos de la plataforma.
- Tienen estado `authorized` asignado por un administrador.
- Tienen un owner identificado y un scope de autorización documentado.

**Implementación técnica requerida:**
```python
# Pseudocódigo obligatorio antes de cualquier scan
def execute_scan(asset_id: str, user: User) -> ScanResult:
    asset = db.get_asset(asset_id)
    assert asset is not None, "Asset not found"
    assert asset.status == AssetStatus.AUTHORIZED, "Asset not authorized"
    assert asset.authorization_scope is not None, "No authorization scope defined"
    audit_log.record(action="scan_start", asset_id=asset_id, user=user)
    # ... proceed with scan
```

### 1.2 No Explotación

La plataforma **nunca** implementará, integrará ni orquestará:

| Capacidad prohibida | Ejemplos concretos |
|---|---|
| Explotación de vulnerabilidades | Metasploit modules, exploit payloads, buffer overflows |
| Movimiento lateral | Pass-the-hash, Kerberoasting, SMB relay |
| Evasión de controles | AV bypass, EDR evasion, AMSI bypass |
| Phishing / ingeniería social | Email spoofing, credential harvesting pages |
| Persistencia en sistemas | Backdoors, webshells, cron implants |
| Credential theft | Password dumping, LSASS access, keylogging |
| C2 / RAT | Command & Control listeners, reverse shells |
| DoS / DDoS | Flood attacks, amplification |

### 1.3 Principio de Menor Privilegio en Scans

Los scans se ejecutan con los permisos **mínimos necesarios**:
- Nmap se ejecuta como usuario no-root cuando sea posible.
- No se realizan scans UDP exhaustivos (alto noise, bajo valor en MVP).
- OpenSCAP se ejecuta en modo **audit-only**, nunca en modo de remediación automática.

---

## 2. Restricciones de Diseño

### 2.1 AI Assistant — Límites del Módulo IA

El módulo de IA (Claude API) **sólo puede**:
- Explicar una vulnerabilidad en lenguaje natural.
- Sugerir pasos de remediación basados en información pública (CVE, CIS, NIST).
- Contextualizar el riesgo según el tipo de activo registrado.
- Responder preguntas sobre configuración segura.

El módulo de IA **nunca puede**:
- Generar exploits, payloads o código de ataque.
- Sugerir cómo evadir controles de seguridad.
- Proporcionar técnicas de post-explotación.
- Actuar de forma autónoma sobre ningún sistema.

**Implementación**: Los prompts al Claude API siempre incluirán instrucciones de sistema que restringen estas capacidades. Los prompts del usuario se sanitizarán antes de enviarse.

### 2.2 Outputs del Sistema

Los reportes generados **siempre incluirán**:
- Fecha y scope de autorización del activo evaluado.
- Identificación del analista que ejecutó la evaluación.
- Disclaimer de uso autorizado.

Los reportes generados **nunca incluirán**:
- Pruebas de concepto (PoC) de explotación.
- Passwords o secretos en claro descubiertos accidentalmente.
- Información que permita re-crear un ataque.

### 2.3 Audit Log

- **Append-only**: El audit log no puede ser modificado ni eliminado por ningún usuario, incluyendo admins.
- **Datos mínimos por entrada**: timestamp, user_id, action, target_asset_id, result_summary.
- **Retención**: Mínimo 90 días. Configurable hasta 2 años.
- **Exportable**: Para auditorías externas, en formato JSON o CSV firmado.

---

## 3. Controles de Acceso

### 3.1 Roles y Permisos

| Acción | Admin | Analyst | Read-Only |
|---|---|---|---|
| Registrar activos | ✅ | ✅ | ❌ |
| Autorizar activos | ✅ | ❌ | ❌ |
| Ejecutar scans | ✅ | ✅ | ❌ |
| Ver resultados | ✅ | ✅ | ✅ |
| Exportar reportes | ✅ | ✅ | ✅ |
| Ver audit log | ✅ | ❌ | ❌ |
| Gestionar usuarios | ✅ | ❌ | ❌ |
| Borrar activos | ✅ | ❌ | ❌ |
| Configurar sistema | ✅ | ❌ | ❌ |

### 3.2 Autenticación

- JWT con expiración de 8 horas máximo.
- Refresh tokens con revocación centralizada.
- Rate limiting en endpoints de autenticación: máximo 10 intentos / minuto.
- Passwords hasheados con bcrypt (cost factor ≥ 12).

---

## 4. Gestión de Datos Sensibles

### 4.1 En Base de Datos

- Las credenciales de acceso a sistemas auditados (si aplica en fases futuras) se almacenan **encriptadas** (AES-256 o KMS externo).
- No se almacenan en BD: contraseñas en claro, tokens de sesión completos, claves privadas.

### 4.2 En Tránsito

- Todas las comunicaciones API usan TLS 1.2+ obligatorio.
- Certificados auto-firmados sólo permitidos en entornos de desarrollo.

### 4.3 En Reportes

- Los reportes PDF incluyen marca de agua con el nombre del analista y fecha.
- No se exportan resultados de scans a sistemas externos sin acción explícita del usuario.

---

## 5. Uso Aceptable

### Este producto está autorizado para:

- Evaluación de seguridad de sistemas **propios** de la organización.
- Evaluación de sistemas de **terceros con contrato y autorización escrita**.
- Entornos de laboratorio y pruebas controladas con activos dedicados.
- Formación y certificación interna en ciberseguridad defensiva.

### Este producto NO está autorizado para:

- Escanear sistemas sin autorización explícita del propietario.
- Uso en competencias CTF con activos reales (sólo en rangos aislados).
- Actividades de Bug Bounty sin programa activo y scope definido.
- Cualquier uso que viole las leyes locales de ciberseguridad o acceso no autorizado.

---

## 6. Proceso de Revisión

Este documento se revisa:
- Al inicio de cada fase de desarrollo.
- Cuando se propone añadir una nueva capacidad de escaneo o análisis.
- Ante cualquier incidente de seguridad relacionado con la plataforma.

**Aprobación de cambios:** Requiere revisión del equipo de producto + responsable de seguridad.

---

*Incumplir estas restricciones en código comprometido puede resultar en la cancelación del proyecto.*
