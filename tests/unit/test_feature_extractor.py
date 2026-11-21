"""Plan de Pruebas Unitarias PU-07: Modulo FeatureExtractor.py.

Evalua la clase FE para validacion de archivos, parseo TSV multiprotocolo,
truncamiento por limite de paquetes y conmutacion fallback a Scapy sobre .pcap.
"""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import numpy as np
import pytest
from scapy.layers.inet import ICMP, IP, TCP, UDP
from scapy.layers.l2 import ARP, Ether
from scapy.utils import wrpcap

from FeatureExtractor import FE


def _make_tsv_row(
    time_epoch: str = "1500000000.0",
    frame_len: str = "60",
    eth_src: str = "00:11:22:33:44:55",
    eth_dst: str = "66:77:88:99:aa:bb",
    ip_src: str = "",
    ip_dst: str = "",
    tcp_sport: str = "",
    tcp_dport: str = "",
    udp_sport: str = "",
    udp_dport: str = "",
    icmp_type: str = "",
    icmp_code: str = "",
    arp_opcode: str = "",
    arp_src_mac: str = "",
    arp_src_ip: str = "",
    arp_dst_mac: str = "",
    arp_dst_ip: str = "",
    ipv6_src: str = "",
    ipv6_dst: str = "",
) -> list[str]:
    """Construye una fila TSV de 19 columnas compatible con tshark."""
    return [
        time_epoch, frame_len, eth_src, eth_dst, ip_src, ip_dst,
        tcp_sport, tcp_dport, udp_sport, udp_dport, icmp_type, icmp_code,
        arp_opcode, arp_src_mac, arp_src_ip, arp_dst_mac, arp_dst_ip,
        ipv6_src, ipv6_dst,
    ]


@pytest.mark.unit
class TestFeatureExtractor:
    """Suite consolidada de pruebas unitarias para FeatureExtractor.py (2 casos)."""

    def test_ut_fe_001_validation_tsv_parsing_and_limit(
        self, tmp_path: Path, synthetic_tsv_factory: Callable[[list[list[str]], str], Path]
    ) -> None:
        """UT-FE-001: Verifica excepciones de entrada, parseo TSV (6 protocolos) y truncamiento por limit."""
        # 1. Archivo inexistente y extension invalida
        with pytest.raises(Exception):
            FE(str(tmp_path / "non_existent_capture.pcap"))
        bad_ext_file = tmp_path / "invalid.txt"
        bad_ext_file.write_text("dummy content", encoding="utf-8")
        with pytest.raises(Exception):
            FE(str(bad_ext_file))

        # 2. Parseo TSV de los 6 protocolos (IPv4/TCP, IPv4/UDP, IPv6/TCP, ARP, ICMP, L2 MAC)
        rows = [
            _make_tsv_row(time_epoch="100.0", frame_len="74", ip_src="192.168.1.10", ip_dst="192.168.1.20", tcp_sport="50000", tcp_dport="80"),
            _make_tsv_row(time_epoch="100.1", frame_len="64", ip_src="192.168.1.10", ip_dst="8.8.8.8", udp_sport="53000", udp_dport="53"),
            _make_tsv_row(time_epoch="100.2", frame_len="86", ipv6_src="fe80::1", ipv6_dst="fe80::2", tcp_sport="443", tcp_dport="55000"),
            _make_tsv_row(
                time_epoch="100.3", frame_len="42", arp_opcode="1",
                arp_src_mac="00:11:22:33:44:55", arp_src_ip="192.168.1.10",
                arp_dst_mac="ff:ff:ff:ff:ff:ff", arp_dst_ip="192.168.1.1",
            ),
            _make_tsv_row(time_epoch="100.4", frame_len="98", ip_src="192.168.1.10", ip_dst="192.168.1.1", icmp_type="8", icmp_code="0"),
            _make_tsv_row(time_epoch="100.5", frame_len="60", eth_src="aa:bb:cc:00:11:22", eth_dst="dd:ee:ff:33:44:55"),
        ]
        tsv_path = synthetic_tsv_factory(rows, "multi_proto.tsv")
        extractor = FE(str(tsv_path), limit=10)
        assert extractor.parse_type == "tsv" and extractor.get_num_features() == 100 and extractor.limit == 6

        for _ in range(6):
            vec = extractor.get_next_vector()
            assert isinstance(vec, np.ndarray) and vec.shape == (100,) and not np.any(np.isnan(vec))
        assert extractor.get_next_vector() == []
        assert extractor.tsvinf.closed is True

        # 3. Truncamiento por parametro limit
        limit_rows = [
            _make_tsv_row(time_epoch=str(1000.0 + i), ip_src="10.0.0.1", ip_dst="10.0.0.2", tcp_sport="80", tcp_dport="1024")
            for i in range(5)
        ]
        extractor_lim = FE(str(synthetic_tsv_factory(limit_rows, "limit_test.tsv")), limit=2)
        assert extractor_lim.limit == 2
        assert len(extractor_lim.get_next_vector()) == 100
        assert len(extractor_lim.get_next_vector()) == 100
        assert extractor_lim.get_next_vector() == []

    def test_ut_fe_002_scapy_pcap_fallback_parsing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """UT-FE-002: Verifica el parseo directo con Scapy cuando tshark no esta disponible."""
        pcap_path = tmp_path / "synthetic_scapy.pcap"
        packets = [
            Ether(src="00:11:22:33:44:01", dst="00:11:22:33:44:02") / IP(src="10.1.1.1", dst="10.1.1.2") / TCP(sport=12345, dport=80),
            Ether(src="00:11:22:33:44:02", dst="00:11:22:33:44:01") / IP(src="10.1.1.2", dst="10.1.1.1") / UDP(sport=53, dport=54321),
            Ether(src="00:11:22:33:44:01", dst="ff:ff:ff:ff:ff:ff") / ARP(psrc="10.1.1.1", pdst="10.1.1.254"),
            Ether(src="00:11:22:33:44:01", dst="00:11:22:33:44:02") / IP(src="10.1.1.1", dst="10.1.1.2") / ICMP(),
            Ether(src="00:11:22:33:44:01", dst="00:11:22:33:44:02"),
        ]
        wrpcap(str(pcap_path), packets)

        monkeypatch.setattr(FE, "_get_tshark_path", lambda self: "")
        extractor = FE(str(pcap_path))
        assert extractor.parse_type == "scapy" and extractor.limit == 5

        for _ in range(5):
            vec = extractor.get_next_vector()
            assert isinstance(vec, np.ndarray) and vec.shape == (100,) and not np.any(np.isnan(vec))
        assert extractor.get_next_vector() == []
