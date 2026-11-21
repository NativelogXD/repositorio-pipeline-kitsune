# Plan de Pruebas Unitarias Específico `PU-08`: Módulo `Kitsune.py`

## 1. Identificación y Metadatos
* **ID del Plan:** `PU-08-KITSUNE`
* **Módulo Bajo Prueba:** [`Kitsune.py`](../../Kitsune.py) (`Kitsune`)
* **Suite de Prueba:** [`tests/unit/test_kitsune.py`](../../tests/unit/test_kitsune.py)
* **Etapa del Pipeline CI:** `Stage 2 - Pruebas Unitarias (Pytest + Coverage)`
* **Casos Consolidados:** **1 prueba** (`UT-KIT-001`)
* **Cobertura Alcanzada:** **100%** (11/11 líneas ejecutadas)

## 2. Intuición Técnica y Alcance
La clase `Kitsune` actúa como fachada principal del sistema, cableando `FE` con `KitNET`, conectando `FE.get_next_vector()` con `KitNET.process(x)` en cada llamada a `proc_next_packet()` y devolviendo `-1` al llegar al fin de archivo (EOF).

## 3. Especificación de Casos de Prueba Unitarios

| ID Caso | Método Bajo Prueba | Descripción y Datos de Entrada | Oráculo / Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **`UT-KIT-001`** | `Kitsune.__init__()`, `proc_next_packet()` | Archivo `.tsv` de 15 paquetes con `limit=15, max_autoencoder_size=8, FM_grace=4, AD_grace=5, lr=0.05, hr=0.75`. | Verifica `FE.get_num_features()==100` e hiperparámetros en `AnomDetector`; primeros 10 paquetes retornan `0.0`, últimos 5 retornan $\text{RMSE}>0.0$ y EOF retorna `-1`. |

## 4. Comando de Verificación
```powershell
python -m pytest tests/unit/test_kitsune.py --cov=Kitsune --cov-report=term-missing
```
