"""Tests for constants and helper functions."""

import pytest

from traktor_tsi.constants import (
    slot_target, fx_target, deck_target,
    remix_cell_trigger, remix_cell_state,
    CMD_MODIFIER_1, CMD_MODIFIER_8,
    CMD_SLOT_VOLUME, CMD_SLOT_FILTER, CMD_SLOT_MUTE, CMD_SLOT_FX_AMOUNT,
    CMD_FX_UNIT_ON, CMD_FX_KNOB_1, CMD_FX_KNOB_2, CMD_FX_KNOB_3,
    CMD_DECK_FOCUS, CMD_DECK_FOCUS_SELECTOR,
    CMD_PLAY, CMD_CUE, CMD_SYNC,
)


class TestSlotTarget:
    """Tests for slot_target(deck, slot)."""

    def test_deck_a_slot_1(self):
        assert slot_target('A', 1) == 0

    def test_deck_a_slot_4(self):
        assert slot_target('A', 4) == 3

    def test_deck_b_slot_1(self):
        assert slot_target('B', 1) == 4

    def test_deck_c_slot_1(self):
        assert slot_target('C', 1) == 8

    def test_deck_d_slot_4(self):
        assert slot_target('D', 4) == 15

    def test_lowercase(self):
        assert slot_target('a', 1) == 0
        assert slot_target('d', 4) == 15

    def test_all_16_targets(self):
        """All 16 slot targets (4 decks x 4 slots) are unique."""
        targets = set()
        for deck in 'ABCD':
            for slot in range(1, 5):
                targets.add(slot_target(deck, slot))
        assert targets == set(range(16))


class TestFxTarget:
    def test_unit_1(self):
        assert fx_target(1) == 0

    def test_unit_4(self):
        assert fx_target(4) == 3


class TestDeckTarget:
    def test_all_decks(self):
        assert deck_target('A') == 0
        assert deck_target('B') == 1
        assert deck_target('C') == 2
        assert deck_target('D') == 3

    def test_lowercase(self):
        assert deck_target('a') == 0


class TestRemixCellHelpers:
    def test_trigger_slot1_cell1(self):
        assert remix_cell_trigger(1, 1) == 601

    def test_trigger_slot4_cell16(self):
        assert remix_cell_trigger(4, 16) == 664

    def test_state_slot1_cell1(self):
        assert remix_cell_state(1, 1) == 665

    def test_state_slot4_cell16(self):
        assert remix_cell_state(4, 16) == 728

    def test_trigger_no_overlap_with_state(self):
        """Trigger and state ID ranges don't overlap."""
        triggers = {remix_cell_trigger(s, c) for s in range(1, 5) for c in range(1, 17)}
        states = {remix_cell_state(s, c) for s in range(1, 5) for c in range(1, 17)}
        assert len(triggers & states) == 0


class TestCommandConstants:
    """Verify key command IDs match known values from cmdr-editor."""

    def test_modifiers_sequential(self):
        assert CMD_MODIFIER_1 == 2548
        assert CMD_MODIFIER_8 == 2555

    def test_submix_commands(self):
        assert CMD_SLOT_VOLUME == 251
        assert CMD_SLOT_FILTER == 249
        assert CMD_SLOT_MUTE == 259
        assert CMD_SLOT_FX_AMOUNT == 232

    def test_fx_commands(self):
        assert CMD_FX_UNIT_ON == 369
        assert CMD_FX_KNOB_1 == 366

    def test_transport_commands(self):
        assert CMD_PLAY == 100
        assert CMD_CUE == 206
        assert CMD_SYNC == 125

    def test_deck_focus_ids(self):
        assert CMD_DECK_FOCUS == 203
        assert CMD_DECK_FOCUS_SELECTOR == 9
