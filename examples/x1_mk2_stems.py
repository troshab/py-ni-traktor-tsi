#!/usr/bin/env python3
"""
X1 MK2 Stems (trosha_b edition) - TSI mapping generator.

Turns the Traktor Kontrol X1 MK2 into a dedicated stems controller
for 4 decks + FX Unit 1-4 controller.

Two modes:
  - Mute mode (default): bottom 4x4 grid = stem mute toggles
  - Control mode (FX Assign button): select stems + use encoders for Volume/Filter/FX

Usage:
    python -m examples.x1_mk2_stems --source /path/to/StemsX1MK2.tsi --output /path/to/output.tsi

Requires a donor StemsX1MK2.tsi (or any X1 MK2 TSI) as template
for the device definition (DDCI/DDCO control catalog).
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traktor_tsi import (
    parse_tsi, write_tsi, rebuild_tsi, get_device_info,
    build_cmai, build_ddcb,
    build_cmad_knob, build_cmad_button, build_cmad_modifier, build_cmad_output,
    CMD_SLOT_VOLUME, CMD_SLOT_FILTER, CMD_SLOT_MUTE, CMD_SLOT_FX_AMOUNT,
    CMD_MODIFIER_1, CMD_MODIFIER_2, CMD_MODIFIER_3,
    CMD_MODIFIER_4, CMD_MODIFIER_5, CMD_MODIFIER_6, CMD_MODIFIER_7,
    CMD_FX_UNIT_ON, CMD_FX_DRY_WET,
    CMD_FX_KNOB_1, CMD_FX_KNOB_2, CMD_FX_KNOB_3,
    CMD_FX_BUTTON_1, CMD_FX_BUTTON_2, CMD_FX_BUTTON_3,
    CMD_DECK_IS_LOADED,
    slot_target,
)

# ---------------------------------------------------------------------------
# Physical layout
# ---------------------------------------------------------------------------

# Mode toggle: FX Assign buttons above each column
# (ctrl_name, col) where col = M1 value (1-4)
MODE_BUTTONS = [
    ('Left.FX Assign 1',  1),   # Col 1 → Deck C
    ('Left.FX Assign 2',  2),   # Col 2 → Deck A
    ('Right.FX Assign 1', 3),   # Col 3 → Deck B
    ('Right.FX Assign 2', 4),   # Col 4 → Deck D
]

# Mode LED outputs (FX Assign indicator LEDs)
MODE_LED_OUTPUTS = [
    ('Left.FX Assign Indicator 1',  1),
    ('Left.FX Assign Indicator 2',  2),
    ('Right.FX Assign Indicator 1', 3),
    ('Right.FX Assign Indicator 2', 4),
]

# Stem buttons: (ctrl_name, deck, stem_slot, row, col)
# col = M1 value (deck column): 1=C, 2=A, 3=B, 4=D
# row = stem number: 1=Drums, 2=Bass, 3=Other, 4=Vocals
STEM_BUTTONS = [
    # Row 1: Stem 1 (Drums)
    ('Left.HotCue 1',     'C', 1, 1, 1),
    ('Left.HotCue 2',     'A', 1, 1, 2),
    ('Right.HotCue 1',    'B', 1, 1, 3),
    ('Right.HotCue 2',    'D', 1, 1, 4),
    # Row 2: Stem 2 (Bass)
    ('Left.HotCue 3',     'C', 2, 2, 1),
    ('Left.HotCue 4',     'A', 2, 2, 2),
    ('Right.HotCue 3',    'B', 2, 2, 3),
    ('Right.HotCue 4',    'D', 2, 2, 4),
    # Row 3: Stem 3 (Other/Melody)
    ('Left.Flux Button',  'C', 3, 3, 1),
    ('Left.Sync Button',  'A', 3, 3, 2),
    ('Right.Flux Button', 'B', 3, 3, 3),
    ('Right.Sync Button', 'D', 3, 3, 4),
    # Row 4: Stem 4 (Vocals)
    ('Left.Cue Button',   'C', 4, 4, 1),
    ('Left.Play Button',  'A', 4, 4, 2),
    ('Right.Cue Button',  'B', 4, 4, 3),
    ('Right.Play Button', 'D', 4, 4, 4),
]

# Row number → stem selection modifier
ROW_MODIFIER = {
    1: CMD_MODIFIER_2,  # M2 = stem 1 selected
    2: CMD_MODIFIER_3,  # M3 = stem 2 selected
    3: CMD_MODIFIER_4,  # M4 = stem 3 selected
    4: CMD_MODIFIER_5,  # M5 = stem 4 selected
}

COL_TO_DECK = {1: 'C', 2: 'A', 3: 'B', 4: 'D'}

# LED colors for HotCue RGB buttons (NHL output controls are color-specific)
# Columns 1,4 (Deck C,D - outer) = Yellow; Columns 2,3 (Deck A,B - inner) = Blue
HOTCUE_LED_COLORS = {1: 'Yellow', 2: 'Blue', 3: 'Blue', 4: 'Yellow'}

# Dim LED colors for empty decks (different color = no conflict with mute LEDs)
# Yellow columns get Warm Yellow (dimmer shade), Blue columns get Cyan
HOTCUE_DIM_COLORS = {1: 'Warm Yellow', 2: 'Cyan', 3: 'Cyan', 4: 'Warm Yellow'}

# Deck target for CMD_DECK_IS_LOADED output: A=0, B=1, C=2, D=3
DECK_TARGET = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

def _led_name(ctrl_name: str, col: int = 2) -> str:
    """Map input control name to LED output control name.

    HotCue buttons have RGB LEDs with color-specific output names
    (e.g. 'Left.HotCue 1.Blue'). Other buttons use the same name.
    """
    if 'HotCue' in ctrl_name:
        return f'{ctrl_name}.{HOTCUE_LED_COLORS[col]}'
    return ctrl_name

# Encoders: (ctrl_name, traktor_cmd)
ENCODERS = [
    ('Left.Loop Encoder Turn',  CMD_SLOT_VOLUME),    # Stem volume
    ('Browse Encoder Turn',     CMD_SLOT_FILTER),     # Stem filter
    ('Right.Loop Encoder Turn', CMD_SLOT_FX_AMOUNT),  # Stem FX send
]

# FX physical controls per side: (ctrl_name, traktor_cmd, is_knob)
FX_CONTROLS = {
    'left': [
        ('Left.FX Mode Button',  CMD_FX_UNIT_ON,  False),
        ('Left.FX D/W Knob',     CMD_FX_DRY_WET,  True),
        ('Left.FX 1 Button',     CMD_FX_BUTTON_1, False),
        ('Left.FX 1 Knob',       CMD_FX_KNOB_1,   True),
        ('Left.FX 2 Button',     CMD_FX_BUTTON_2, False),
        ('Left.FX 2 Knob',       CMD_FX_KNOB_2,   True),
        ('Left.FX 3 Button',     CMD_FX_BUTTON_3, False),
        ('Left.FX 3 Knob',       CMD_FX_KNOB_3,   True),
    ],
    'right': [
        ('Right.FX Mode Button', CMD_FX_UNIT_ON,  False),
        ('Right.FX D/W Knob',    CMD_FX_DRY_WET,  True),
        ('Right.FX 1 Button',    CMD_FX_BUTTON_1, False),
        ('Right.FX 1 Knob',      CMD_FX_KNOB_1,   True),
        ('Right.FX 2 Button',    CMD_FX_BUTTON_2, False),
        ('Right.FX 2 Knob',      CMD_FX_KNOB_2,   True),
        ('Right.FX 3 Button',    CMD_FX_BUTTON_3, False),
        ('Right.FX 3 Knob',      CMD_FX_KNOB_3,   True),
    ],
}

# FX unit selection: modifier + target per modifier value
# M6 (left): 0→FX3 (target 2), 1→FX1 (target 0)
# M7 (right): 0→FX4 (target 3), 1→FX2 (target 1)
FX_SELECT = {
    'left':  (CMD_MODIFIER_6, {0: 2, 1: 0}),
    'right': (CMD_MODIFIER_7, {0: 3, 1: 1}),
}

# FX Assign button → (modifier, value_to_set)
FX_ASSIGN_MOD = {
    'Left.FX Assign 1':  (CMD_MODIFIER_6, 0),   # → FX3 (default)
    'Left.FX Assign 2':  (CMD_MODIFIER_6, 1),   # → FX1
    'Right.FX Assign 1': (CMD_MODIFIER_7, 1),   # → FX2
    'Right.FX Assign 2': (CMD_MODIFIER_7, 0),   # → FX4 (default)
}


def generate():
    """Generate all mapping entries.

    Architecture:
    - M1: active column (0=mute mode, 1=C, 2=A, 3=B, 4=D)
    - M2-M5: stem 1-4 selected (0/1), toggled by stem buttons
    - M6: left FX unit select (0=FX3, 1=FX1)
    - M7: right FX unit select (0=FX4, 1=FX2)

    Mute mode (M1=0): buttons toggle stem mute
    Control mode (M1=1-4): buttons select stems, encoders adjust selected stems
    for the deck identified by M1

    FX Assign buttons set both M1 (column select) and M6/M7 (FX unit select):
    - FX Assign 1 Left (col 1/C) → M6=0 (FX3, default)
    - FX Assign 2 Left (col 2/A) → M6=1 (FX1)
    - FX Assign 1 Right (col 3/B) → M7=1 (FX2)
    - FX Assign 2 Right (col 4/D) → M7=0 (FX4, default)
    """
    cmais = []
    names = []
    idx = 0

    def add(ctrl_name, mapping_type, cmd_id, cmad):
        nonlocal idx
        cmais.append(build_cmai(idx, mapping_type, cmd_id, cmad))
        names.append(ctrl_name)
        idx += 1

    # --- Section A: Mode toggle (20 entries) ---
    # Absolute mode requires conditions on ALL entries to prevent release reset.
    # Without condition, Absolute mode sends max_output on press AND 0 on release.
    # With condition, release doesn't fire because the condition is no longer met
    # (the press already changed M1, so the original condition is false).
    #
    # Per button (col=N): 4 "enter" entries (from M1=0,other1,other2,other3)
    #   + 1 "exit" entry (from M1=N → M1=0). Allows direct column switching.
    all_cols = [c for _, c in MODE_BUTTONS]
    for ctrl, col in MODE_BUTTONS:
        # Enter from each possible source value (0 and other columns)
        for src in [0] + [c for c in all_cols if c != col]:
            add(ctrl, 0, CMD_MODIFIER_1,
                build_cmad_modifier(value=col,
                                    cond1_mod=CMD_MODIFIER_1, cond1_val=src))
        # Exit: toggle off when already in this column
        add(ctrl, 0, CMD_MODIFIER_1,
            build_cmad_modifier(value=0,
                                cond1_mod=CMD_MODIFIER_1, cond1_val=col))

    # --- Section A2: FX unit selector (4 entries) ---
    # FX Assign buttons also select which FX unit the side controls.
    # M6 (left): 0=FX3 (default), 1=FX1. M7 (right): 0=FX4 (default), 1=FX2.
    # Latch: condition on opposite value prevents Absolute mode release reset.
    for ctrl, _col in MODE_BUTTONS:
        fx_mod, fx_val = FX_ASSIGN_MOD[ctrl]
        add(ctrl, 0, fx_mod,
            build_cmad_modifier(value=fx_val,
                                cond1_mod=fx_mod, cond1_val=1 - fx_val))

    # --- Section B: Stem mute in mute mode (16 entries) ---
    # Condition: M1=0
    for ctrl, deck, slot, row, col in STEM_BUTTONS:
        tgt = slot_target(deck, slot)
        add(ctrl, 0, CMD_SLOT_MUTE,
            build_cmad_button(target=tgt, interaction_mode=1,
                              cond1_mod=CMD_MODIFIER_1, cond1_val=0))

    # --- Section C: Stem select (32 entries) ---
    # Toggle stem selection (M2-M5) using Absolute mode with conditions.
    # Conditions prevent Absolute mode release reset (latch pattern):
    #   Press when M=0: condition true → set M=1. Release: M=1 now, condition false → no reset.
    #   Press when M=1: first entry skips (M≠0). Second fires → set M=0. Release: M=0, condition false → no reset.
    # cond2: M1=col ensures stem select only fires in the correct column's control mode,
    # preventing unintended modifier changes in mute mode (M1=0) or other columns.
    for ctrl, deck, slot, row, col in STEM_BUTTONS:
        stem_mod = ROW_MODIFIER[row]
        add(ctrl, 0, stem_mod,
            build_cmad_modifier(value=1,
                                cond1_mod=stem_mod, cond1_val=0,
                                cond2_mod=CMD_MODIFIER_1, cond2_val=col))
        add(ctrl, 0, stem_mod,
            build_cmad_modifier(value=0,
                                cond1_mod=stem_mod, cond1_val=1,
                                cond2_mod=CMD_MODIFIER_1, cond2_val=col))

    # --- Section D: Encoders x deck x stem (48 entries) ---
    # Conditions: M1=col (deck) AND M_stem=1
    # interaction_mode=4 (Relative) for encoder Turn controls
    for enc_name, enc_cmd in ENCODERS:
        for col in range(1, 5):
            deck = COL_TO_DECK[col]
            for row in range(1, 5):
                tgt = slot_target(deck, row)
                stem_mod = ROW_MODIFIER[row]
                add(enc_name, 0, enc_cmd,
                    build_cmad_knob(
                        target=tgt,
                        interaction_mode=4,
                        cond1_mod=CMD_MODIFIER_1, cond1_val=col,
                        cond2_mod=stem_mod, cond2_val=1,
                    ))

    # --- Section E: FX controls (32 entries) ---
    # Conditional on M6 (left) / M7 (right) for FX unit selection.
    for side in ('left', 'right'):
        fx_mod, targets = FX_SELECT[side]
        for mod_val, fx_tgt in targets.items():
            for fx_name, fx_cmd, is_knob in FX_CONTROLS[side]:
                if is_knob:
                    add(fx_name, 0, fx_cmd,
                        build_cmad_knob(target=fx_tgt,
                                        cond1_mod=fx_mod, cond1_val=mod_val))
                else:
                    add(fx_name, 0, fx_cmd,
                        build_cmad_button(target=fx_tgt, interaction_mode=1,
                                          cond1_mod=fx_mod, cond1_val=mod_val))

    # --- Section F: FX unit selector LEDs (4 entries) ---
    # LED shows which FX unit is active per side.
    # Output raw modifier value; invert for "default" buttons (M6=0, M7=0).
    fx_indicator_leds = [
        ('Left.FX Assign Indicator 1',  CMD_MODIFIER_6, 1),  # invert=1: ON when M6=0 (FX3)
        ('Left.FX Assign Indicator 2',  CMD_MODIFIER_6, 0),  # invert=0: ON when M6=1 (FX1)
        ('Right.FX Assign Indicator 1', CMD_MODIFIER_7, 0),  # invert=0: ON when M7=1 (FX2)
        ('Right.FX Assign Indicator 2', CMD_MODIFIER_7, 1),  # invert=1: ON when M7=0 (FX4)
    ]
    for ctrl, fx_mod, inv in fx_indicator_leds:
        add(ctrl, 1, fx_mod,
            build_cmad_output(target=0, invert=inv))

    # --- Section G: Stem mute LEDs (16 entries) ---
    # invert=1: lit = unmuted (playing), dark = muted
    # HotCue buttons use color-specific output names (e.g. 'Left.HotCue 1.Blue')
    for ctrl, deck, slot, row, col in STEM_BUTTONS:
        tgt = slot_target(deck, slot)
        add(_led_name(ctrl, col), 1, CMD_SLOT_MUTE,
            build_cmad_output(target=tgt, invert=1))

    # --- Section H: FX button LEDs (16 entries) ---
    # Conditional on M6/M7 for correct FX unit target.
    for side in ('left', 'right'):
        fx_mod, targets = FX_SELECT[side]
        for mod_val, fx_tgt in targets.items():
            for fx_name, fx_cmd, is_knob in FX_CONTROLS[side]:
                if not is_knob:
                    add(fx_name, 1, fx_cmd,
                        build_cmad_output(target=fx_tgt, invert=0,
                                          cond1_mod=fx_mod, cond1_val=mod_val))

    # --- Section I: Empty deck dim LEDs (8 entries) ---
    # When deck has no track loaded, HotCue buttons show dim glow in alternate color.
    # Uses different NHL color output (Warm Yellow / Cyan) to avoid conflict with
    # mute LEDs (Yellow / Blue). CMD_DECK_IS_LOADED invert=1: ON when NOT loaded.
    # Only HotCue buttons (rows 1-2) - non-HotCue have mono LEDs, can't use alt color.
    for ctrl, deck, slot, row, col in STEM_BUTTONS:
        if 'HotCue' not in ctrl:
            continue
        deck_tgt = DECK_TARGET[deck]
        led_name = f'{ctrl}.{HOTCUE_DIM_COLORS[col]}'
        add(led_name, 1, CMD_DECK_IS_LOADED,
            build_cmad_output(target=deck_tgt, invert=1))

    return cmais, names


def main():
    parser = argparse.ArgumentParser(description='Generate X1 MK2 Stems TSI mapping')
    parser.add_argument('--source', '-s', required=True,
                        help='Source X1 MK2 TSI file (template for device definition)')
    parser.add_argument('--output', '-o', required=True,
                        help='Output TSI file path')
    args = parser.parse_args()

    print(f"Parsing template: {args.source}")
    original = parse_tsi(args.source)
    info = get_device_info(original)
    print(f"  Device: {info['name']}")
    print(f"  Inputs: {info.get('input_count', '?')}, Outputs: {info.get('output_count', '?')}")
    print(f"  Existing mappings: {info.get('mapping_count', '?')}")

    print("\nGenerating mapping entries...")
    cmais, names = generate()
    print(f"  Total entries: {len(cmais)}")

    ddcb = build_ddcb(cmais, names)
    new_binary = rebuild_tsi(original, ddcb,
                             new_comment='X1 MK2 StemsFX (trosha_b edition)')

    print(f"\nWriting: {args.output}")
    write_tsi(new_binary, args.output, args.source)

    # Verify
    verify = parse_tsi(args.output)
    verify_info = get_device_info(verify)
    print(f"  Verified: {verify_info.get('mapping_count', '?')} mappings, "
          f"comment={verify_info.get('comment', '?')!r}")
    print("Done.")


if __name__ == '__main__':
    main()
