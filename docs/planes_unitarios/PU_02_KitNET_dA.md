# Plan de Pruebas Unitarias Específico `PU-02`: Módulo `KitNET/dA.py`

## 1. Identificación y Metadatos
* **ID del Plan:** `PU-02-DA`
* **Módulo Bajo Prueba:** [`KitNET/dA.py`](../../KitNET/dA.py) (`dA_params` y `dA`)
* **Suite de Prueba:** [`tests/unit/test_da.py`](../../tests/unit/test_da.py)
* **Etapa del Pipeline CI:** `Stage 2 - Pruebas Unitarias (Pytest + Coverage)`
* **Casos Consolidados:** **2 pruebas** (`UT-DA-001` a `UT-DA-002`)
* **Cobertura Alcanzada:** **100%** (65/65 líneas ejecutadas)

## 2. Intuición Técnica y Alcance
La clase `dA` implementa un *Denoising Autoencoder* de tres capas con pesos atados ($W' = W^\top$) que opera de forma estrictamente *online*. Este plan verifica dimensionamiento `hiddenRatio`, determinismo (`RandomState(1234)`), corrupción binomial, seguimiento `norm_min`/`norm_max`, compuerta `inGrace()` y convergencia SGD.

## 3. Especificación de Casos de Prueba Unitarios

| ID Caso | Método Bajo Prueba | Descripción y Datos de Entrada | Oráculo / Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **`UT-DA-001`** | `dA.__init__()`, `get_corrupted_input()`, `train()` | `n_visible=10, hiddenRatio=0.75`, dos instancias `n_visible=6`, y máscara con `corruption_level=0.3` y `1.0`. | `n_hidden == 8`, pesos atados `W_prime == W.T`, pesos idénticos entre instancias, máscara en `{0.0, 5.0}` y `AssertionError` con `1.0`. |
| **`UT-DA-002`** | `train(x)`, `execute(x)`, `inGrace()` | Seguimiento min-max (`x1, x2`), compuerta `gracePeriod=3` y 150 iteraciones SGD en $\mathbb{R}^5$ vs vector anómalo. | Actualización exacta de `norm_min`/`norm_max`, `execute() == 0.0` en gracia, descenso de RMSE y $\text{RMSE}_{\text{anomalía}} > \text{RMSE}_{\text{normal}}$. |

## 4. Comando de Verificación
```powershell
python -m pytest tests/unit/test_da.py --cov=KitNET.dA --cov-report=term-missing
```
