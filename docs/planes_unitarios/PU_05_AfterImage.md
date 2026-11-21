# Plan de Pruebas Unitarias Específico `PU-05`: Módulo `AfterImage.py`

## 1. Identificación y Metadatos
* **ID del Plan:** `PU-05-AFTERIMAGE`
* **Módulo Bajo Prueba:** [`AfterImage.py`](../../AfterImage.py) (`incStat`, `incStat_cov`, `incStatDB`)
* **Suite de Prueba:** [`tests/unit/test_afterimage.py`](../../tests/unit/test_afterimage.py)
* **Etapa del Pipeline CI:** `Stage 2 - Pruebas Unitarias (Pytest + Coverage)`
* **Casos Consolidados:** **2 pruebas** (`UT-AI-001` a `UT-AI-002`)
* **Cobertura Alcanzada:** **98%** (284/291 líneas ejecutadas)

## 2. Intuición Técnica y Alcance
`AfterImage` mantiene perfiles estadísticos de flujos de red en tiempo $O(1)$ usando decaimiento exponencial $2^{-\lambda \Delta t}$ tanto para estadísticas 1D (`incStat`), covarianzas 2D (`incStat_cov`) como para la tabla hash (`incStatDB`).

## 3. Especificación de Casos de Prueba Unitarios

| ID Caso | Clase / Método | Descripción y Datos de Entrada | Oráculo / Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **`UT-AI-001`** | `incStat`, `incStat_cov` | Decaimiento `Lambda=1.0`, modo `isTypeDiff=True`, magnitud `(3,4)`, encabezados 1D/2D y 7 actualizaciones acopladas `A`/`B`. | Factor $\gamma=0.5$, peso $w=1.5$, jitter $\Delta t=2.0$, magnitud `5.0`, vectores `get_stats1..4` sin `NaN` y encabezados `ver=1..5`. |
| **`UT-AI-002`** | `incStatDB` (`register`, `get_*`, `cleanOutOldRecords`) | `limit=2` con 3 flujos distintos, consultas sobre claves ausentes, flujos 1D/2D/nD y poda en `t=20.0` con `cutoffWeight=0.01`. | Lanza `LookupError` al 3er registro, retorna `NaN`/`[]` en ausentes, resuelve vector 7D/nD y elimina los 2 registros caducados. |

## 4. Comando de Verificación
```powershell
python -m pytest tests/unit/test_afterimage.py --cov=AfterImage --cov-report=term-missing
```
