"""Plan de Pruebas Unitarias PU-08: Modulo Kitsune.py.

Evalua la fachada principal Kitsune verificando el cableado FE <-> KitNET y el flujo
de proc_next_packet() a traves de las fases FM, AD, ejecucion y centinela EOF (-1).
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np
import pytest

from Kitsune import Kitsune


@pytest.mark.unit
class TestKitsuneFacade:
    """Suite consolidada de pruebas unitarias para la fachada principal Kitsune (1 caso)."""

    def test_ut_kit_001_init_and_full_packet_lifecycle_eof(
        self, synthetic_tsv_factory: Callable[[list[list[str]], str], Path]
    ) -> None:
        """UT-KIT-001: Verifica inicializacion FE+KitNET, entrenamiento (0.0), ejecucion (>0) y EOF (-1)."""
        rows: list[list[str]] = []
        for idx in range(15):
            rows.append([
                f"{1000.0 + idx * 0.2:.1f}",
                str(60 + (idx % 5) * 10),
                "00:11:22:33:44:55",
                "66:77:88:99:aa:bb",
                "192.168.1.10",
                "192.168.1.20",
                str(40000 + (idx % 3)),
                "443",
                "", "", "", "", "", "", "", "", "", "", "",
            ])

        tsv_path = synthetic_tsv_factory(rows, "lifecycle.tsv")
        fm_grace, ad_grace = 4, 5
        kitsune = Kitsune(
            file_path=str(tsv_path),
            limit=15,
            max_autoencoder_size=8,
            FM_grace_period=fm_grace,
            AD_grace_period=ad_grace,
            learning_rate=0.05,
            hidden_ratio=0.75,
        )

        # Verificacion de cableado inicial FE <-> KitNET
        assert kitsune.FE.get_num_features() == 100
        assert kitsune.AnomDetector.n == 100
        assert kitsune.AnomDetector.m == 8
        assert kitsune.AnomDetector.FM_grace_period == fm_grace
        assert kitsune.AnomDetector.AD_grace_period == ad_grace

        # Ejecucion completa de paquetes hasta EOF (-1)
        scores: list[float] = []
        while True:
            rmse = kitsune.proc_next_packet()
            if rmse == -1:
                break
            scores.append(float(rmse))

        assert len(scores) == 15
        assert all(score == 0.0 for score in scores[: fm_grace + ad_grace + 1])
        assert all(score > 0.0 and not np.isnan(score) for score in scores[fm_grace + ad_grace + 1 :])
        assert kitsune.proc_next_packet() == -1
