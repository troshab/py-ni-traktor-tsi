#!/usr/bin/env python3
"""
X1 MK2 Stems (trosha_b edition) - TSI mapping generator.

Turns the Traktor Kontrol X1 MK2 into a dedicated stems controller
for 4 decks + FX Unit 3/4 controller.

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
    build_cmad_knob, build_cmad_button, build_cmad_output,
    CMD_SLOT_VOLUME, CMD_SLOT_FILTER, CMD_SLOT_MUTE, CMD_SLOT_FX_AMOUNT,
    CMD_MODIFIER_1, CMD_MODIFIER_2, CMD_MODIFIER_3,
    CMD_FX_UNIT_ON, CMD_FX_DRY_WET,
    CMD_FX_KNOB_1, CMD_FX_KNOB_2, CMD_FX_KNOB_3,
    CMD_FX_BUTTON_1, CMD_FX_BUTTON_2, CMD_FX_BUTTON_3,
    slot_target,
)

# Physical layout: (col, row, midi_name, deck, stem_slot, m1_value, m2_value)
# Column-to-deck mirrors S4 MK3 mixer: Col1=C, Col2=A, Col3=B, Col4=D
STEM_BUTTONS = [
    # Row 1: Stem 1 (Drums)
    (1, 1, 'Left.HotCue 1',     'C', 1, 1, 1),
    (2, 1, 'Left.HotCue 2',     'A', 1, 1, 2),
    (3, 1, 'Right.HotCue 1',    'B', 1, 1, 3),
    (4, 1, 'Right.HotCue 2',    'D', 1, 1, 4),
    # Row 2: Stem 2 (Bass)
    (1, 2, 'Left.HotCue 3',     'C', 2, 2, 1),
    (2, 2, 'Left.HotCue 4',     'A', 2, 2, 2),
    (3, 2, 'Right.HotCue 3',    'B', 2, 2, 3),
    (4, 2, 'Right.HotCue 4',    'D', 2, 2, 4),
    # Row 3: Stem 3 (Other/Melody)
    (1, 3, 'Left.Flux Button',  'C', 3, 3, 1),
    (2, 3, 'Left.Sync Button',  'A', 3, 3, 2),
    (3, 3, 'Right.Flux Button', 'B', 3, 3, 3),
    (4, 3, 'Right.Sync Button', 'D', 3, 3, 4),
    # Row 4: Stem 4 (Vocals)
    (1, 4, 'Left.Cue Button',   'C', 4, 4, 1),
    (2, 4, 'Left.Play Button',  'A', 4, 4, 2),
    (3, 4, 'Right.Cue Button',  'B', 4, 4, 3),
    (4, 4, 'Right.Play Button', 'D', 4, 4, 4),
]

ENCODERS = [
    ('Left.Loop Encoder Turn',  CMD_SLOT_VOLUME),    # Stem volume
    ('Browse Encoder Turn',     CMD_SLOT_FILTER),     # Stem filter
    ('Right.Loop Encoder Turn', CMD_SLOT_FX_AMOUNT),  # Stem FX send
]

FX_ENTRIES = [
    # Left side = FX Unit 3
    ('Left.FX Mode Button',  CMD_FX_UNIT_ON,  2, False),
    ('Left.FX D/W Knob',     CMD_FX_DRY_WET,  2, True),
    ('Left.FX 1 Button',     CMD_FX_BUTTON_1, 2, False),
    ('Left.FX 1 Knob',       CMD_FX_KNOB_1,   2, True),
    ('Left.FX 2 Button',     CMD_FX_BUTTON_2, 2, False),
    ('Left.FX 2 Knob',       CMD_FX_KNOB_2,   2, True),
    ('Left.FX 3 Button',     CMD_FX_BUTTON_3, 2, False),
    ('Left.FX 3 Knob',       CMD_FX_KNOB_3,   2, True),
    # Right side = FX Unit 4
    ('Right.FX Mode Button', CMD_FX_UNIT_ON,  3, False),
    ('Right.FX D/W Knob',    CMD_FX_DRY_WET,  3, True),
    ('Right.FX 1 Button',    CMD_FX_BUTTON_1, 3, False),
    ('Right.FX 1 Knob',      CMD_FX_KNOB_1,   3, True),
    ('Right.FX 2 Button',    CMD_FX_BUTTON_2, 3, False),
    ('Right.FX 2 Knob',      CMD_FX_KNOB_2,   3, True),
    ('Right.FX 3 Button',    CMD_FX_BUTTON_3, 3, False),
    ('Right.FX 3 Knob',      CMD_FX_KNOB_3,   3, True),
]


def generate():
    """Generate all mapping entries. Returns (cmai_payloads, ctrl_names)."""
    cmais = []
    names = []
    idx = 0

    def add(ctrl_name, mapping_type, cmd_id, cmad):
        nonlocal idx
        cmais.append(build_cmai(idx, mapping_type, cmd_id, cmad))
        names.append(ctrl_name)
        idx += 1

    # Section A: 16 stem buttons x 6 entries = 96
    for col, row, midi_name, deck, slot, m1, m2 in STEM_BUTTONS:
        tgt = slot_target(deck, slot)

        # A1: Set M1 (stem row) on press
        add(midi_name, 0, CMD_MODIFIER_1,
            build_cmad_button(target=m1, interaction_mode=2))

        # A2: Set M2 (deck column) on press
        add(midi_name, 0, CMD_MODIFIER_2,
            build_cmad_button(target=m2, interaction_mode=2))

        # A3: Reset M3 (encoder-used flag) on press
        add(midi_name, 0, CMD_MODIFIER_3,
            build_cmad_button(target=0, interaction_mode=2))

        # A4: Toggle mute on release (only if encoder was NOT used)
        add(midi_name, 0, CMD_SLOT_MUTE,
            build_cmad_button(
                target=tgt, interaction_mode=1,
                cond1_mod=CMD_MODIFIER_3, cond1_val=0,
                trigger_release=1,
            ))

        # A5: Reset M1 on release
        add(midi_name, 0, CMD_MODIFIER_1,
            build_cmad_button(target=0, interaction_mode=2, trigger_release=1))

        # A6: Reset M2 on release
        add(midi_name, 0, CMD_MODIFIER_2,
            build_cmad_button(target=0, interaction_mode=2, trigger_release=1))

    # Section B: 3 encoders x 16 M1/M2 combinations = 48
    for enc_name, enc_cmd in ENCODERS:
        for m1 in range(1, 5):
            for m2 in range(1, 5):
                deck = {1: 'C', 2: 'A', 3: 'B', 4: 'D'}[m2]
                tgt = slot_target(deck, m1)
                add(enc_name, 0, enc_cmd,
                    build_cmad_knob(
                        target=tgt,
                        cond1_mod=CMD_MODIFIER_1, cond1_val=m1,
                        cond2_mod=CMD_MODIFIER_2, cond2_val=m2,
                    ))

    # Section B2: 3 encoders x 4 M1 values = 12 (set M3 encoder-used flag)
    for enc_name, _ in ENCODERS:
        for m1 in range(1, 5):
            add(enc_name, 0, CMD_MODIFIER_3,
                build_cmad_button(
                    target=1, interaction_mode=2,
                    cond1_mod=CMD_MODIFIER_1, cond1_val=m1,
                ))

    # Section C: FX Unit 3/4 controls = 16
    for fx_name, fx_cmd, fx_tgt, is_knob in FX_ENTRIES:
        if is_knob:
            add(fx_name, 0, fx_cmd, build_cmad_knob(target=fx_tgt))
        else:
            add(fx_name, 0, fx_cmd,
                build_cmad_button(target=fx_tgt, interaction_mode=1))

    # Section D: LED output for 16 stem buttons = 16
    for col, row, midi_name, deck, slot, m1, m2 in STEM_BUTTONS:
        tgt = slot_target(deck, slot)
        add(midi_name, 1, CMD_SLOT_MUTE,
            build_cmad_output(target=tgt, invert=1))

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
    new_binary = rebuild_tsi(original, ddcb, 'X1 MK2 Stems (trosha_b edition)')

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
