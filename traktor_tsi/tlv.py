"""TLV (Tag-Length-Value) parsing and building for Traktor TSI binary format.

Binary format: each chunk = 4-byte ASCII tag + 4-byte uint32 BE length + payload.
Known tags: DIOM, DIOI, DEVS, DEVI, DDAT, DDIF, DDIV, DDIC, DDPT,
            DDDC, DDCI, DDCO, DCDT, DDCB, CMAS, CMAI, CMAD, DCBM, DVST.
"""

import struct


def parse_tlv(data: bytes, offset: int = 0) -> list[tuple[str, bytes, int]]:
    """Parse TLV chunks from binary data.

    Args:
        data: Binary data containing TLV chunks.
        offset: Starting offset in data.

    Returns:
        List of (tag, payload, start_offset) tuples.
    """
    chunks = []
    while offset + 8 <= len(data):
        tag = data[offset:offset + 4].decode('ascii', errors='replace')
        length = struct.unpack('>I', data[offset + 4:offset + 8])[0]
        payload = data[offset + 8:offset + 8 + length]
        chunks.append((tag, payload, offset))
        offset += 8 + length
    return chunks


def build_tlv(tag: str, payload: bytes) -> bytes:
    """Build a TLV chunk.

    Args:
        tag: 4-character ASCII tag.
        payload: Raw payload bytes.

    Returns:
        Complete TLV chunk bytes.
    """
    return tag.encode('ascii') + struct.pack('>I', len(payload)) + payload


def find_chunk(chunks: list[tuple[str, bytes, int]], tag: str) -> bytes:
    """Find first chunk with given tag and return its payload.

    Raises:
        KeyError: If tag not found.
    """
    for t, payload, _ in chunks:
        if t == tag:
            return payload
    raise KeyError(f"TLV tag {tag!r} not found")
