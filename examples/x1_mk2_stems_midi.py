#!/usr/bin/env python3
"""
X1 MK2 Stems (trosha_b edition) - Generic MIDI TSI mapping generator.

Two modes:
  - Mute mode (default): bottom 4x4 grid = stem mute toggles
  - Control mode (FX Mode button): select stems + use encoders for Volume/Filter/FX

Requires X1 MK2 in MIDI mode (via Controller Editor).
MIDI assignments from current_basic.nckx1m2 (Controller Editor default).

Usage:
    python -m examples.x1_mk2_stems_midi \
        --source empty_generic_midi_x1mk2.tsi \
        --output X1_MK2_Stems_MIDI_trosha_b.tsi
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traktor_tsi import (
    parse_tsi, write_tsi, rebuild_tsi, get_device_info,
    build_cmai, build_ddcb,
    build_cmad_knob, build_cmad_button, build_cmad_output,
    CMD_SLOT_VOLUME, CMD_SLOT_FILTER, CMD_SLOT_MUTE, CMD_SLOT_FX_AMOUNT,
    CMD_MODIFIER_1, CMD_MODIFIER_2, CMD_MODIFIER_3,
    CMD_MODIFIER_4, CMD_MODIFIER_5,
    CMD_FX_UNIT_ON, CMD_FX_DRY_WET,
    CMD_FX_KNOB_1, CMD_FX_KNOB_2, CMD_FX_KNOB_3,
    CMD_FX_BUTTON_1, CMD_FX_BUTTON_2, CMD_FX_BUTTON_3,
    slot_target,
)

# ---------------------------------------------------------------------------
# MIDI helpers
# ---------------------------------------------------------------------------

NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']


def midi_note_name(note: int, channel: int = 1) -> str:
    octave = note // 12 - 1
    name = NOTE_NAMES[note % 12]
    return f'Ch{channel:02d}.Note.{name}{octave}'


def midi_cc_name(cc: int, channel: int = 1) -> str:
    return f'Ch{channel:02d}.CC.{cc:03d}'


# ---------------------------------------------------------------------------
# Physical layout
# ---------------------------------------------------------------------------

# Stem buttons: (midi_note, midi_ch, deck, stem_slot, row, col)
# col = M6 value (deck column): 1=C, 2=A, 3=B, 4=D
# row = stem number: 1=Drums, 2=Bass, 3=Other, 4=Vocals
# Stem modifier: row 1→M2, row 2→M3, row 3→M4, row 4→M5
STEM_BUTTONS = [
    # Row 1: Stem 1 (Drums)
    (30, 1, 'C', 1, 1, 1),
    (32, 1, 'A', 1, 1, 2),
    (31, 1, 'B', 1, 1, 3),
    (33, 1, 'D', 1, 1, 4),
    # Row 2: Stem 2 (Bass)
    (34, 1, 'C', 2, 2, 1),
    (36, 1, 'A', 2, 2, 2),
    (35, 1, 'B', 2, 2, 3),
    (37, 1, 'D', 2, 2, 4),
    # Row 3: Stem 3 (Other/Melody)
    (38, 1, 'C', 3, 3, 1),
    (40, 1, 'A', 3, 3, 2),
    (39, 1, 'B', 3, 3, 3),
    (41, 1, 'D', 3, 3, 4),
    # Row 4: Stem 4 (Vocals)
    (42, 1, 'C', 4, 4, 1),
    (44, 1, 'A', 4, 4, 2),
    (43, 1, 'B', 4, 4, 3),
    (45, 1, 'D', 4, 4, 4),
]

# Row number → stem selection modifier
ROW_MODIFIER = {
    1: CMD_MODIFIER_2,  # M2 = stem 1 selected
    2: CMD_MODIFIER_3,  # M3 = stem 2 selected
    3: CMD_MODIFIER_4,  # M4 = stem 3 selected
    4: CMD_MODIFIER_5,  # M5 = stem 4 selected
}

# Mode toggle buttons: FX Assign 1/2 Left/Right (above the stem columns)
# (midi_note, midi_ch, m1_target)
# Toggle: M1=target if M1!=target, else M1=0 (back to mute mode)
MODE_BUTTONS = [
    (20, 1, 1),   # G#0 = FX Assign 1 Left  → col 1 / Deck C
    (22, 1, 2),   # A#0 = FX Assign 2 Left  → col 2 / Deck A
    (21, 1, 3),   # A0  = FX Assign 1 Right → col 3 / Deck B
    (23, 1, 4),   # B0  = FX Assign 2 Right → col 4 / Deck D
]

# Encoders: (midi_cc, midi_ch, traktor_cmd)
ENCODERS = [
    (24, 1, CMD_SLOT_VOLUME),    # Left Loop Encoder → Stem Volume
    (16, 1, CMD_SLOT_FILTER),    # Browse Encoder → Stem Filter
    (25, 1, CMD_SLOT_FX_AMOUNT), # Right Loop Encoder → Stem FX Send
]

# FX controls: full FX Unit 3 (left) and FX Unit 4 (right)
FX_ENTRIES = [
    # Left side = FX Unit 3 (target=2)
    (8,  1, CMD_FX_UNIT_ON,  2, False),
    (0,  1, CMD_FX_DRY_WET,  2, True),
    (10, 1, CMD_FX_BUTTON_1, 2, False),
    (2,  1, CMD_FX_KNOB_1,   2, True),
    (12, 1, CMD_FX_BUTTON_2, 2, False),
    (4,  1, CMD_FX_KNOB_2,   2, True),
    (14, 1, CMD_FX_BUTTON_3, 2, False),
    (6,  1, CMD_FX_KNOB_3,   2, True),
    # Right side = FX Unit 4 (target=3)
    (9,  1, CMD_FX_UNIT_ON,  3, False),
    (1,  1, CMD_FX_DRY_WET,  3, True),
    (11, 1, CMD_FX_BUTTON_1, 3, False),
    (3,  1, CMD_FX_KNOB_1,   3, True),
    (13, 1, CMD_FX_BUTTON_2, 3, False),
    (5,  1, CMD_FX_KNOB_2,   3, True),
    (15, 1, CMD_FX_BUTTON_3, 3, False),
    (7,  1, CMD_FX_KNOB_3,   3, True),
]

COL_TO_DECK = {1: 'C', 2: 'A', 3: 'B', 4: 'D'}


def generate():
    """Generate all mapping entries.

    Architecture:
    - M1: active column (0=mute mode, 1=C, 2=A, 3=B, 4=D)
    - M2-M5: stem 1-4 selected (0/1), toggled by stem buttons

    Mute mode (M1=0): buttons toggle stem mute
    Control mode (M1=1-4): buttons select stems, encoders adjust selected stems
    for the deck identified by M1
    """
    cmais = []
    names = []
    idx = 0

    def add(ctrl_name, mapping_type, cmd_id, cmad):
        nonlocal idx
        cmais.append(build_cmai(idx, mapping_type, cmd_id, cmad))
        names.append(ctrl_name)
        idx += 1

    # --- Section A: Mode toggle (8 entries) ---
    # Each column has 2 entries (Direct mode, snapshot evaluation):
    #   1. Set M1=col (no condition) — always fires
    #   2. Set M1=0 (cond M1=col) — overwrites #1 if already in this column
    # Net: if M1!=col → M1=col (enter), if M1==col → M1=0 (exit)
    for note, ch, col in MODE_BUTTONS:
        ctrl = midi_note_name(note, ch)
        # Entry 1: set M1 to column value
        add(ctrl, 0, CMD_MODIFIER_1,
            build_cmad_button(target=col, interaction_mode=2))
        # Entry 2: reset M1 to 0 if already on this column (overwrites entry 1)
        add(ctrl, 0, CMD_MODIFIER_1,
            build_cmad_button(target=0, interaction_mode=2,
                              cond1_mod=CMD_MODIFIER_1, cond1_val=col))

    # --- Section B: Stem mute in mute mode (16 entries) ---
    # Condition: M1=0
    for note, ch, deck, slot, row, col in STEM_BUTTONS:
        tgt = slot_target(deck, slot)
        ctrl = midi_note_name(note, ch)
        add(ctrl, 0, CMD_SLOT_MUTE,
            build_cmad_button(target=tgt, interaction_mode=1,
                              cond1_mod=CMD_MODIFIER_1, cond1_val=0))

    # --- Section C: Stem select (16 entries) ---
    # Toggle stem selection (M2-M5) based on row.
    # No M1 condition: fires in both modes; harmless in mute mode
    # since nothing reads M2-M5 when M1=0.
    for note, ch, deck, slot, row, col in STEM_BUTTONS:
        ctrl = midi_note_name(note, ch)
        stem_mod = ROW_MODIFIER[row]
        add(ctrl, 0, stem_mod,
            build_cmad_button(target=1, interaction_mode=1))

    # --- Section D: Encoders x deck x stem (48 entries) ---
    # Conditions: M1=col (deck) AND M_stem=1
    for enc_cc, enc_ch, enc_cmd in ENCODERS:
        enc_ctrl = midi_cc_name(enc_cc, enc_ch)
        for col in range(1, 5):
            deck = COL_TO_DECK[col]
            for row in range(1, 5):
                tgt = slot_target(deck, row)
                stem_mod = ROW_MODIFIER[row]
                add(enc_ctrl, 0, enc_cmd,
                    build_cmad_knob(
                        target=tgt,
                        cond1_mod=CMD_MODIFIER_1, cond1_val=col,
                        cond2_mod=stem_mod, cond2_val=1,
                    ))

    # --- Section E: FX controls (16 entries) ---
    for midi_num, ch, fx_cmd, fx_tgt, is_knob in FX_ENTRIES:
        if is_knob:
            ctrl = midi_cc_name(midi_num, ch)
            add(ctrl, 0, fx_cmd, build_cmad_knob(target=fx_tgt))
        else:
            ctrl = midi_note_name(midi_num, ch)
            add(ctrl, 0, fx_cmd,
                build_cmad_button(target=fx_tgt, interaction_mode=1))

    # --- Section F: Mode button LEDs (4 entries) ---
    # Output CMD_MODIFIER_1 with condition M1=col: LED on when column active
    for note, ch, col in MODE_BUTTONS:
        ctrl = midi_note_name(note, ch)
        add(ctrl, 1, CMD_MODIFIER_1,
            build_cmad_output(target=1, invert=0,
                              cond1_mod=CMD_MODIFIER_1, cond1_val=col))

    # --- Section G: Stem mute LEDs (16 entries) ---
    # All on Ch01 (Ch03 causes constant-on for HotCue rows)
    # lit = unmuted (playing), dark = muted
    for note, ch, deck, slot, row, col in STEM_BUTTONS:
        tgt = slot_target(deck, slot)
        ctrl = midi_note_name(note, 1)
        add(ctrl, 1, CMD_SLOT_MUTE,
            build_cmad_output(target=tgt, invert=0))

    return cmais, names


def main():
    parser = argparse.ArgumentParser(
        description='Generate X1 MK2 Stems TSI mapping (Generic MIDI mode)')
    parser.add_argument('--source', '-s', required=True,
                        help='Source Generic MIDI TSI file (template)')
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
    new_binary = rebuild_tsi(original, ddcb, 'X1 MK2 Stems MIDI (trosha_b edition)')

    print(f"\nWriting: {args.output}")
    write_tsi(new_binary, args.output, args.source)

    verify = parse_tsi(args.output)
    verify_info = get_device_info(verify)
    print(f"  Verified: {verify_info.get('mapping_count', '?')} mappings, "
          f"comment={verify_info.get('comment', '?')!r}")
    print("Done.")


if __name__ == '__main__':
    main()
