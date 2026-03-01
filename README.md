# py-ni-traktor-tsi

Python library for reading and writing Native Instruments Traktor Pro TSI mapping files.

## What is TSI?

TSI files are Traktor's controller mapping format. They contain XML with a Base64-encoded binary blob using a nested TLV (Tag-Length-Value) structure. This library handles the binary format so you can programmatically create and modify mappings.

## Installation

```bash
pip install -e .
```

## Usage

### Parse an existing TSI

```python
from traktor_tsi import parse_tsi, get_device_info

binary = parse_tsi("my_mapping.tsi")
info = get_device_info(binary)
print(info)
# {'name': 'Traktor.Kontrol X1 MK2.Default', 'comment': 'My Mapping', ...}
```

### Build a mapping entry

```python
from traktor_tsi import (
    build_cmai, build_cmad_button, build_ddcb,
    rebuild_tsi, write_tsi,
    CMD_SLOT_MUTE, slot_target,
)

# Mute toggle for Deck A, Stem 1
cmad = build_cmad_button(target=slot_target('A', 1), interaction_mode=1)
cmai = build_cmai(midi_idx=0, mapping_type=0, cmd_id=CMD_SLOT_MUTE, cmad_payload=cmad)

ddcb = build_ddcb([cmai], ['Left.HotCue 1'])
new_binary = rebuild_tsi(original_binary, ddcb, comment='My Stems Mapping')
write_tsi(new_binary, 'output.tsi', 'template.tsi')
```

### CMAD field reference

| Offset | Field | Description |
|--------|-------|-------------|
| 0 | DeviceType | Always 4 |
| 4 | ControlType | 0=Button, 1=Knob, 0xFFFF=Output |
| 8 | InteractionMode | 1=Toggle, 2=Direct, 3=Absolute, 8=Output |
| 12 | Target | Deck/slot/FX assignment (0-15) |
| 20 | Invert | 0 or 1 |
| 52 | Cond1ModifierCmd | Modifier command ID for condition 1 |
| 56 | Cond1Value | Required modifier value |
| 60 | Cond2Value | Condition 2 value |
| 64 | Cond2ModifierCmd | Modifier command ID for condition 2 |
| 100 | TriggerRelease | 0=on press, 1=on release |

## Example: X1 MK2 Stems

See `examples/x1_mk2_stems.py` - generates a 188-entry mapping that turns the X1 MK2 into a dedicated stems controller for 4 decks.

```bash
python -m examples.x1_mk2_stems \
    --source StemsX1MK2.tsi \
    --output X1_MK2_Stems_trosha_b.tsi
```

## Binary format

The TSI binary uses nested TLV chunks (4-byte ASCII tag + 4-byte BE length + payload):

```
DIOM > DIOI, DEVS > DEVI > DDAT > DDIF, DDIV, DDIC, DDPT, DDDC, DDCB, DVST
```

Command IDs sourced from [cmdr-editor](https://github.com/cmdr-editor/cmdr).

## License

MIT
