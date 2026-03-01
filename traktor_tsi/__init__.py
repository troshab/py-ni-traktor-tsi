"""
traktor_tsi - Python library for reading and writing Native Instruments Traktor Pro TSI mapping files.

TSI files contain MIDI controller mappings stored as Base64-encoded binary TLV data inside XML.
"""

from traktor_tsi.tlv import parse_tlv, build_tlv
from traktor_tsi.strings import decode_utf16be_str, encode_utf16be_str
from traktor_tsi.cmad import build_cmad_knob, build_cmad_button, build_cmad_output
from traktor_tsi.tsi import parse_tsi, write_tsi, rebuild_tsi, get_device_info, build_cmai, build_ddcb
from traktor_tsi.constants import *

try:
    from importlib.metadata import version as _pkg_version
    __version__ = _pkg_version("py-ni-traktor-tsi")
except Exception:
    __version__ = "0.0.0-dev"
