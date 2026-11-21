# Plan de Pruebas Unitarias Específico `PU-01`: Módulo `KitNET/utils.py`

## 1. Identificación y Metadatos
* **ID del Plan:** `PU-01-UTILS`
* **Módulo Bajo Prueba:** [`KitNET/utils.py`](../../KitNET/utils.py)
* **Suite de Prueba:** [`tests/unit/test_utils.py`](../../tests/unit/test_utils.py)
* **Etapa del Pipeline CI:** `Stage 2 - Pruebas Unitarias (Pytest + Coverage)`
* **Casos Consolidados:** **2 pruebas** (`UT-UTILS-001` a `UT-UTILS-002`)
* **Cobertura Alcanzada:** **100%** (35/35 líneas ejecutadas)

## 2. Intuición Técnica y Alcance
El módulo `KitNET/utils.py` provee los bloques matemáticos elementales de los autoencoders y del ajuste estadístico de anomalías:
1. **Funciones Estadísticas (`pdf`, `invLogCDF`):** Evalúan la densidad gaussiana $\mathcal{N}(\mu, \sigma^2)$ y la función de supervivencia logarítmica $\log(1 - \Phi(z))$.
2. **Ventana Deslizante Circular (`rollmean`):** Calcula la media móvil de tamaño $k$ usando un puntero circular.
3. **Funciones de Activación y Gradientes (`sigmoid`, `dsigmoid`, `tanh`, `dtanh`, `softmax`, `ReLU`, `dReLU`):** Operan vectorialmente sobre tensores de NumPy.

## 3. Especificación de Casos de Prueba Unitarios

| ID Caso | Función / Clase | Descripción y Datos de Entrada | Oráculo / Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **`UT-UTILS-001`** | `pdf()`, `invLogCDF()`, `rollmean(k=3)` | `pdf(0,0,1)`, simetría vectorizada en $\mu=5, \sigma=2$, `invLogCDF([0..3], 1, 0.5)` e inserción de `3, 6, 9, 12` en `rollmean(3)`. | Valor $\frac{1}{\sqrt{2\pi}}$, simetría exacta, igualdad con `norm.logcdf(-z)` y medias `1.0, 3.0, 6.0, 9.0` con puntero circular `0->1`. |
| **`UT-UTILS-002`** | `sigmoid`, `dsigmoid`, `tanh`, `dtanh`, `softmax`, `ReLU`, `dReLU` | Vectores 1D y matriz 2D `(2, 3)` incluyendo desplazamiento `+1000` en `softmax`. | Cotas `(0,1)`, identidad $y(1-y)$, imparidad de `tanh`, suma `1.0` invariante en `softmax` y subgradiente de `ReLU`. |

## 4. Comando de Verificación
```powershell
python -m pytest tests/unit/test_utils.py --cov=KitNET.utils --cov-report=term-missing
```
