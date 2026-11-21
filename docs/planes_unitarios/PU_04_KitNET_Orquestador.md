# Plan de Pruebas Unitarias Específico `PU-04`: Módulo `KitNET/KitNET.py`

## 1. Identificación y Metadatos
* **ID del Plan:** `PU-04-KITNET`
* **Módulo Bajo Prueba:** [`KitNET/KitNET.py`](../../KitNET/KitNET.py) (`KitNET`)
* **Suite de Prueba:** [`tests/unit/test_kitnet.py`](../../tests/unit/test_kitnet.py)
* **Etapa del Pipeline CI:** `Stage 2 - Pruebas Unitarias (Pytest + Coverage)`
* **Casos Consolidados:** **2 pruebas** (`UT-KN-001` a `UT-KN-002`)
* **Cobertura Alcanzada:** **100%** (61/61 líneas ejecutadas)

## 2. Intuición Técnica y Alcance
`KitNET` coordina la transición entre `FM train-mode`, `AD train-mode` y `AD execute-mode`, la herencia de `FM_grace_period`, la protección contra ejecución sin mapeo y la construcción de `ensembleLayer` + `outputLayer`.

## 3. Especificación de Casos de Prueba Unitarios

| ID Caso | Método Bajo Prueba | Descripción y Datos de Entrada | Oráculo / Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **`UT-KN-001`** | `KitNET.__init__()`, `execute()`, `process()` | `m=0, FM_grace=None`, llamada a `execute` sin mapeo, y `feature_map=[[0,1,2],[3,4],[5]]` con `FM_grace=0, AD_grace=5`. | Herencia `FM_grace=500`, `m=1`, `RuntimeError` sin mapeo y ejecución inmediata con 3 autoencoders tras 6 pasos AD. |
| **`UT-KN-002`** | `KitNET.process(x)` | Flujo completo con `n=12, m=4, FM_grace=10, AD_grace=15`. | Transición exacta en paquete 11 (creación de `v` y AD) y en paquete 27 (primera ejecución con $\text{RMSE} > 0$). |

## 4. Comando de Verificación
```powershell
python -m pytest tests/unit/test_kitnet.py --cov=KitNET.KitNET --cov-report=term-missing
```
