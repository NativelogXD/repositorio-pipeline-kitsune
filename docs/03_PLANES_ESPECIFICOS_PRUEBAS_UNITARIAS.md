# Documentación Específica de Cada Plan de Pruebas Unitarias (`PU-01` a `PU-08`)

> **Proyecto:** `Kitsune-py`  
> **Directorio de Implementación:** [`tests/unit/`](../tests/unit)  
> **Framework de Ejecución:** `pytest` + `pytest-cov`  
> **Total de Pruebas Ejecutables:** **15 pruebas unitarias consolidadas**  
> **Semilla de Reproducibilidad:** `np.random.default_rng(seed=42)` (en [`tests/conftest.py`](../tests/conftest.py)) y `numpy.random.RandomState(1234)` (interno en `KitNET/dA.py`).

---

## Índice de Planes de Pruebas Unitarias por Módulo

1. [**Plan Unitario 1 (`PU-01` — `PU-UTILS`)**: Funciones Matemáticas, Distribuciones y Ventana Móvil (`KitNET/utils.py`) — 2 pruebas](#1-plan-de-pruebas-unitarias-pu-01--módulo-kitnetutilspy)
2. [**Plan Unitario 2 (`PU-02` — `PU-DA`)**: Denoising Autoencoder y Retropropagación SGD (`KitNET/dA.py`) — 2 pruebas](#2-plan-de-pruebas-unitarias-pu-02--módulo-kitnetdapy)
3. [**Plan Unitario 3 (`PU-03` — `PU-CORCLUST`)**: Clustering Incremental de Correlación (`KitNET/corClust.py`) — 2 pruebas](#3-plan-de-pruebas-unitarias-pu-03--módulo-kitnetcorclustpy)
4. [**Plan Unitario 4 (`PU-04` — `PU-KITNET`)**: Orquestador del Ensamble de Autoencoders (`KitNET/KitNET.py`) — 2 pruebas](#4-plan-de-pruebas-unitarias-pu-04--módulo-kitnetkitnetpy)
5. [**Plan Unitario 5 (`PU-05` — `PU-AFTERIMAGE`)**: Estadísticas Incrementales Amortiguadas 1D/2D y Base Hash (`AfterImage.py`) — 2 pruebas](#5-plan-de-pruebas-unitarias-pu-05--módulo-afterimagepy)
6. [**Plan Unitario 6 (`PU-06` — `PU-NETSTAT`)**: Estadísticas Multiperspectiva de Tráfico de Red (`netStat.py`) — 2 pruebas](#6-plan-de-pruebas-unitarias-pu-06--módulo-netstatpy)
7. [**Plan Unitario 7 (`PU-07` — `PU-FE`)**: Captura y Extracción de Paquetes TSV/PCAP (`FeatureExtractor.py`) — 2 pruebas](#7-plan-de-pruebas-unitarias-pu-07--módulo-featureextractorpy)
8. [**Plan Unitario 8 (`PU-08` — `PU-KITSUNE`)**: Fachada Principal del Detector NIDS (`Kitsune.py`) — 1 prueba](#8-plan-de-pruebas-unitarias-pu-08--módulo-kitsunepy)

*(Nota: Cada plan también dispone de su ficha individual en [`docs/planes_unitarios/`](planes_unitarios/)).*

---

## 1. Plan de Pruebas Unitarias `PU-01` — Módulo [`KitNET/utils.py`](../KitNET/utils.py)

* **Identificador del Plan:** `PU-01-UTILS`
* **Archivo de Prueba:** [`tests/unit/test_utils.py`](../tests/unit/test_utils.py)
* **Documento Individual:** [`docs/planes_unitarios/PU_01_KitNET_utils.md`](planes_unitarios/PU_01_KitNET_utils.md)
* **Cobertura Alcanzada:** **100%** (35/35 sentencias).
* **Comando de Ejecución Aislada:** `python -m pytest tests/unit/test_utils.py -v`

### Matriz de Casos de Prueba (`PU-01`)

| ID Caso | Método / Función Bajo Prueba | Entrada de Prueba | Resultado Esperado / Invariante Matemático | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`UT-UTILS-001`** | `pdf()`, `invLogCDF()`, `rollmean(k=3)` | `pdf(0,0,1)`, simetría vectorizada en $\mu=5, \sigma=2$, `invLogCDF([0..3], 1, 0.5)` y secuencia `3, 6, 9, 12` en `rollmean(3)`. | Valor $\frac{1}{\sqrt{2\pi}}$, simetría exacta, coincidencia con `scipy.stats.norm.logcdf(-z)` y medias `1.0, 3.0, 6.0, 9.0` con aritmética modular del puntero. | ✅ PASS |
| **`UT-UTILS-002`** | `sigmoid`, `dsigmoid`, `tanh`, `dtanh`, `softmax`, `ReLU`, `dReLU` | Vectores 1D y matriz 2D `(2, 3)` incluyendo desplazamiento `+1000` en `softmax`. | Cotas `(0,1)`, identidad $y(1-y)$, imparidad de `tanh`, suma `1.0` invariante al desplazamiento en `softmax` y subgradiente escalón de `ReLU`. | ✅ PASS |

---

## 2. Plan de Pruebas Unitarias `PU-02` — Módulo [`KitNET/dA.py`](../KitNET/dA.py)

* **Identificador del Plan:** `PU-02-DA`
* **Archivo de Prueba:** [`tests/unit/test_da.py`](../tests/unit/test_da.py)
* **Documento Individual:** [`docs/planes_unitarios/PU_02_KitNET_dA.md`](planes_unitarios/PU_02_KitNET_dA.md)
* **Cobertura Alcanzada:** **100%** (65/65 sentencias).
* **Comando de Ejecución Aislada:** `python -m pytest tests/unit/test_da.py -v`

### Matriz de Casos de Prueba (`PU-02`)

| ID Caso | Método / Función Bajo Prueba | Entrada de Prueba | Resultado Esperado / Invariante Matemático | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`UT-DA-001`** | `dA.__init__()`, `get_corrupted_input()`, `train()` | `n_visible=10, hiddenRatio=0.75`, dos instancias `n_visible=6` y máscara con `corruption_level=0.3` y `1.0`. | `n_hidden == 8`, pesos atados `W_prime == W.T`, determinismo por semilla `1234`, máscara en `{0.0, 5.0}` y `AssertionError` con `1.0`. | ✅ PASS |
| **`UT-DA-002`** | `dA.train(x)`, `execute(x)`, `inGrace()` | Seguimiento min-max (`x1, x2`), compuerta `gracePeriod=3` y 150 iteraciones SGD en $\mathbb{R}^5$ vs patrón anómalo. | `norm_min`/`norm_max` exactos, `execute() == 0.0` durante gracia, $\text{RMSE}_{\text{final}} < \text{RMSE}_{\text{inicial}}$ y $\text{RMSE}_{\text{anomalía}} > \text{RMSE}_{\text{normal}}$. | ✅ PASS |

---

## 3. Plan de Pruebas Unitarias `PU-03` — Módulo [`KitNET/corClust.py`](../KitNET/corClust.py)

* **Identificador del Plan:** `PU-03-CORCLUST`
* **Archivo de Prueba:** [`tests/unit/test_corclust.py`](../tests/unit/test_corclust.py)
* **Documento Individual:** [`docs/planes_unitarios/PU_03_KitNET_corClust.md`](planes_unitarios/PU_03_KitNET_corClust.md)
* **Cobertura Alcanzada:** **100%** (37/37 sentencias).
* **Comando de Ejecución Aislada:** `python -m pytest tests/unit/test_corclust.py -v`

### Matriz de Casos de Prueba (`PU-03`)

| ID Caso | Método / Función Bajo Prueba | Entrada de Prueba | Resultado Esperado / Invariante Matemático | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`UT-CC-001`** | `corClust.__init__()`, `update()`, `corrDist()` | `n=8` inicial, vectores colineales en $\mathbb{R}^3$ y 10 vectores en $\mathbb{R}^4$ con 2 features constantes. | Estructuras en cero, simetría $C == C^\top$, protección `1e-100` ante varianza nula y ausencia total de `NaN`/`Inf`. | ✅ PASS |
| **`UT-CC-002`** | `corClust.cluster(maxClust)` | 40 muestras gaussianas en $\mathbb{R}^{15}$ (`maxClust=4`) y fronteras `maxClust=0` y `100` en $\mathbb{R}^6$. | Partición disjunta completa con $1 \le |v_i| \le 4$; clamping a 6 singletons (`0`) y 1 clúster único (`100`). | ✅ PASS |

---

## 4. Plan de Pruebas Unitarias `PU-04` — Módulo [`KitNET/KitNET.py`](../KitNET/KitNET.py)

* **Identificador del Plan:** `PU-04-KITNET`
* **Archivo de Prueba:** [`tests/unit/test_kitnet.py`](../tests/unit/test_kitnet.py)
* **Documento Individual:** [`docs/planes_unitarios/PU_04_KitNET_Orquestador.md`](planes_unitarios/PU_04_KitNET_Orquestador.md)
* **Cobertura Alcanzada:** **100%** (61/61 sentencias).
* **Comando de Ejecución Aislada:** `python -m pytest tests/unit/test_kitnet.py -v`

### Matriz de Casos de Prueba (`PU-04`)

| ID Caso | Método / Función Bajo Prueba | Entrada de Prueba | Resultado Esperado / Invariante Matemático | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`UT-KN-001`** | `KitNET.__init__()`, `execute()`, `process()` | `m=0, FM_grace=None`, `execute()` sin mapeo y `feature_map=[[0,1,2],[3,4],[5]]` (`FM_grace=0, AD_grace=5`). | Herencia `FM_grace=500`, `m=1`, `RuntimeError` sin mapeo y ejecución con 3 autoencoders tras 6 pasos de entrenamiento. | ✅ PASS |
| **`UT-KN-002`** | `KitNET.process(x)` (Ciclo completo) | `n=12, m=4, FM_grace=10, AD_grace=15` | Recorre exactamente `11` pasos en fase FM (instanciando `v`), `15` pasos en fase AD (`0.0`) y emite $\text{RMSE} > 0$ desde el paso `27`. | ✅ PASS |

---

## 5. Plan de Pruebas Unitarias `PU-05` — Módulo [`AfterImage.py`](../AfterImage.py)

* **Identificador del Plan:** `PU-05-AFTERIMAGE`
* **Archivo de Prueba:** [`tests/unit/test_afterimage.py`](../tests/unit/test_afterimage.py)
* **Documento Individual:** [`docs/planes_unitarios/PU_05_AfterImage.md`](planes_unitarios/PU_05_AfterImage.md)
* **Cobertura Alcanzada:** **98%** (284/291 sentencias).
* **Comando de Ejecución Aislada:** `python -m pytest tests/unit/test_afterimage.py -v`

### Matriz de Casos de Prueba (`PU-05`)

| ID Caso | Método / Función Bajo Prueba | Entrada de Prueba | Resultado Esperado / Invariante Matemático | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`UT-AI-001`** | `incStat`, `incStat_cov` | `Lambda=1.0`, `isTypeDiff=True`, magnitud `(3,4)`, encabezados 1D/2D y 7 actualizaciones acopladas `A`/`B`. | Factor $\gamma=0.5$, peso $w=1.5$, jitter $\Delta t=2.0$, magnitud `5.0`, `get_stats1..4` sin `NaN` y encabezados `ver=1..5`. | ✅ PASS |
| **`UT-AI-002`** | `incStatDB` (`register`, `get_*`, `cleanOutOldRecords`) | `limit=2` con 3 flujos, claves ausentes, flujos 1D/2D/nD y poda en `t=20.0` (`cutoffWeight=0.01`). | Lanza `LookupError` al 3er flujo, retorna `NaN`/`[]` en ausentes, resuelve vector 7D/nD y elimina los 2 registros caducados. | ✅ PASS |

---

## 6. Plan de Pruebas Unitarias `PU-06` — Módulo [`netStat.py`](../netStat.py)

* **Identificador del Plan:** `PU-06-NETSTAT`
* **Archivo de Prueba:** [`tests/unit/test_netstat.py`](../tests/unit/test_netstat.py)
* **Documento Individual:** [`docs/planes_unitarios/PU_06_netStat.md`](planes_unitarios/PU_06_netStat.md)
* **Cobertura Alcanzada:** **100%** (59/59 sentencias).
* **Comando de Ejecución Aislada:** `python -m pytest tests/unit/test_netstat.py -v`

### Matriz de Casos de Prueba (`PU-06`)

| ID Caso | Método / Función Bajo Prueba | Entrada de Prueba | Resultado Esperado / Invariante Matemático | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`UT-NS-001`** | `netStat.__init__()`, `getNetStatHeaders()`, `findDirection()` | `Lambdas` default vs `[1.0, 0.1]`, e IPv4 (`IPtype=0`), IPv6 (`IPtype=1`) y L2 (`IPtype=np.nan`). | Genera 100 (default) y 40 (custom) encabezados; extrae subred `/24` IPv4, mitad IPv6 y direcciones MAC completas en L2. | ✅ PASS |
| **`UT-NS-002`** | `netStat.updateGetStats()` | Tráfico TCP bidireccional y trama ARP (`srcProtocol="arp"`). | Retorna `np.ndarray` de forma `(100,)` finito sin `NaN` e indexa `HT_Hp` mediante `srcMAC` en la rama ARP. | ✅ PASS |

---

## 7. Plan de Pruebas Unitarias `PU-07` — Módulo [`FeatureExtractor.py`](../FeatureExtractor.py)

* **Identificador del Plan:** `PU-07-FE`
* **Archivo de Prueba:** [`tests/unit/test_feature_extractor.py`](../tests/unit/test_feature_extractor.py)
* **Documento Individual:** [`docs/planes_unitarios/PU_07_FeatureExtractor.md`](planes_unitarios/PU_07_FeatureExtractor.md)
* **Cobertura Alcanzada:** **83%** (139/167 sentencias).
* **Comando de Ejecución Aislada:** `python -m pytest tests/unit/test_feature_extractor.py -v`

### Matriz de Casos de Prueba (`PU-07`)

| ID Caso | Método / Función Bajo Prueba | Entrada de Prueba | Resultado Esperado / Invariante Matemático | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`UT-FE-001`** | `FE.__init__()`, `__prep__()`, `get_next_vector()` (TSV) | Ruta inexistente, extensión `.txt`, `.tsv` de 6 protocolos y truncamiento con `limit=2`. | Lanza `Exception` en entradas inválidas; extrae 6 vectores `(100,)` cerrando `tsvinf`; trunca exactamente a 2 vectores con `limit=2`. | ✅ PASS |
| **`UT-FE-002`** | `FE.get_next_vector()` (Scapy `.pcap`) | Archivo `.pcap` con 5 tramas (TCP, UDP, ARP, ICMP, L2 Ether) con `_get_tshark_path` mockeado a `""`. | Selecciona `parse_type == "scapy"`, extrae 5 vectores `(100,)` válidos y retorna `[]` al finalizar. | ✅ PASS |

---

## 8. Plan de Pruebas Unitarias `PU-08` — Módulo [`Kitsune.py`](../Kitsune.py)

* **Identificador del Plan:** `PU-08-KITSUNE`
* **Archivo de Prueba:** [`tests/unit/test_kitsune.py`](../tests/unit/test_kitsune.py)
* **Documento Individual:** [`docs/planes_unitarios/PU_08_Kitsune_Facade.md`](planes_unitarios/PU_08_Kitsune_Facade.md)
* **Cobertura Alcanzada:** **100%** (11/11 sentencias).
* **Comando de Ejecución Aislada:** `python -m pytest tests/unit/test_kitsune.py -v`

### Matriz de Casos de Prueba (`PU-08`)

| ID Caso | Método / Función Bajo Prueba | Entrada de Prueba | Resultado Esperado / Invariante Matemático | Estado |
| :--- | :--- | :--- | :--- | :---: |
| **`UT-KIT-001`** | `Kitsune.__init__()`, `proc_next_packet()` | Archivo `.tsv` de 15 paquetes con `limit=15, max_autoencoder_size=8, FM_grace=4, AD_grace=5, lr=0.05, hr=0.75`. | Verifica cableado (`FE=100`, `AnomDetector` configurado); primeros 10 paquetes retornan `0.0`, últimos 5 retornan $\text{RMSE} > 0.0$ y EOF retorna `-1`. | ✅ PASS |

---

## 9. Resumen Consolidado de Ejecución y Cobertura Unitaria

| Plan Unitario | Módulo Bajo Prueba | Archivo de Test | Casos Ejecutados | Aprobados | Cobertura de Líneas |
| :--- | :--- | :--- | :---: | :---: | :---: |
| **`PU-01`** | `KitNET/utils.py` | `tests/unit/test_utils.py` | 2 | 2 (100%) | **100%** |
| **`PU-02`** | `KitNET/dA.py` | `tests/unit/test_da.py` | 2 | 2 (100%) | **100%** |
| **`PU-03`** | `KitNET/corClust.py` | `tests/unit/test_corclust.py` | 2 | 2 (100%) | **100%** |
| **`PU-04`** | `KitNET/KitNET.py` | `tests/unit/test_kitnet.py` | 2 | 2 (100%) | **100%** |
| **`PU-05`** | `AfterImage.py` | `tests/unit/test_afterimage.py` | 2 | 2 (100%) | **98%** |
| **`PU-06`** | `netStat.py` | `tests/unit/test_netstat.py` | 2 | 2 (100%) | **100%** |
| **`PU-07`** | `FeatureExtractor.py` | `tests/unit/test_feature_extractor.py` | 2 | 2 (100%) | **83%** |
| **`PU-08`** | `Kitsune.py` | `tests/unit/test_kitsune.py` | 1 | 1 (100%) | **100%** |
| **TOTAL** | **8 Módulos Core** | **8 Suites Unitarias** | **15** | **15 (100%)** | **95.19%** |
