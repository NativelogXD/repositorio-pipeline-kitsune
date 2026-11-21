# Plan de Pruebas Unitarias Específico `PU-07`: Módulo `FeatureExtractor.py`

## 1. Identificación y Metadatos
* **ID del Plan:** `PU-07-FE`
* **Módulo Bajo Prueba:** [`FeatureExtractor.py`](../../FeatureExtractor.py) (`FE`)
* **Suite de Prueba:** [`tests/unit/test_feature_extractor.py`](../../tests/unit/test_feature_extractor.py)
* **Etapa del Pipeline CI:** `Stage 2 - Pruebas Unitarias (Pytest + Coverage)`
* **Casos Consolidados:** **2 pruebas** (`UT-FE-001` a `UT-FE-002`)
* **Cobertura Alcanzada:** **83%** (139/167 líneas ejecutadas)

## 2. Intuición Técnica y Alcance
La clase `FE` transforma tramas crudas desde archivos `.tsv` o `.pcap` en llamadas normalizadas a `netStat.updateGetStats()`. El plan unitario verifica la validación de entradas, todas las ramas de protocolo L2/L3/L4, el truncamiento por `limit` y el mecanismo de fallback a `Scapy`.

## 3. Especificación de Casos de Prueba Unitarios

| ID Caso | Método Bajo Prueba | Descripción y Datos de Entrada | Oráculo / Resultado Esperado |
| :--- | :--- | :--- | :--- |
| **`UT-FE-001`** | `FE.__init__()`, `__prep__()`, `get_next_vector()` (TSV) | Ruta inexistente, extensión `.txt`, archivo `.tsv` de 6 protocolos (TCP, UDP, IPv6, ARP, ICMP, L2) y truncamiento con `limit=2`. | Lanza `Exception` en entradas inválidas; extrae 6 vectores `(100,)` cerrando `tsvinf`; trunca exactamente a 2 paquetes con `limit=2`. |
| **`UT-FE-002`** | `FE.get_next_vector()` (Scapy) | Archivo `.pcap` sintético de 5 tramas (TCP, UDP, ARP, ICMP, L2 Ether) con `_get_tshark_path` mockeado a `""`. | Activa `parse_type == "scapy"`, extrae los 5 vectores `(100,)` y retorna `[]` al concluir. |

## 4. Comando de Verificación
```powershell
python -m pytest tests/unit/test_feature_extractor.py --cov=FeatureExtractor --cov-report=term-missing
```
