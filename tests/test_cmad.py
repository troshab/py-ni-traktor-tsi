"""Tests for CMAD builders and parser."""

import struct
import pytest

from traktor_tsi.cmad import (
    build_cmad_knob,
    build_cmad_button,
    build_cmad_modifier,
    build_cmad_continuous_button,
    build_cmad_output,
    parse_cmad,
    CMAD_SIZE,
)


class TestBuildCmadKnob:
    """Tests for build_cmad_knob."""

    def test_size(self):
        assert len(build_cmad_knob()) == CMAD_SIZE

    def test_device_type_always_4(self):
        d = parse_cmad(build_cmad_knob())
        assert d['device_type'] == 4

    def test_absolute_mode_control_type_1(self):
        """Absolute mode (3) uses ControlType=1 (FaderOrKnob)."""
        d = parse_cmad(build_cmad_knob(interaction_mode=3))
        assert d['control_type'] == 1

    def test_relative_mode_control_type_2(self):
        """Relative mode (4) MUST use ControlType=2 (Encoder).

        This was Bug #1 - all 48 encoder entries in X1 MK2 were broken
        because control_type was hardcoded to 1.
        """
        d = parse_cmad(build_cmad_knob(interaction_mode=4))
        assert d['control_type'] == 2

    def test_direct_mode_control_type_1(self):
        """Direct mode (2) uses ControlType=1."""
        d = parse_cmad(build_cmad_knob(interaction_mode=2))
        assert d['control_type'] == 1

    def test_value_type_continuous(self):
        """Knobs always use value_type=2 (continuous)."""
        d = parse_cmad(build_cmad_knob())
        assert d['value_type'] == 2

    def test_target(self):
        d = parse_cmad(build_cmad_knob(target=7))
        assert d['target'] == 7

    def test_conditions(self):
        d = parse_cmad(build_cmad_knob(
            cond1_mod=2548, cond1_val=1,
            cond2_mod=2549, cond2_val=1,
        ))
        assert d['cond1_mod_cmd'] == 2548
        assert d['cond1_value'] == 1
        assert d['cond2_mod_cmd'] == 2549
        assert d['cond2_value'] == 1

    def test_led_feedback_enabled(self):
        """Knobs should have led_feedback=1."""
        d = parse_cmad(build_cmad_knob())
        assert d['led_feedback'] == 1

    def test_led_type_2(self):
        """Knobs use led_type=2."""
        d = parse_cmad(build_cmad_knob())
        assert d['led_type'] == 2


class TestBuildCmadButton:
    """Tests for build_cmad_button."""

    def test_size(self):
        assert len(build_cmad_button()) == CMAD_SIZE

    def test_control_type_0(self):
        """Buttons always use ControlType=0."""
        d = parse_cmad(build_cmad_button())
        assert d['control_type'] == 0

    def test_value_type_digital(self):
        """Buttons use value_type=1 (digital)."""
        d = parse_cmad(build_cmad_button())
        assert d['value_type'] == 1

    def test_toggle_mode(self):
        d = parse_cmad(build_cmad_button(interaction_mode=1))
        assert d['interaction_mode'] == 1

    def test_direct_mode(self):
        d = parse_cmad(build_cmad_button(interaction_mode=2))
        assert d['interaction_mode'] == 2

    def test_trigger_release(self):
        d = parse_cmad(build_cmad_button(trigger_release=1))
        assert d['trigger_release'] == 1

    def test_max_output_default(self):
        d = parse_cmad(build_cmad_button())
        assert d['max_output_raw'] == 0x3F800000

    def test_max_output_custom(self):
        d = parse_cmad(build_cmad_button(max_output=0))
        assert d['max_output_raw'] == 0

    def test_led_type_1(self):
        """Buttons use led_type=1."""
        d = parse_cmad(build_cmad_button())
        assert d['led_type'] == 1


class TestBuildCmadModifier:
    """Tests for build_cmad_modifier (latch pattern)."""

    def test_size(self):
        assert len(build_cmad_modifier()) == CMAD_SIZE

    def test_target_always_0(self):
        """Modifier entries always have target=0."""
        d = parse_cmad(build_cmad_modifier(value=3))
        assert d['target'] == 0

    def test_value_stored_in_max_output(self):
        """Modifier value is stored in max_output field."""
        d = parse_cmad(build_cmad_modifier(value=5))
        assert d['max_output_raw'] == 5

    def test_reserved36_is_1(self):
        """Field [9] (offset 36) = 1 for modifiers (differs from buttons)."""
        fields = struct.unpack('>30I', build_cmad_modifier())
        assert fields[9] == 1

    def test_encoder_mode_is_7(self):
        """Modifier max range = 7 (field [22] / offset 88)."""
        d = parse_cmad(build_cmad_modifier())
        assert d['encoder_mode'] == 7

    def test_led_feedback_enabled(self):
        d = parse_cmad(build_cmad_modifier())
        assert d['led_feedback'] == 1

    def test_latch_pattern_set(self):
        """Standard latch: set M=1 when M=0."""
        cmad = build_cmad_modifier(
            value=1,
            cond1_mod=2548, cond1_val=0,
        )
        d = parse_cmad(cmad)
        assert d['interaction_mode'] == 3
        assert d['max_output_raw'] == 1
        assert d['cond1_mod_cmd'] == 2548
        assert d['cond1_value'] == 0

    def test_latch_pattern_reset(self):
        """Standard latch: set M=0 when M=1."""
        cmad = build_cmad_modifier(
            value=0,
            cond1_mod=2548, cond1_val=1,
        )
        d = parse_cmad(cmad)
        assert d['max_output_raw'] == 0
        assert d['cond1_value'] == 1

    def test_dual_conditions(self):
        """Latch with dual conditions (e.g. stem select + column check)."""
        cmad = build_cmad_modifier(
            value=1,
            cond1_mod=2549, cond1_val=0,
            cond2_mod=2548, cond2_val=2,
        )
        d = parse_cmad(cmad)
        assert d['cond1_mod_cmd'] == 2549
        assert d['cond1_value'] == 0
        assert d['cond2_mod_cmd'] == 2548
        assert d['cond2_value'] == 2

    def test_output_scale_is_1(self):
        """Modifier entries have output_scale=1 (unlike knobs)."""
        d = parse_cmad(build_cmad_modifier())
        assert d['output_scale_raw'] == 1

    def test_override_factory_map(self):
        """Field [29] (offset 116) = 0 for Override Factory Map.

        Bug #6: was 1 (UseFactoryMap=True), causing modifier entries to NOT
        override the factory mapping. FX Assign buttons triggered native FX
        assignment instead of setting M1.
        """
        d = parse_cmad(build_cmad_modifier())
        assert d['reserved116'] == 0


class TestBuildCmadContinuousButton:
    """Tests for build_cmad_continuous_button (Bug #3 fix)."""

    def test_size(self):
        assert len(build_cmad_continuous_button()) == CMAD_SIZE

    def test_value_type_continuous(self):
        """MUST use value_type=2 for continuous params.

        Bug #3: build_cmad_button used value_type=1 (digital) which caused
        Traktor to ignore Volume/Filter/FX Amount reset commands.
        """
        d = parse_cmad(build_cmad_continuous_button())
        assert d['value_type'] == 2

    def test_control_type_button(self):
        """Still a button (ControlType=0), not a knob."""
        d = parse_cmad(build_cmad_continuous_button())
        assert d['control_type'] == 0

    def test_absolute_mode_with_volume(self):
        """Volume reset: Absolute mode, max=1.0."""
        cmad = build_cmad_continuous_button(
            target=0,
            interaction_mode=3,
            max_output=0x3F800000,
            trigger_release=1,
        )
        d = parse_cmad(cmad)
        assert d['interaction_mode'] == 3
        assert d['max_output_raw'] == 0x3F800000
        assert d['trigger_release'] == 1

    def test_filter_center(self):
        """Filter reset: 0.5 (center)."""
        cmad = build_cmad_continuous_button(
            max_output=0x3F000000,
        )
        d = parse_cmad(cmad)
        assert d['max_output_raw'] == 0x3F000000

    def test_fx_amount_zero(self):
        """FX Amount reset: 0.0."""
        cmad = build_cmad_continuous_button(max_output=0)
        d = parse_cmad(cmad)
        assert d['max_output_raw'] == 0

    def test_knob_style_fields(self):
        """Continuous button uses knob-style reserved fields."""
        d = parse_cmad(build_cmad_continuous_button())
        assert d['reserved76'] == 2
        assert d['reserved84'] == 2
        assert d['led_type'] == 2

    def test_deck_focus_condition(self):
        """S4 MK3 stem reset: conditioned on Deck Focus (cmd 203)."""
        cmad = build_cmad_continuous_button(
            target=0,
            cond1_mod=203,
            cond1_val=0,
            trigger_release=1,
        )
        d = parse_cmad(cmad)
        assert d['cond1_mod_cmd'] == 203
        assert d['cond1_value'] == 0


class TestBuildCmadOutput:
    """Tests for build_cmad_output."""

    def test_size(self):
        assert len(build_cmad_output()) == CMAD_SIZE

    def test_control_type_ffff(self):
        """Output entries use ControlType=0xFFFF."""
        d = parse_cmad(build_cmad_output())
        assert d['control_type'] == 0xFFFF

    def test_interaction_mode_8(self):
        d = parse_cmad(build_cmad_output())
        assert d['interaction_mode'] == 8

    def test_max_output_zero(self):
        """Output MaxOutput = 0 (matches community pattern)."""
        d = parse_cmad(build_cmad_output())
        assert d['max_output_raw'] == 0

    def test_invert_default(self):
        d = parse_cmad(build_cmad_output())
        assert d['invert'] == 1

    def test_invert_off(self):
        d = parse_cmad(build_cmad_output(invert=0))
        assert d['invert'] == 0

    def test_trigger_release_default_0(self):
        """All community TSIs use trigger_release=0 for output entries."""
        d = parse_cmad(build_cmad_output())
        assert d['trigger_release'] == 0

    def test_conditions_for_modifier_led(self):
        """Modifier LED: output CMD_MODIFIER_1 with cond M1=col."""
        cmad = build_cmad_output(
            target=1,
            invert=0,
            cond1_mod=2548,
            cond1_val=2,
        )
        d = parse_cmad(cmad)
        assert d['target'] == 1
        assert d['invert'] == 0
        assert d['cond1_mod_cmd'] == 2548
        assert d['cond1_value'] == 2


class TestParseCmad:
    """Tests for parse_cmad."""

    def test_roundtrip_knob(self):
        """Parse what we build - all fields should round-trip."""
        original = build_cmad_knob(
            target=5, interaction_mode=4,
            cond1_mod=2548, cond1_val=3,
            cond2_mod=2549, cond2_val=1,
        )
        d = parse_cmad(original)
        assert d['target'] == 5
        assert d['interaction_mode'] == 4
        assert d['control_type'] == 2
        assert d['cond1_mod_cmd'] == 2548
        assert d['cond1_value'] == 3

    def test_roundtrip_modifier(self):
        original = build_cmad_modifier(value=4, cond1_mod=2548, cond1_val=0)
        d = parse_cmad(original)
        assert d['max_output_raw'] == 4
        assert d['cond1_mod_cmd'] == 2548

    def test_too_short_raises(self):
        with pytest.raises(ValueError, match="too short"):
            parse_cmad(b'\x00' * 100)

    def test_exact_120_bytes(self):
        parse_cmad(b'\x00' * 120)

    def test_field_count(self):
        d = parse_cmad(build_cmad_button())
        assert len(d) == 30
