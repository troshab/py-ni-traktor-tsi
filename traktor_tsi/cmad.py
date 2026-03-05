"""CMAD (Command Mapping Assignment Data) builders.

CMAD is a 120-byte payload (30 x uint32 BE) inside each CMAI entry.
Field layout reverse-engineered from real TSI files and cmdr-editor source.

Field map (offset in bytes):
    [0]   DeviceType        - always 4
    [4]   ControlType       - 0=Button, 1=FaderOrKnob, 0xFFFF=Output
    [8]   InteractionMode   - 1=Toggle, 2=Hold, 3=Direct, 4=Relative, 5=Inc, 6=Dec, 8=Output
    [12]  Target            - deck/slot/FX unit assignment (0-15)
    [16]  AutoRepeat        - 0
    [20]  Invert            - 0 or 1
    [24]  SoftTakeover      - 0
    [28]  RotarySensitivity - float32: 5.0 (0x40A00000)
    [32]  RotaryAcceleration - 0
    [36]  HasValueUI        - 0 or 1
    [40]  ValueUIType       - 1=button, 2=continuous
    [44]  SetValueTo        - float32/uint32 value
    [48]  Comment           - WideString char count (0 = empty)
    [52]  Cond1Id           - modifier command ID for condition 1 (0=none)
    [56]  Cond1Target       - condition 1 target deck (0=Global)
    [60]  Cond1Value        - condition 1 value (uint32)
    [64]  Cond2Id           - modifier command ID for condition 2 (0=none)
    [68]  Cond2Target       - condition 2 target deck (0=Global)
    [72]  Cond2Value        - condition 2 value (uint32)
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
    interaction_mode: int = 3,
    invert: int = 0,
    cond1_mod: int = 0,
    cond1_val: int = 0,
    cond2_mod: int = 0,
    cond2_val: int = 0,
) -> bytes:
    """Build CMAD payload for a knob/encoder input.

    Args:
        interaction_mode: 2=Direct, 3=Absolute (knobs), 4=Relative (encoders).

    ControlType depends on mode: 1=FaderOrKnob (Absolute/Direct),
    2=Encoder (Relative). Confirmed from community NHL TSI analysis
    (100% of mode=4 entries use control_type=2).
    """
    # Mode 4 (Relative) requires ControlType=2 (Encoder), not 1 (FaderOrKnob)
    control_type = 2 if interaction_mode == 4 else 1
    fields = [
        4, control_type, interaction_mode, target,
        0, invert, 0, 0x40A00000,
        0, 0, 2, 0x3F800000,
        0, cond1_mod, 0, cond1_val,
        cond2_mod, 0, cond2_val, 2,
        0, 2, 0x3F800000, 0,
        127, 0, 1, 2,
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
    max_output: int = 0x3F800000,
) -> bytes:
    """Build CMAD payload for a button input.

    Args:
        interaction_mode: 1=Toggle, 2=Direct, 3=Absolute (for modifiers).
        trigger_release: 0=fire on press, 1=fire on release.
        max_output: raw uint32 for MaxOutput field [44]. Default 0x3F800000
            (float 1.0) for normal buttons. For modifier commands with
            Absolute mode, use the integer value to set (e.g. 1, 2, 3).
    """
    fields = [
        4, 0, interaction_mode, target,
        0, invert, 0, 0x40A00000,
        0, 0, 1, max_output,
        0, cond1_mod, 0, cond1_val,
        cond2_mod, 0, cond2_val, 1,
        0, 1, 1, 0,
        127, trigger_release, led_feedback, 1,
        1, 0,
    ]
    return struct.pack('>30I', *fields)


def build_cmad_modifier(
    value: int = 0,
    interaction_mode: int = 3,
    cond1_mod: int = 0,
    cond1_val: int = 0,
    cond2_mod: int = 0,
    cond2_val: int = 0,
) -> bytes:
    """Build CMAD payload for a modifier command (CMD_MODIFIER_1..8).

    Reverse-engineered from community NHL mappings (CHAMELEON, L-K,
    TempoKontrol). Modifier entries differ from regular buttons in
    several fields:
      - [9]  offset 36: 1 (vs 0 for buttons) - unknown flag
      - [11] offset 44: integer value to set (not float 1.0)
      - [22] offset 88: 7 (modifier max range, vs 1 for buttons)
      - [26] offset 104: 1 (LED feedback enabled)

    Args:
        value: Modifier value to set (0-7).
        interaction_mode: 3=Absolute (set value), 2=Direct (hold).
        cond1_mod/cond1_val: Condition 1 (required for latch behavior).
        cond2_mod/cond2_val: Condition 2.
    """
    fields = [
        4, 0, interaction_mode, 0,        # target=0 always for modifiers
        0, 0, 0, 0x40A00000,
        0, 1, 1, value,                    # [9]=1, [11]=value
        0, cond1_mod, 0, cond1_val,
        cond2_mod, 0, cond2_val, 1,
        0, 1, 7, 0,                        # [22]=7 (modifier max range)
        127, 0, 1, 1,                      # [26]=1 (LED feedback)
        1, 0,                              # [28]=output_scale=1, [29]=0 (Override factory map)
    ]
    return struct.pack('>30I', *fields)


def build_cmad_continuous_button(
    target: int = 0,
    interaction_mode: int = 3,
    invert: int = 0,
    cond1_mod: int = 0,
    cond1_val: int = 0,
    cond2_mod: int = 0,
    cond2_val: int = 0,
    trigger_release: int = 0,
    max_output: int = 0x3F800000,
) -> bytes:
    """Build CMAD payload for a button controlling a continuous parameter.

    Unlike build_cmad_button (value_type=1, digital), this uses value_type=2
    (continuous) and knob-style field layout. Required for Reset/Absolute
    mode on continuous commands like CMD_SLOT_VOLUME, CMD_SLOT_FILTER,
    CMD_SLOT_FX_AMOUNT.

    Args:
        interaction_mode: 3=Absolute (set to max_output), 7=Reset (to default).
        max_output: Target value as raw uint32. For Absolute mode:
            Volume default: 0x3F800000 (1.0), Filter center: 0x3F000000 (0.5),
            FX Amount off: 0 (0.0).
        trigger_release: 0=on press, 1=on release.
    """
    fields = [
        4, 0, interaction_mode, target,
        0, invert, 0, 0x40A00000,
        0, 0, 2, max_output,              # value_type=2 (continuous)
        0, cond1_mod, 0, cond1_val,
        cond2_mod, 0, cond2_val, 2,               # reserved76=2 (knob-style)
        0, 2, 0x3F800000, 0,              # reserved84=2, encoder_mode=1.0f
        127, trigger_release, 0, 2,        # led_type=2 (knob-style)
        0x3D800000, 0,                     # output_scale=0.0625f
    ]
    return struct.pack('>30I', *fields)


def build_cmad_output(
    target: int = 0,
    invert: int = 1,
    cond1_mod: int = 0,
    cond1_val: int = 0,
    cond2_mod: int = 0,
    cond2_val: int = 0,
    trigger_release: int = 0,
) -> bytes:
    """Build CMAD payload for an LED output entry.

    Pattern from real TSI: ControlType=0xFFFF, InteractionMode=8.

    Conditions can be used for modifier LED feedback:
    output CMD_MODIFIER_1 with cond1_mod=CMD_MODIFIER_1, cond1_val=N
    makes LED light up only when modifier equals N.

    Args:
        trigger_release: 0=standard for Output entries (all community TSIs use 0).
    """
    fields = [
        4, 0xFFFF, 8, target,
        0, invert, 0, 0x40A00000,
        0, 0, 1, 0,               # MaxOutput = 0 (matches community pattern)
        0, cond1_mod, 0, cond1_val,
        cond2_mod, 0, cond2_val, 1,
        0, 1, 1, 0,
        127, trigger_release, 0, 1,
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
        'reserved48', 'cond1_mod_cmd', 'cond1_target', 'cond1_value',
        'cond2_mod_cmd', 'cond2_target', 'cond2_value', 'reserved76',
        'reserved80', 'reserved84', 'encoder_mode', 'reserved92',
        'max_velocity', 'trigger_release', 'led_feedback', 'led_type',
        'output_scale_raw', 'reserved116',
    ]
    return dict(zip(names, fields))
