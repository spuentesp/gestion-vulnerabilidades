# Propuesta de Gestión de Vulnerabilidades

## 1. Contexto del análisis
En este proyecto se analizaron 5 repositorios para identificar vulnerabilidades y construir una propuesta de gestión. Los repositorios evaluados fueron:
- **`asciinema/asciinema`**
- **`n8n-io/n8n`**
- **`SillyTavern/SillyTavern`**
- **`spuentesp/lain`**
- **`spuentesp/monitor_dm_system`**

El objetivo fue identificar vulnerabilidades usando un enfoque holístico que abarca tres vectores de ataque principales: las dependencias y código fuente, los pipelines de CI/CD, y el factor humano. Las actividades previas incluyeron la generación de un Software Bill of Materials (SBOM) utilizando `syft` y el escaneo de dependencias con `grype`.

## 2. Vulnerabilidades encontradas
De las 195 vulnerabilidades extraídas en total, se seleccionaron tres grupos críticos que representan los hallazgos más relevantes a través de los 5 repositorios:
1. **Librerías NPM y crates Rust con CVEs conocidos** en `SillyTavern` (`simple-git`), `monitor_dm_system` (`next`) y `lain` (`ring`).
2. **Dependencias vulnerables en flujos de CI/CD** encontradas en los pipelines de GitHub Actions de `n8n` (ej. `trivy-action`).
3. **Ausencia de políticas automatizadas** para la revisión de dependencias y uso de código no seguro (ej. bloques `unsafe` sin auditar en `asciinema`).

## 3. Clasificación según vector de ataque
1. **Dependencias y código fuente:** Librerías con vulnerabilidades críticas (CVEs en `simple-git`, `next` y `ring`).
2. **Pipelines de CI/CD:** Acciones de GitHub comprometidas u obsoletas en los flujos de integración.
3. **Humanos:** Falta de automatización (Dependabot) que obliga al equipo a actualizar manualmente, incrementando el error humano.

## 4. Análisis usando el ciclo Conozco → Verifico → Evidencio → Decido y Actúo

### Grupo 1: Vulnerabilidades en Dependencias de Código Fuente (SillyTavern, monitor_dm_system, lain)
- **Conozco:** Múltiples repositorios dependen de librerías de terceros (NPM y Cargo) que poseen vulnerabilidades públicas (ej. `GHSA-hffm-xvc3-vprc` en `simple-git`). Los atacantes podrían explotar estos fallos para ejecución de código remoto (RCE) o denegación de servicio (DoS).
- **Verifico:** Se revisaron los resultados de `grype` para los repositorios mencionados, confirmando la existencia de estas librerías en los archivos `package.json` y `Cargo.lock`.
- **Evidencio:** El archivo `results/SillyTavern_vulns.json` y `results/monitor_dm_system_vulns.json` reportan versiones desactualizadas de los paquetes.
- **Decido y Actúo:** Actualizar inmediatamente las versiones de `simple-git`, `next` y `ring` en los archivos de dependencias a las versiones parcheadas indicadas por los reportes de Grype.

### Grupo 2: Acciones Vulnerables en CI/CD (n8n y asciinema)
- **Conozco:** Los flujos de trabajo de GitHub Actions utilizan herramientas de terceros. En `n8n` se detectaron vulnerabilidades en acciones como `aquasecurity/trivy-action` (`GHSA-69fq-xp46-6x23`), y en `asciinema` se usan acciones mutables (pineadas por tags como `@v5` en vez de SHA). Esto compromete la cadena de suministro.
- **Verifico:** Se auditaron los archivos `.github/workflows/` de los repositorios, cruzándolos con los resultados del escaneo.
- **Evidencio:** La evidencia está en `results/n8n_vulns.json` y en las líneas del código fuente de `asciinema/release.yml`.
- **Decido y Actúo:** Refactorizar los pipelines de CI/CD para fijar (pinear) todas las Github Actions al commit SHA inmutable y actualizar las acciones a sus versiones más recientes y seguras.

### Grupo 3: Vector Humanos - Dependencia Manual (Todos los repositorios)
- **Conozco:** Ninguno de los repositorios tiene una estrategia automatizada uniforme para alertar sobre nuevas vulnerabilidades. Esto traslada toda la carga al equipo (Vector Humanos), quienes pueden olvidar revisar las dependencias de forma regular.
- **Verifico:** Se revisó la estructura de los 5 repositorios, confirmando la ausencia generalizada de configuraciones robustas de `dependabot.yml` en la mayoría de ellos.
- **Evidencio:** Los reportes extraídos mediante el script `scripts/analisis.py` revelan que el error humano permitió la acumulación de 195 vulnerabilidades activas en la muestra.
- **Decido y Actúo:** Obligar mediante políticas de equipo la inclusión de un archivo `.github/dependabot.yml` o Renovate en todos los repositorios para automatizar las Pull Requests de actualización de seguridad.

## 5. Priorización de vulnerabilidades
La priorización del triage debe ser la siguiente:
1. **Alta Prioridad (Grupo 1 - Código Fuente):** Los CVEs críticos en componentes como `next` o `simple-git` tienen exposición directa en producción y deben ser mitigados en el próximo sprint.
2. **Media Prioridad (Grupo 2 - CI/CD):** Las herramientas vulnerables en el pipeline podrían permitir comprometer el entorno de compilación. Se deben actualizar inmediatamente tras el parche del código fuente.
3. **Preventiva (Grupo 3 - Humanos):** La instalación de Dependabot es un parche arquitectónico preventivo para detener la acumulación técnica de vulnerabilidades a futuro.

## 6. Acciones propuestas
1. **Parcheo Activo:** Ejecutar `npm audit fix` y `cargo update` en `SillyTavern`, `monitor_dm_system` y `lain` para mitigar las librerías críticas identificadas.
2. **Hardening de Pipelines:** Revisar y pinear por SHA todas las GitHub Actions en `n8n` y `asciinema`.
3. **Automatización:** Habilitar Dependabot en los 5 repositorios evaluados.

## 7. Evidencia utilizada
Toda la evidencia y datos generados se encuentran organizados en el repositorio:
- `data/`: Contiene los Software Bill of Materials generados con `syft` para los 5 repositorios en formato SPDX JSON.
- `results/`: Contiene los reportes de escaneo de dependencias generados con `grype` para los 5 repositorios.
- `scripts/analisis.py`: Script en Python utilizado para consolidar y contar las vulnerabilidades extraídas de todos los repositorios analizados.
- `evidence/reportes/resumen_analisis.txt`: Reporte final emitido por el script detallando los conteos de vulnerabilidades por repositorio y por severidad.

## 8. Conclusiones y Respuesta a la Pregunta Central
**¿Cómo debería gestionar el equipo las vulnerabilidades encontradas, considerando su origen, su evidencia y el nivel de riesgo que representan?**

El equipo debe gestionar las vulnerabilidades mediante una **estrategia de mitigación en capas basada en el riesgo**:
1. **Por su nivel de riesgo:** Atender inmediatamente los fallos en dependencias base (como `simple-git` y `next`) aplicando parches críticos (`npm audit fix` / `cargo update`), dado que presentan exposición directa a ataques (ej. RCE) comprobados por la evidencia de Grype.
2. **Por su origen en CI/CD:** Posteriormente, asegurar la inmutabilidad de los flujos de integración pineando los SHAs de las GitHub Actions (ej. en `n8n` y `asciinema`) para cortar de raíz cualquier posible ataque de cadena de suministro sobre los repositorios.
3. **Por su prevención (Factor Humano):** Finalmente, para evitar que la suma de vulnerabilidades vuelva a alcanzar cifras críticas (195 hallazgos), el equipo debe instalar de forma obligatoria bots de automatización (Dependabot/Renovate) en todos los repositorios, delegando el monitoreo continuo a las herramientas y retirando la carga de memoria humana.
