#!/usr/bin/env python3
"""
S4 MK3 Stem Load Reset - TSI mapping generator.

Adds stem parameter reset to the Load (Browse.Encoder.Push) button
on the Traktor Kontrol S4 MK3. When loading a track, all stem
parameters (Volume, Filter, FX Amount, Mute) for the focused deck
reset to defaults.

Uses Deck Focus Selector (cmd 203) as condition to target only the
currently focused deck. No modifiers needed.

Uses Reset interaction mode (7) which resets parameters to their
factory default on button press.

Works alongside native Load function (no Override Factory Map needed).

Usage:
    python -m examples.s4_mk3_stem_reset \
        --source /path/to/S4MK3.tsi --output /path/to/output.tsi
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traktor_tsi import (
    parse_tsi, write_tsi, rebuild_tsi, get_device_info,
    build_cmai, build_ddcb,
    build_cmad_button, build_cmad_continuous_button,
    CMD_SLOT_VOLUME, CMD_SLOT_FILTER, CMD_SLOT_FX_AMOUNT, CMD_SLOT_MUTE,
    CMD_DECK_FOCUS,
    slot_target,
)

FOCUS_VAL = {'A': 0, 'B': 1, 'C': 2, 'D': 3}

# Left Browse.Encoder.Push loads into focused deck on left side (A or C).
# Right Browse.Encoder.Push loads into focused deck on right side (B or D).
LOAD_SIDES = [
    ('Left.Browse.Encoder.Push',  ['A', 'C']),
    ('Right.Browse.Encoder.Push', ['B', 'D']),
]

# Continuous stem parameters: use Absolute mode (3) with default values.
# Reset mode (7) has no confirmed support for Submix Slot commands in NHL mode.
# value_type=2 (continuous) is required for these commands.
CONTINUOUS_RESETS = [
    (CMD_SLOT_VOLUME,    0x3F800000),  # Absolute 1.0 (max volume)
    (CMD_SLOT_FILTER,    0x3F000000),  # Absolute 0.5 (filter center = off)
    (CMD_SLOT_FX_AMOUNT, 0),           # Absolute 0.0 (no FX send)
]


def generate():
    """Generate all mapping entries.

    2 sides x 2 decks x 4 slots x (3 continuous + 1 mute) = 64 entries.
    Each conditioned on Deck Focus matching the target deck.
    trigger_release=1: fires on button release (after native Load completes).
    """
    cmais = []
    names = []
    idx = 0

    def add(ctrl_name, mapping_type, cmd_id, cmad):
        nonlocal idx
        cmais.append(build_cmai(idx, mapping_type, cmd_id, cmad))
        names.append(ctrl_name)
        idx += 1

    for load_ctrl, decks in LOAD_SIDES:
        for deck in decks:
            for slot in range(1, 5):
                tgt = slot_target(deck, slot)
                # Continuous params: Absolute mode with value_type=2
                for cmd, default_val in CONTINUOUS_RESETS:
                    add(load_ctrl, 0, cmd,
                        build_cmad_continuous_button(
                            target=tgt,
                            interaction_mode=3,
                            max_output=default_val,
                            trigger_release=1,
                            cond1_mod=CMD_DECK_FOCUS,
                            cond1_val=FOCUS_VAL[deck],
                        ))
                # Mute: Digital button, Direct mode sets to 0 (unmuted)
                add(load_ctrl, 0, CMD_SLOT_MUTE,
                    build_cmad_button(
                        target=tgt,
                        interaction_mode=2,
                        max_output=0,
                        trigger_release=1,
                        cond1_mod=CMD_DECK_FOCUS,
                        cond1_val=FOCUS_VAL[deck],
                    ))

    return cmais, names


def main():
    parser = argparse.ArgumentParser(
        description='Generate S4 MK3 Stem Load Reset TSI')
    parser.add_argument('--source', '-s', required=True,
                        help='Source S4 MK3 TSI file (template for device definition)')
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
    new_binary = rebuild_tsi(original, ddcb, 'S4 MK3 Stem Load Reset')

    print(f"\nWriting: {args.output}")
    write_tsi(new_binary, args.output, args.source)

    verify = parse_tsi(args.output)
    verify_info = get_device_info(verify)
    print(f"  Verified: {verify_info.get('mapping_count', '?')} mappings, "
          f"comment={verify_info.get('comment', '?')!r}")
    print("Done.")


if __name__ == '__main__':
    main()
