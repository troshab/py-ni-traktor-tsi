#!/usr/bin/env python3
"""
S4 MK3 Stem Load Reset + DJ NUO Mod - TSI merge tool.

Merges the DJ NUO Loop In/Out Control mapping with stem parameter
reset on the Load (Browse.Encoder.Push) button.

When loading a track, all stem parameters (Volume, Filter, FX Amount,
Mute) for the focused deck reset to defaults. Uses NUO's M7/M8
modifiers (set by Deck Select buttons) as conditions.

Usage:
    python -m examples.s4_mk3_stem_reset_nuo \
        --nuo /path/to/DJ_NUO_Mod.tsi \
        --output /path/to/output.tsi
"""

import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from traktor_tsi import (
    parse_tsi, write_tsi, rebuild_tsi, get_device_info,
    build_cmai, build_ddcb,
    build_cmad_button, build_cmad_continuous_button,
    CMD_SLOT_VOLUME, CMD_SLOT_FILTER, CMD_SLOT_FX_AMOUNT, CMD_SLOT_MUTE,
    CMD_MODIFIER_7, CMD_MODIFIER_8, CMD_LOAD_SELECTED,
    slot_target, deck_target,
)
from traktor_tsi.tlv import parse_tlv, find_chunk
from traktor_tsi.strings import decode_utf16be_str

# NUO sets M7 from Left Deck Select (A=0, C=1) and M8 from Right (B=0, D=1).
# We condition stem reset on these modifiers.
DECK_COND = {
    'A': (CMD_MODIFIER_7, 0),
    'C': (CMD_MODIFIER_7, 1),
    'B': (CMD_MODIFIER_8, 0),
    'D': (CMD_MODIFIER_8, 1),
}

LOAD_SIDES = [
    ('Left.Browse.Encoder.Push',  ['A', 'C']),
    ('Right.Browse.Encoder.Push', ['B', 'D']),
]

# Continuous stem parameters: Absolute mode (3) with default values.
# value_type=2 (continuous) required for these commands.
CONTINUOUS_RESETS = [
    (CMD_SLOT_VOLUME,    0x3F800000),  # 1.0 (max volume)
    (CMD_SLOT_FILTER,    0x3F000000),  # 0.5 (filter center = off)
    (CMD_SLOT_FX_AMOUNT, 0),           # 0.0 (no FX send)
]


def extract_entries(binary: bytes) -> tuple[list[bytes], list[str]]:
    """Extract existing CMAI entries and control names from TSI binary.

    NHL TSIs (e.g. from CMDR editor) often have non-sequential midi_idx
    values. This function re-indexes entries to 0..N-1 while preserving
    the correct midi_idx-to-control-name binding via the DCBM lookup.

    Returns:
        (cmai_payloads, ctrl_names) - parallel lists, re-indexed.
    """
    diom_payload = find_chunk(parse_tlv(binary), 'DIOM')
    devs_payload = find_chunk(parse_tlv(diom_payload), 'DEVS')
    devi_chunks = parse_tlv(devs_payload, offset=4)
    devi_payload = find_chunk(devi_chunks, 'DEVI')

    name, rest_off = decode_utf16be_str(devi_payload, 0)
    ddat_payload = find_chunk(parse_tlv(devi_payload, offset=rest_off), 'DDAT')
    ddat_chunks = parse_tlv(ddat_payload)
    ddcb_payload = find_chunk(ddat_chunks, 'DDCB')
    ddcb_chunks = parse_tlv(ddcb_payload)

    # Build midi_idx -> control name lookup from DCBM.
    # DCBM entries may have sparse indices (e.g. 14, 16, 18, 51, ...).
    idx_to_name = {}
    dcbm_payload = find_chunk(ddcb_chunks, 'DCBM')
    for tag, payload, _ in parse_tlv(dcbm_payload, offset=4):
        if tag == 'DCBM':
            orig_idx = struct.unpack('>I', payload[:4])[0]
            ctrl_name, _ = decode_utf16be_str(payload, 4)
            idx_to_name[orig_idx] = ctrl_name

    # Extract CMAI entries, re-index to 0..N-1, resolve correct names.
    cmai_list = []
    names_list = []
    cmas_payload = find_chunk(ddcb_chunks, 'CMAS')
    new_idx = 0
    for tag, payload, _ in parse_tlv(cmas_payload, offset=4):
        if tag == 'CMAI':
            old_idx = struct.unpack('>I', payload[:4])[0]
            ctrl_name = idx_to_name.get(old_idx, f'Unknown_{old_idx}')
            # Rewrite midi_idx to sequential value
            reindexed = struct.pack('>I', new_idx) + payload[4:]
            cmai_list.append(reindexed)
            names_list.append(ctrl_name)
            new_idx += 1

    return cmai_list, names_list


def generate_stem_reset(start_idx: int) -> tuple[list[bytes], list[str]]:
    """Generate Load + stem reset mapping entries.

    Per side: 1 Load + 2 decks x 4 slots x (3 continuous + 1 mute) = 33 entries.
    2 sides = 66 entries total.

    Load Selected fires on press (trigger_release=0).
    Stem reset fires on release (trigger_release=1) after Load completes.
    """
    cmais = []
    names = []
    idx = start_idx

    for load_ctrl, decks in LOAD_SIDES:
        # Explicit Load Selected: fires on press, no condition needed.
        cmais.append(build_cmai(idx, 0, CMD_LOAD_SELECTED,
            build_cmad_button(
                interaction_mode=2,
                trigger_release=0,
            )))
        names.append(load_ctrl)
        idx += 1

        for deck in decks:
            cond_mod, cond_val = DECK_COND[deck]
            for slot in range(1, 5):
                tgt = slot_target(deck, slot)
                # Continuous params: Absolute mode with value_type=2
                for cmd, default_val in CONTINUOUS_RESETS:
                    cmais.append(build_cmai(idx, 0, cmd,
                        build_cmad_continuous_button(
                            target=tgt,
                            interaction_mode=3,
                            max_output=default_val,
                            trigger_release=1,
                            cond1_mod=cond_mod,
                            cond1_val=cond_val,
                        )))
                    names.append(load_ctrl)
                    idx += 1
                # Mute: Digital button, Direct mode sets to 0 (unmuted)
                cmais.append(build_cmai(idx, 0, CMD_SLOT_MUTE,
                    build_cmad_button(
                        target=tgt,
                        interaction_mode=2,
                        max_output=0,
                        trigger_release=1,
                        cond1_mod=cond_mod,
                        cond1_val=cond_val,
                    )))
                names.append(load_ctrl)
                idx += 1

    return cmais, names


def main():
    parser = argparse.ArgumentParser(
        description='Merge DJ NUO Mod with S4 MK3 Stem Load Reset')
    parser.add_argument('--nuo', '-n', required=True,
                        help='DJ NUO Mod TSI file (source template)')
    parser.add_argument('--output', '-o', required=True,
                        help='Output TSI file path')
    args = parser.parse_args()

    print(f"Parsing DJ NUO Mod: {args.nuo}")
    nuo_binary = parse_tsi(args.nuo)
    nuo_info = get_device_info(nuo_binary)
    print(f"  Device: {nuo_info['name']}")
    print(f"  Comment: {nuo_info.get('comment', '?')}")
    print(f"  Existing mappings: {nuo_info.get('mapping_count', '?')}")

    print("\nExtracting existing entries...")
    existing_cmais, existing_names = extract_entries(nuo_binary)
    print(f"  Extracted: {len(existing_cmais)} CMAI entries, "
          f"{len(existing_names)} control names")

    print("\nGenerating stem reset entries...")
    reset_cmais, reset_names = generate_stem_reset(
        start_idx=len(existing_cmais))
    print(f"  Generated: {len(reset_cmais)} entries")

    # Merge
    all_cmais = existing_cmais + reset_cmais
    all_names = existing_names + reset_names
    print(f"\nMerged total: {len(all_cmais)} entries")

    comment = 'S4 MK3 Stem Load Reset (+DJ NUO Loop In/Out Control)'
    ddcb = build_ddcb(all_cmais, all_names)
    new_binary = rebuild_tsi(nuo_binary, ddcb, comment)

    print(f"\nWriting: {args.output}")
    write_tsi(new_binary, args.output, args.nuo)

    verify = parse_tsi(args.output)
    verify_info = get_device_info(verify)
    print(f"  Verified: {verify_info.get('mapping_count', '?')} mappings, "
          f"comment={verify_info.get('comment', '?')!r}")
    print("Done.")


if __name__ == '__main__':
    main()
