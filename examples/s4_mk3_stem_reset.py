#!/usr/bin/env python3
"""
S4 MK3 Stem Load Reset - TSI mapping generator.

Adds stem parameter reset to the Load (Browse.Encoder.Push) button
on the Traktor Kontrol S4 MK3. When loading a track, all stem
parameters (Volume, Filter, FX Amount, Mute) for the focused deck
reset to defaults.

Uses M7/M8 modifiers set by Deck Select buttons as conditions:
  Left.Deck Select.A -> M7=0, Left.Deck Select.C -> M7=1
  Right.Deck Select.B -> M8=0, Right.Deck Select.D -> M8=1

Adds explicit Load Selected command (on press) so native Load works
even when custom mappings are added to Browse.Encoder.Push.
Stem reset fires on release (after Load completes).

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
    build_cmad_button, build_cmad_modifier, build_cmad_continuous_button,
    CMD_SLOT_VOLUME, CMD_SLOT_FILTER, CMD_SLOT_FX_AMOUNT, CMD_SLOT_MUTE,
    CMD_MODIFIER_7, CMD_MODIFIER_8, CMD_LOAD_SELECTED,
    slot_target, deck_target,
)

# M7 tracks left side focus: A=0, C=1 (set by Deck Select buttons)
# M8 tracks right side focus: B=0, D=1
DECK_COND = {
    'A': (CMD_MODIFIER_7, 0),
    'C': (CMD_MODIFIER_7, 1),
    'B': (CMD_MODIFIER_8, 0),
    'D': (CMD_MODIFIER_8, 1),
}

# Deck Select buttons set M7/M8 to track which deck is focused per side.
DECK_SELECT_ENTRIES = [
    ('Left.Deck Select.A',  CMD_MODIFIER_7, 0),
    ('Left.Deck Select.C',  CMD_MODIFIER_7, 1),
    ('Right.Deck Select.B', CMD_MODIFIER_8, 0),
    ('Right.Deck Select.D', CMD_MODIFIER_8, 1),
]

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

    4 Deck Select entries (set M7/M8) +
    Per side: 1 Load + 2 decks x 4 slots x (3 continuous + 1 mute) = 33 entries.
    Total: 4 + 2x33 = 70 entries.

    Load Selected fires on press (trigger_release=0) to replicate native Load.
    Stem reset fires on release (trigger_release=1) after Load completes.
    Each conditioned on M7/M8 matching the target deck.
    """
    cmais = []
    names = []
    idx = 0

    def add(ctrl_name, mapping_type, cmd_id, cmad):
        nonlocal idx
        cmais.append(build_cmai(idx, mapping_type, cmd_id, cmad))
        names.append(ctrl_name)
        idx += 1

    # Deck Select buttons set M7/M8 to track deck focus per side
    for ctrl_name, mod_cmd, mod_val in DECK_SELECT_ENTRIES:
        add(ctrl_name, 0, mod_cmd,
            build_cmad_modifier(value=mod_val, interaction_mode=3))

    for load_ctrl, decks in LOAD_SIDES:
        # Explicit Load Selected: fires on press, no condition needed.
        add(load_ctrl, 0, CMD_LOAD_SELECTED,
            build_cmad_button(
                interaction_mode=2,
                trigger_release=0,
            ))

        for deck in decks:
            cond_mod, cond_val = DECK_COND[deck]
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
                            cond1_mod=cond_mod,
                            cond1_val=cond_val,
                        ))
                # Mute: Digital button, Direct mode sets to 0 (unmuted)
                add(load_ctrl, 0, CMD_SLOT_MUTE,
                    build_cmad_button(
                        target=tgt,
                        interaction_mode=2,
                        max_output=0,
                        trigger_release=1,
                        cond1_mod=cond_mod,
                        cond1_val=cond_val,
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
