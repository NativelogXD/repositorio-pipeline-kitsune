"""Plan de Pruebas Unitarias PU-06: Modulo netStat.py.

Evalua inicializacion con Lambdas, resolucion de subredes en findDirection y
extraccion del vector de 100 caracteristicas multiperspectiva en trafico TCP/UDP y ARP.
"""

from __future__ import annotations

import numpy as np
import pytest

from netStat import netStat


@pytest.mark.unit
class TestNetStat:
    """Suite consolidada de pruebas unitarias para netStat.py (2 casos)."""

    def test_ut_ns_001_init_lambdas_and_find_direction(self) -> None:
        """UT-NS-001: Verifica Lambdas por defecto/personalizadas (100/40 headers) y findDirection (IPv4/IPv6/L2)."""
        ns_default = netStat()
        assert ns_default.Lambdas == [5, 3, 1, 0.1, 0.01]
        assert ns_default.HostLimit == 255
        assert len(ns_default.getNetStatHeaders()) == 100

        ns_custom = netStat(Lambdas=[1.0, 0.1], HostLimit=50, HostSimplexLimit=100)
        assert ns_custom.Lambdas == [1.0, 0.1]
        assert len(ns_custom.getNetStatHeaders()) == 40

        src_v4, dst_v4 = ns_default.findDirection(0, "192.168.1.15", "10.0.0.254", "aa:bb:cc:dd:ee:01", "aa:bb:cc:dd:ee:02")
        assert src_v4 == "192.168.1" and dst_v4 == "10.0.0"

        src_v6, dst_v6 = ns_default.findDirection(
            1, "fe80::1ff:fe23:4567:890a", "2001:db8::8a2e:370:7334", "aa:bb:cc:dd:ee:01", "aa:bb:cc:dd:ee:02"
        )
        assert len(src_v6) == round(len("fe80::1ff:fe23:4567:890a") / 2)
        assert len(dst_v6) == round(len("2001:db8::8a2e:370:7334") / 2)

        src_l2, dst_l2 = ns_default.findDirection(np.nan, "", "", "aa:bb:cc:dd:ee:01", "aa:bb:cc:dd:ee:02")
        assert src_l2 == "aa:bb:cc:dd:ee:01" and dst_l2 == "aa:bb:cc:dd:ee:02"

    def test_ut_ns_002_update_get_stats_tcp_udp_and_arp(self) -> None:
        """UT-NS-002: Verifica vector finito de 100 dimensiones en IP/TCP y rama ARP por MAC en HT_Hp."""
        ns = netStat()
        vec1 = ns.updateGetStats(0, "00:11:22:33:44:55", "66:77:88:99:aa:bb", "192.168.1.10", "443", "192.168.1.20", "51234", 120, 1000.0)
        vec2 = ns.updateGetStats(0, "66:77:88:99:aa:bb", "00:11:22:33:44:55", "192.168.1.20", "51234", "192.168.1.10", "443", 240, 1000.5)
        assert vec1.shape == (100,) and vec2.shape == (100,)
        assert not np.any(np.isnan(vec1)) and not np.any(np.isnan(vec2))

        vec_arp = ns.updateGetStats(
            0, "00:aa:bb:cc:dd:01", "ff:ff:ff:ff:ff:ff", "192.168.1.1", "arp", "192.168.1.99", "arp", 42, 2000.0
        )
        assert vec_arp.shape == (100,) and not np.any(np.isnan(vec_arp))
        assert any(key.startswith("00:aa:bb:cc:dd:01_") for key in ns.HT_Hp.HT)
