"""UTF-16-BE string encoding/decoding for Traktor TSI binary format.

String format: uint32 BE char count + UTF-16-BE encoded characters.
"""

import struct


def decode_utf16be_str(data: bytes, offset: int) -> tuple[str, int]:
    """Decode a length-prefixed UTF-16-BE string.

    Args:
        data: Binary data.
        offset: Starting offset.

    Returns:
        (decoded_string, next_offset) tuple.
    """
    char_count = struct.unpack('>I', data[offset:offset + 4])[0]
    raw = data[offset + 4:offset + 4 + char_count * 2]
    s = raw.decode('utf-16-be')
    return s, offset + 4 + char_count * 2


def encode_utf16be_str(s: str) -> bytes:
    """Encode a string as length-prefixed UTF-16-BE.

    Args:
        s: String to encode.

    Returns:
        uint32 char count + UTF-16-BE bytes.
    """
    return struct.pack('>I', len(s)) + s.encode('utf-16-be')
