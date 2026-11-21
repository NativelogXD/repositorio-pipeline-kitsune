# Plan de Pruebas Unitarias Específico `PU-06`: Módulo `netStat.py`

## 1. Identificación y Metadatos
* **ID del Plan:** `PU-06-NETSTAT`
* **Módulo Bajo Prueba:** [`netStat.py`](../../netStat.py) (`netStat`)
* **Suite de Prueba:** [`tests/unit/test_netstat.py`](../../tests/unit/test_netstat.py)
* **Etapa del Pipeline CI:** `Stage 2 - Pruebas Unitarias (Pytest + Coverage)`
* **Casos Consolidados:** **2 pruebas** (`UT-NS-001` a `UT-NS-002`)
* **Cobertura Alcanzada:** **100%** (59/59 líneas ejecutadas)

## 2. Intuición Técnica y Alcance
`netStat` coordina las cuatro vistas contextuales de cada paquete (`HT_MI`, `HT_H`, `HT_jit`, `HT_Hp`) a través de las 5 escalas temporales $\Lambda = [5, 3, 1, 0.1, 0.01]$, produciendo el vector de características $x \in \mathbb{R}^{100}$.

## 3. Especificación de Casos de Prueba Unitarios

| ID Caso | Método Bajo Prueba | Descripción y Datos de Entrada | Oráculo / Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **`UT-NS-001`** | `netStat.__init__()`, `getNetStatHeaders()`, `findDirection()` | `Lambdas` default vs `[1.0, 0.1]`, y resolución en `IPtype=0` (IPv4), `IPtype=1` (IPv6) y `np.nan` (L2 MAC). | 100 encabezados (default) y 40 (custom); extrae prefijo `/24` IPv4, mitad IPv6 y direcciones MAC en L2. |
| **`UT-NS-002`** | `netStat.updateGetStats()` | Tráfico bidireccional TCP (`192.168.1.10:443 <-> .20:51234`) y trama `arp`. | Vectores `np.ndarray` `(100,)` sin `NaN` e indexación de `HT_Hp` por dirección MAC en la rama ARP. |

## 4. Comando de Verificación
```powershell
python -m pytest tests/unit/test_netstat.py --cov=netStat --cov-report=term-missing
```
