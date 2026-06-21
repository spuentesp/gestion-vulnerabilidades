# Propuesta de Gestión de Vulnerabilidades

## 1. Contexto del análisis
En este proyecto se analizaron 5 repositorios (uno principal para la propuesta y cuatro adicionales como base del muestreo):
- **`asciinema/asciinema`** (Repositorio principal para la demostración de la propuesta)
- **`n8n-io/n8n`**
- **`SillyTavern/SillyTavern`**
- **`spuentesp/lain`**
- **`spuentesp/monitor_dm_system`**

El objetivo fue identificar vulnerabilidades usando un enfoque holístico que abarca tres vectores de ataque principales: las dependencias y código fuente, los pipelines de CI/CD, y el factor humano. Las actividades previas incluyeron la generación de un Software Bill of Materials (SBOM) utilizando `syft` para todos los repositorios, así como la extracción de vulnerabilidades mediante `grype`. La propuesta de gestión de ciclo se enfoca principalmente en los hallazgos demostrativos del repositorio `asciinema/asciinema`.

## 2. Vulnerabilidades encontradas
Se identificaron tres vulnerabilidades principales que afectan diferentes capas del ciclo de vida del software:
1. Uso de acciones mutables en flujos de CI/CD (Pipeline).
2. Falta de revisión y actualización automática de dependencias (Humano).
3. Uso de código inseguro (bloques `unsafe`) en FFI (Código fuente).

## 3. Clasificación según vector de ataque
Las vulnerabilidades se clasifican de la siguiente manera:
1. **Dependencias y código fuente:** Bloques `unsafe` (Vulnerabilidad 3).
2. **Pipelines de CI/CD:** Acciones no pineadas (Vulnerabilidad 1).
3. **Humanos:** Ausencia de automatización en actualización de dependencias (Vulnerabilidad 2).

## 4. Análisis usando el ciclo Conozco → Verifico → Evidencio → Decido y Actúo
<!-- Explicación del análisis realizado para cada vulnerabilidad o grupo de vulnerabilidades. -->

### Vulnerabilidad 1: Acciones de GitHub no pineadas por hash (Unpinned Third-Party Actions)
- **Conozco:** Los flujos de CI/CD del repositorio utilizan dependencias de terceros (GitHub Actions) referenciadas por etiquetas de versión (ej. `@v5` o `@stable`) en lugar de hashes exactos (SHA). Si la cuenta de un mantenedor externo es comprometida, un atacante podría sobrescribir la etiqueta para introducir código malicioso que se ejecutaría en los pipelines del proyecto con permisos elevados.
- **Verifico:** Se revisaron los archivos `.github/workflows/ci.yml` y `.github/workflows/release.yml` en el repositorio de `asciinema/asciinema`, confirmando que acciones críticas como `actions/checkout@v5` y `dtolnay/rust-toolchain@stable` no están pineadas.
- **Evidencio:** En el archivo `release.yml`, líneas 17 y 59, se observa el uso de etiquetas mutables:
  ```yaml
  - uses: actions/checkout@v5
  - uses: dtolnay/rust-toolchain@stable
  ```
- **Decido y Actúo:** Modificar los flujos de trabajo para utilizar el hash SHA inmutable de la acción, combinado con comentarios para identificar la versión. Ejemplo: `uses: actions/checkout@a5ac7e51b41094c92402da3b24376905380afc29 # v4.1.6`. Esto previene ataques de cadena de suministro sobre los pipelines.

### Vulnerabilidad 2: Ausencia de automatización para actualización de dependencias
- **Conozco:** El repositorio no cuenta con herramientas automáticas para la gestión y actualización de dependencias (como Dependabot o Renovate). Esto traslada toda la carga al equipo humano (Vector Humanos), obligándolos a monitorear y actualizar manualmente. Esta práctica incrementa significativamente el riesgo de que vulnerabilidades conocidas permanezcan en el código fuente porque los humanos pueden olvidar o posponer las revisiones.
- **Verifico:** Se listó el contenido del directorio `.github/` y `.github/workflows/` del repositorio, verificando que no existe ningún archivo `dependabot.yml` ni configuraciones similares de seguridad automatizada.
- **Evidencio:** La estructura del directorio `.github/` solo contiene `ISSUE_TEMPLATE` y `workflows` (con rutinas básicas de CI y Release). No hay evidencia de flujos de escaneo de dependencias en Rust (Cargo) o Actions.
- **Decido y Actúo:** Añadir un archivo `.github/dependabot.yml` para habilitar el escaneo semanal del ecosistema `cargo` y `github-actions`. Esto reducirá la carga cognitiva del equipo y alertará proactivamente sobre vulnerabilidades.

## 5. Priorización de vulnerabilidades
La priorización se definió evaluando el impacto potencial frente a la dificultad de explotación y remediación:
1. **Alta Prioridad - Vulnerabilidad 1 (CI/CD):** Las acciones no pineadas son un riesgo crítico en la cadena de suministro. Si se compromete una dependencia, el atacante obtiene control de los artefactos de compilación. Su mitigación es trivial (cambiar tags por SHAs).
2. **Media Prioridad - Vulnerabilidad 2 (Humanos):** La falta de un sistema como Dependabot es una deuda técnica que incrementa pasivamente la superficie de ataque con el tiempo. Habilitarlo toma pocos minutos.
3. **Baja/Media Prioridad - Vulnerabilidad 3 (Código fuente):** Aunque un fallo de memoria en `unsafe` es severo, la explotación en el contexto de una herramienta CLI local como asciinema requiere acceso local o ingeniería social avanzada. Su parche (auditoría Miri) tomará más tiempo de desarrollo.

## 6. Acciones propuestas
Para remediar integralmente estos hallazgos, el equipo de desarrollo debe:
1. Actualizar inmediatamente `.github/workflows/ci.yml` y `release.yml` para pinear todas las GitHub Actions al SHA del commit.
2. Añadir el archivo `.github/dependabot.yml` para monitorear el ecosistema de Cargo y GitHub Actions semanalmente.
3. Integrar comprobaciones de la herramienta `Miri` en el pipeline de CI para las pruebas unitarias que involucren los módulos `pty.rs` y `tty`.

## 7. Evidencia utilizada
Toda la evidencia y datos generados se encuentran organizados en el repositorio:
- `data/`: Contiene los Software Bill of Materials generados con `syft` para los 5 repositorios en formato SPDX JSON.
- `results/`: Contiene los reportes de escaneo de dependencias generados con `grype` para los 5 repositorios.
- `scripts/analisis.py`: Script en Python utilizado para consolidar y contar las vulnerabilidades extraídas de todos los repositorios analizados.
- `evidence/reportes/resumen_analisis.txt`: Reporte final emitido por el script detallando los conteos de vulnerabilidades por repositorio y por severidad.

## 8. Conclusiones
El enfoque Conozco → Verifico → Evidencio → Decido y Actúo permitió estructurar una evaluación de seguridad robusta para el proyecto `asciinema`. Abordar las vulnerabilidades identificadas no solo mitigará los riesgos de ataques a la cadena de suministro, sino que también mejorará las prácticas del equipo (reduciendo el factor de error humano) y robustecerá la fiabilidad del código base mediante una gestión estricta de las dependencias y la memoria.
