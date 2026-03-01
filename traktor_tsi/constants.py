"""Traktor command IDs and mapping constants.

Command IDs sourced from cmdr-editor/cmdr KnownCommands.cs
and verified against real TSI files.
"""

# Submix / Stem controls (TargetType.Slot)
# Target encodes both deck and slot: RemixDeck1 Slot1-4 = 0-3,
# RemixDeck2 Slot1-4 = 4-7, RemixDeck3 Slot1-4 = 8-11, RemixDeck4 Slot1-4 = 12-15
CMD_SLOT_VOLUME = 251       # Submix Slot Volume Adjust
CMD_SLOT_FILTER = 249       # Submix Slot Filter Adjust
CMD_SLOT_FILTER_ON = 250    # Submix Slot Filter On
CMD_SLOT_MUTE = 259         # Submix Slot Mute On
CMD_SLOT_FX_ON = 239        # Submix Slot FX On
CMD_SLOT_FX_AMOUNT = 232    # Submix Slot FX Amount
CMD_SLOT_RETRIGGER = 260    # Submix Slot Retrigger
CMD_SLOT_PREFADER_L = 261   # Submix Slot Pre-Fader Level (L) - output only
CMD_SLOT_PREFADER_R = 262   # Submix Slot Pre-Fader Level (R) - output only
CMD_SLOT_PREFADER_LR = 361  # Submix Slot Pre-Fader Level (L+R) - output only

# Modifiers (per-device, values 0-7)
CMD_MODIFIER_1 = 2548
CMD_MODIFIER_2 = 2549
CMD_MODIFIER_3 = 2550
CMD_MODIFIER_4 = 2551
CMD_MODIFIER_5 = 2552
CMD_MODIFIER_6 = 2553
CMD_MODIFIER_7 = 2554
CMD_MODIFIER_8 = 2555

# FX Unit controls (target = FX Unit 0-3)
CMD_FX_UNIT_ON = 369
CMD_FX_DRY_WET = 365
CMD_FX_KNOB_1 = 366
CMD_FX_KNOB_2 = 367
CMD_FX_KNOB_3 = 368
CMD_FX_BUTTON_1 = 370
CMD_FX_BUTTON_2 = 371
CMD_FX_BUTTON_3 = 372
CMD_FX_EFFECT_1_SEL = 362
CMD_FX_EFFECT_2_SEL = 363
CMD_FX_EFFECT_3_SEL = 364
CMD_FX_MODE_SEL = 2301
CMD_FX_ROUTING_SEL = 325
CMD_FX_STORE_PRESET = 326
CMD_FX_LFO_RESET = 323

# Mixer FX assignment (target = channel A/B/C/D)
CMD_MIXER_FX1_ON = 321
CMD_MIXER_FX2_ON = 322
CMD_MIXER_FX3_ON = 338
CMD_MIXER_FX4_ON = 339
CMD_MIXER_FILTER_ON = 319
CMD_MIXER_FILTER_ADJ = 320
CMD_MIXER_FX_SEL = 349

# Transport (target = Deck A/B/C/D: 0-3)
CMD_PLAY = 100
CMD_CUE = 206
CMD_SYNC = 125
CMD_VOLUME = 102
CMD_GAIN = 117
CMD_CUE_MONITOR = 119


def slot_target(deck: str, slot: int) -> int:
    """Calculate Submix slot target value.

    Args:
        deck: 'A', 'B', 'C', or 'D'.
        slot: 1-4 (stem slot number).

    Returns:
        Target value 0-15.
    """
    deck_base = {'A': 0, 'B': 4, 'C': 8, 'D': 12}
    return deck_base[deck.upper()] + (slot - 1)


def fx_target(unit: int) -> int:
    """FX Unit target value (1-indexed).

    Args:
        unit: FX unit number 1-4.

    Returns:
        Target value 0-3.
    """
    return unit - 1
