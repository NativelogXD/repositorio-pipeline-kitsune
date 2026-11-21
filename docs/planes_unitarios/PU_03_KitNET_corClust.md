# Plan de Pruebas Unitarias Específico `PU-03`: Módulo `KitNET/corClust.py`

## 1. Identificación y Metadatos
* **ID del Plan:** `PU-03-CORCLUST`
* **Módulo Bajo Prueba:** [`KitNET/corClust.py`](../../KitNET/corClust.py) (`corClust`)
* **Suite de Prueba:** [`tests/unit/test_corclust.py`](../../tests/unit/test_corclust.py)
* **Etapa del Pipeline CI:** `Stage 2 - Pruebas Unitarias (Pytest + Coverage)`
* **Casos Consolidados:** **2 pruebas** (`UT-CC-001` a `UT-CC-002`)
* **Cobertura Alcanzada:** **100%** (37/37 líneas ejecutadas)

## 2. Intuición Técnica y Alcance
La clase `corClust` calcula de forma incremental la correlación entre las $n$ características y construye un árbol jerárquico aglomerativo podado para garantizar que ningún autoencoder reciba más de `maxClust` entradas.

## 3. Especificación de Casos de Prueba Unitarios

| ID Caso | Método Bajo Prueba | Descripción y Datos de Entrada | Oráculo / Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **`UT-CC-001`** | `corClust.__init__()`, `update()`, `corrDist()` | Inicialización `n=8`, vectores colineales en $\mathbb{R}^3$ y 10 muestras en $\mathbb{R}^4$ con 2 features constantes. | Estructuras en cero, simetría $C = C^\top$, sustitución `1e-100` ante varianza cero y ausencia total de `NaN`/`Inf`. |
| **`UT-CC-002`** | `corClust.cluster(maxClust)` | 40 vectores gaussianos en $\mathbb{R}^{15}$ (`maxClust=4`) y pruebas de frontera en $\mathbb{R}^6$ (`maxClust=0` y `100`). | Grupos $1 \le |v_i| \le 4$ cubriendo todos los índices; clamping a 6 singletons (`0`) y 1 clúster completo (`100`). |

## 4. Comando de Verificación
```powershell
python -m pytest tests/unit/test_corclust.py --cov=KitNET.corClust --cov-report=term-missing
```
