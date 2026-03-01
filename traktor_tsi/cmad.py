"""CMAD (Command Mapping Assignment Data) builders.

CMAD is a 120-byte payload (30 x uint32 BE) inside each CMAI entry.
Field layout reverse-engineered from real TSI files and cmdr-editor source.

Field map (offset in bytes):
    [0]   DeviceType        - always 4
    [4]   ControlType       - 0=Button, 1=FaderOrKnob, 0xFFFF=Output
    [8]   InteractionMode   - 1=Toggle, 2=Direct, 3=Absolute, 8=OutputMode
    [12]  Target            - deck/slot/FX unit assignment (0-15)
    [16]  AutoRepeat        - 0
    [20]  Invert            - 0 or 1
    [24]  Reserved
    [28]  MaxInput          - float32: 5.0 (0x40A00000)
    [32]  Reserved
    [36]  Reserved
    [40]  ValueType         - 1=button, 2=continuous
    [44]  MaxOutput         - float32: 1.0 (0x3F800000)
    [48]  Reserved
    [52]  Cond1ModifierCmd  - modifier command ID for condition 1 (0=none)
    [56]  Cond1Value        - value the modifier must equal
    [60]  Cond2Value        - value for condition 2
    [64]  Cond2ModifierCmd  - modifier command ID for condition 2 (0=none)
    [68]  Reserved
    [72]  Reserved
    [76]  Reserved76        - 1 for buttons, 2 for knobs
    [80]  Reserved80        - 0
    [84]  Reserved84        - 1 for buttons, 2 for knobs
    [88]  EncoderMode       - 1 for buttons, 0x3F800000 (1.0f) for knobs
    [92]  Reserved
    [96]  MaxVelocity       - 127
    [100] TriggerRelease    - 0=on press, 1=on release
    [104] LEDFeedback       - 0 or 1
    [108] LEDType           - 1 for buttons, 2 for knobs
    [112] OutputScale       - 1 for buttons (raw uint), 0x3D800000 (0.0625f) for knobs
    [116] Reserved
"""

import struct

CMAD_SIZE = 120  # bytes


def build_cmad_knob(
    target: int = 0,
    invert: int = 0,
    cond1_mod: int = 0,
    cond1_val: int = 0,
    cond2_mod: int = 0,
    cond2_val: int = 0,
) -> bytes:
    """Build CMAD payload for a knob/encoder input.

    Pattern from real TSI: ControlType=1, InteractionMode=3,
    Reserved76=2, Reserved84=2, EncoderMode=1.0f, LEDType=2,
    OutputScale=0.0625f.
    """
    fields = [
        4, 1, 3, target,
        0, invert, 0, 0x40A00000,
        0, 0, 2, 0x3F800000,
        0, cond1_mod, cond1_val, cond2_val,
        cond2_mod, 0, 0, 2,
        0, 2, 0x3F800000, 0,
        127, 0, 0, 2,
        0x3D800000, 0,
    ]
    return struct.pack('>30I', *fields)


def build_cmad_button(
    target: int = 0,
    interaction_mode: int = 1,
    invert: int = 0,
    cond1_mod: int = 0,
    cond1_val: int = 0,
    cond2_mod: int = 0,
    cond2_val: int = 0,
    trigger_release: int = 0,
    led_feedback: int = 0,
) -> bytes:
    """Build CMAD payload for a button input.

    Args:
        interaction_mode: 1=Toggle, 2=Direct (for modifiers).
        trigger_release: 0=fire on press, 1=fire on release.
    """
    fields = [
        4, 0, interaction_mode, target,
        0, invert, 0, 0x40A00000,
        0, 0, 1, 0x3F800000,
        0, cond1_mod, cond1_val, cond2_val,
        cond2_mod, 0, 0, 1,
        0, 1, 1, 0,
        127, trigger_release, led_feedback, 1,
        1, 0,
    ]
    return struct.pack('>30I', *fields)


def build_cmad_output(target: int = 0, invert: int = 1) -> bytes:
    """Build CMAD payload for an LED output entry.

    Pattern from real TSI: ControlType=0xFFFF, InteractionMode=8.
    """
    fields = [
        4, 0xFFFF, 8, target,
        0, invert, 0, 0x40A00000,
        0, 0, 1, 0x3F800000,
        0, 0, 0, 0,
        0, 0, 0, 1,
        0, 1, 1, 0,
        127, 0, 0, 1,
        1, 0,
    ]
    return struct.pack('>30I', *fields)


def parse_cmad(data: bytes) -> dict:
    """Parse a 120-byte CMAD payload into a dict of fields.

    Args:
        data: 120 bytes of CMAD payload.

    Returns:
        Dict with named fields.
    """
    if len(data) < CMAD_SIZE:
        raise ValueError(f"CMAD payload too short: {len(data)} < {CMAD_SIZE}")

    fields = struct.unpack('>30I', data[:CMAD_SIZE])
    names = [
        'device_type', 'control_type', 'interaction_mode', 'target',
        'auto_repeat', 'invert', 'reserved24', 'max_input_raw',
        'reserved32', 'reserved36', 'value_type', 'max_output_raw',
        'reserved48', 'cond1_mod_cmd', 'cond1_value', 'cond2_value',
        'cond2_mod_cmd', 'reserved68', 'reserved72', 'reserved76',
        'reserved80', 'reserved84', 'encoder_mode', 'reserved92',
        'max_velocity', 'trigger_release', 'led_feedback', 'led_type',
        'output_scale_raw', 'reserved116',
    ]
    return dict(zip(names, fields))
