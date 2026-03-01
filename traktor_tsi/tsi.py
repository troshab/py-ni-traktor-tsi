"""TSI file I/O: parsing, rebuilding, and writing.

A TSI file is XML with a Base64-encoded binary blob in the
DeviceIO.Config.Controller (or .Keyboard) entry.
The binary uses a nested TLV structure.

Hierarchy:
    DIOM > DIOI, DEVS > [count] DEVI > name + DDAT >
        DDIF, DDIV, DDIC, DDPT, DDDC > (DDCI, DDCO), DDCB > (CMAS, DCBM), DVST
"""

import base64
import struct
import xml.etree.ElementTree as ET

from traktor_tsi.tlv import parse_tlv, build_tlv, find_chunk
from traktor_tsi.strings import decode_utf16be_str, encode_utf16be_str


# --- File I/O ----------------------------------------------------------------

def parse_tsi(filepath: str) -> bytes:
    """Read a TSI file and return the decoded binary blob.

    Args:
        filepath: Path to .tsi file.

    Returns:
        Raw binary data (decoded from Base64).
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    for entry in root.iter('Entry'):
        name = entry.get('Name', '')
        if name.startswith('DeviceIO.Config.'):
            return base64.b64decode(entry.get('Value'))
    raise ValueError(f"No DeviceIO.Config entry found in {filepath}")


def write_tsi(binary_data: bytes, output_path: str, template_path: str):
    """Write a TSI file using a template for XML structure.

    Args:
        binary_data: New binary blob to encode.
        output_path: Where to save the .tsi file.
        template_path: Existing .tsi to use as XML template.
    """
    tree = ET.parse(template_path)
    root = tree.getroot()
    for entry in root.iter('Entry'):
        name = entry.get('Name', '')
        if name.startswith('DeviceIO.Config.'):
            entry.set('Value', base64.b64encode(binary_data).decode('ascii'))
            break

    tree.write(output_path, encoding='UTF-8', xml_declaration=True)

    # Fix XML declaration to match Traktor's format
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    content = content.replace(
        "<?xml version='1.0' encoding='UTF-8'?>",
        '<?xml version="1.0" encoding="UTF-8" standalone="no" ?>'
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)


# --- Binary structure navigation ---------------------------------------------

def get_device_info(binary: bytes) -> dict:
    """Extract device info from a TSI binary blob.

    Returns:
        Dict with 'name', 'comment', 'version', 'port', 'input_count',
        'output_count', 'mapping_count'.
    """
    diom_payload = find_chunk(parse_tlv(binary), 'DIOM')
    devs_payload = find_chunk(parse_tlv(diom_payload), 'DEVS')
    devi_chunks = parse_tlv(devs_payload, offset=4)
    devi_payload = find_chunk(devi_chunks, 'DEVI')

    name, rest_off = decode_utf16be_str(devi_payload, 0)
    ddat_payload = find_chunk(parse_tlv(devi_payload, offset=rest_off), 'DDAT')

    ddat_chunks = parse_tlv(ddat_payload)
    info = {'name': name}

    for tag, payload, _ in ddat_chunks:
        if tag == 'DDIC':
            info['comment'], _ = decode_utf16be_str(payload, 0)
        elif tag == 'DDIV':
            info['version'], _ = decode_utf16be_str(payload, 0)
        elif tag == 'DDDC':
            for t2, p2, _ in parse_tlv(payload):
                if t2 == 'DDCI':
                    info['input_count'] = struct.unpack('>I', p2[:4])[0]
                elif t2 == 'DDCO':
                    info['output_count'] = struct.unpack('>I', p2[:4])[0]
        elif tag == 'DDCB':
            cmas_payload = find_chunk(parse_tlv(payload), 'CMAS')
            info['mapping_count'] = struct.unpack('>I', cmas_payload[:4])[0]

    return info


# --- Mapping builders --------------------------------------------------------

def build_cmai(midi_idx: int, mapping_type: int, cmd_id: int, cmad_payload: bytes) -> bytes:
    """Build a CMAI entry payload (without the CMAI TLV wrapper).

    Args:
        midi_idx: MIDI control index (used in DCBM binding).
        mapping_type: 0=Input, 1=Output.
        cmd_id: Traktor command ID.
        cmad_payload: 120-byte CMAD payload.

    Returns:
        CMAI inner payload bytes.
    """
    header = struct.pack('>III', midi_idx, mapping_type, cmd_id)
    cmad_tlv = build_tlv('CMAD', cmad_payload)
    return header + cmad_tlv


def build_ddcb(cmai_payloads: list[bytes], ctrl_names: list[str]) -> bytes:
    """Build complete DDCB TLV from mapping entries.

    Args:
        cmai_payloads: List of raw CMAI inner payloads.
        ctrl_names: Parallel list of MIDI control names for DCBM bindings.

    Returns:
        Complete DDCB TLV bytes (tag + length + payload).
    """
    count = len(cmai_payloads)

    # CMAS: count + CMAI TLVs
    cmas_inner = struct.pack('>I', count)
    for raw in cmai_payloads:
        cmas_inner += build_tlv('CMAI', raw)
    cmas_tlv = build_tlv('CMAS', cmas_inner)

    # DCBM (outer): count + DCBM entry TLVs
    dcbm_inner = struct.pack('>I', count)
    for i, name in enumerate(ctrl_names):
        entry = struct.pack('>I', i) + encode_utf16be_str(name)
        dcbm_inner += build_tlv('DCBM', entry)
    dcbm_outer = build_tlv('DCBM', dcbm_inner)

    return build_tlv('DDCB', cmas_tlv + dcbm_outer)


# --- TSI rebuilder -----------------------------------------------------------

def rebuild_tsi(
    original_binary: bytes,
    new_ddcb: bytes,
    new_comment: str | None = None,
) -> bytes:
    """Rebuild TSI binary with new DDCB section, recalculating all TLV lengths.

    Args:
        original_binary: Original TSI binary blob.
        new_ddcb: New DDCB TLV bytes (from build_ddcb).
        new_comment: Optional new DDIC comment string.

    Returns:
        New complete TSI binary blob.
    """
    diom_payload = find_chunk(parse_tlv(original_binary), 'DIOM')

    new_diom = b''
    for tag, payload, _ in parse_tlv(diom_payload):
        if tag == 'DEVS':
            new_diom += build_tlv('DEVS', _rebuild_devs(payload, new_ddcb, new_comment))
        else:
            new_diom += build_tlv(tag, payload)

    return build_tlv('DIOM', new_diom)


def _rebuild_devs(payload: bytes, new_ddcb: bytes, comment: str | None) -> bytes:
    count = struct.unpack('>I', payload[:4])[0]
    result = struct.pack('>I', count)
    for tag, p, _ in parse_tlv(payload, offset=4):
        if tag == 'DEVI':
            result += build_tlv('DEVI', _rebuild_devi(p, new_ddcb, comment))
        else:
            result += build_tlv(tag, p)
    return result


def _rebuild_devi(payload: bytes, new_ddcb: bytes, comment: str | None) -> bytes:
    name, rest_off = decode_utf16be_str(payload, 0)
    name_bytes = encode_utf16be_str(name)
    rest = b''
    for tag, p, _ in parse_tlv(payload, offset=rest_off):
        if tag == 'DDAT':
            rest += build_tlv('DDAT', _rebuild_ddat(p, new_ddcb, comment))
        else:
            rest += build_tlv(tag, p)
    return name_bytes + rest


def _rebuild_ddat(payload: bytes, new_ddcb: bytes, comment: str | None) -> bytes:
    result = b''
    for tag, p, _ in parse_tlv(payload):
        if tag == 'DDCB':
            result += new_ddcb
        elif tag == 'DDIC' and comment is not None:
            result += build_tlv('DDIC', encode_utf16be_str(comment))
        else:
            result += build_tlv(tag, p)
    return result
