"""Tests for TSI binary structure builders."""

import struct

from traktor_tsi.tsi import build_cmai, build_ddcb
from traktor_tsi.tlv import parse_tlv, find_chunk
from traktor_tsi.cmad import build_cmad_button, build_cmad_knob, CMAD_SIZE


class TestBuildCmai:
    """Tests for build_cmai."""

    def test_header_fields(self):
        cmad = build_cmad_button()
        payload = build_cmai(midi_idx=5, mapping_type=0, cmd_id=259, cmad_payload=cmad)
        idx, mtype, cmd = struct.unpack('>III', payload[:12])
        assert idx == 5
        assert mtype == 0
        assert cmd == 259

    def test_cmad_embedded(self):
        """CMAI contains a CMAD TLV with the 120-byte payload."""
        cmad = build_cmad_button(target=3)
        payload = build_cmai(0, 0, 100, cmad)
        # After 12-byte header, expect CMAD TLV
        tag = payload[12:16].decode('ascii')
        length = struct.unpack('>I', payload[16:20])[0]
        assert tag == 'CMAD'
        assert length == CMAD_SIZE

    def test_output_entry(self):
        """mapping_type=1 for output entries."""
        cmad = build_cmad_button()
        payload = build_cmai(0, 1, 369, cmad)
        _, mtype, _ = struct.unpack('>III', payload[:12])
        assert mtype == 1


class TestBuildDdcb:
    """Tests for build_ddcb."""

    def test_single_entry(self):
        cmad = build_cmad_button()
        cmai = build_cmai(0, 0, 259, cmad)
        ddcb = build_ddcb([cmai], ['Left.HotCue 1'])

        # DDCB is a TLV
        chunks = parse_tlv(ddcb)
        ddcb_tag, ddcb_payload, _ = chunks[0]
        assert ddcb_tag == 'DDCB'

        # Inside: CMAS + DCBM
        inner = parse_tlv(ddcb_payload)
        tags = [t for t, _, _ in inner]
        assert 'CMAS' in tags
        assert 'DCBM' in tags

    def test_cmas_count(self):
        """CMAS starts with entry count."""
        entries = []
        names = []
        for i in range(5):
            cmad = build_cmad_button()
            entries.append(build_cmai(i, 0, 259, cmad))
            names.append(f'Control.{i}')

        ddcb = build_ddcb(entries, names)
        ddcb_payload = find_chunk(parse_tlv(ddcb), 'DDCB')
        cmas_payload = find_chunk(parse_tlv(ddcb_payload), 'CMAS')
        count = struct.unpack('>I', cmas_payload[:4])[0]
        assert count == 5

    def test_dcbm_count(self):
        """DCBM count matches entry count."""
        entries = []
        names = []
        for i in range(3):
            cmad = build_cmad_knob(interaction_mode=4)
            entries.append(build_cmai(i, 0, 251, cmad))
            names.append(f'Left.Loop Encoder Turn')

        ddcb = build_ddcb(entries, names)
        ddcb_payload = find_chunk(parse_tlv(ddcb), 'DDCB')
        dcbm_payload = find_chunk(parse_tlv(ddcb_payload), 'DCBM')
        count = struct.unpack('>I', dcbm_payload[:4])[0]
        assert count == 3

    def test_empty(self):
        """Zero entries should still produce valid DDCB."""
        ddcb = build_ddcb([], [])
        chunks = parse_tlv(ddcb)
        assert chunks[0][0] == 'DDCB'
