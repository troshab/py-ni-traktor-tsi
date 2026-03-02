"""Traktor command IDs and mapping constants.

Command IDs sourced from cmdr-editor/cmdr KnownCommands.cs and the full
traktor_commands_full.csv (497 commands), verified against real TSI files.

Inline comments indicate direction:
  In/Out = bidirectional (read state + set value)
  In only = input (controller -> Traktor)
  Out only = output (Traktor -> controller LED/display)
"""

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------

# NOTE: CMD_DECK_FOCUS_SELECTOR (9) is "Deck Focus Selector" - selects which deck
# is focused in the UI (A/B/C/D). Use as condition value with cond1_mod/cond2_mod.
# CMD_DECK_FOCUS (203) is "Is In Active Loop" per cmdr, but works as Deck Focus
# condition in CMAD (confirmed in DJ NUO Mod TSI). Keep both names.
CMD_DECK_FOCUS_SELECTOR = 9    # In/Out. Deck Focus Selector: 0=A, 1=B, 2=C, 3=D.
CMD_DECK_FOCUS = 203           # Out only. "Is In Active Loop" in cmdr, but used
                               # as deck focus condition in practice: 0=A,1=B,2=C,3=D.
CMD_TOGGLE_LAST_FOCUS = 2588   # In/Out. Toggle last focused panel.
CMD_LAYOUT_SELECTOR = 4208     # In/Out. Layout Selector.
CMD_ONLY_BROWSER_ON = 4209     # In/Out. Only Browser On.
CMD_FULLSCREEN_ON = 4210       # In/Out. Fullscreen On.

# ---------------------------------------------------------------------------
# Modifiers (per-device, values 0-7)
# ---------------------------------------------------------------------------

CMD_MODIFIER_1 = 2548          # In/Out.
CMD_MODIFIER_2 = 2549          # In/Out.
CMD_MODIFIER_3 = 2550          # In/Out.
CMD_MODIFIER_4 = 2551          # In/Out.
CMD_MODIFIER_5 = 2552          # In/Out.
CMD_MODIFIER_6 = 2553          # In/Out.
CMD_MODIFIER_7 = 2554          # In/Out.
CMD_MODIFIER_8 = 2555          # In/Out.

# ---------------------------------------------------------------------------
# Mixer - X-Fader
# ---------------------------------------------------------------------------

CMD_XFADER_POSITION = 5        # In/Out. X-Fader position.
CMD_XFADER_CURVE = 14          # In/Out. X-Fader curve adjust.
CMD_XFADER_AUTO_LEFT = 2113    # In/Out. Auto X-Fade Left.
CMD_XFADER_AUTO_RIGHT = 2114   # In/Out. Auto X-Fade Right.
CMD_XFADER_ASSIGN_LEFT = 2408  # In/Out. Assign channel to left side.
CMD_XFADER_ASSIGN_RIGHT = 2409 # In/Out. Assign channel to right side.

# ---------------------------------------------------------------------------
# Mixer - Volumes / Levels
# ---------------------------------------------------------------------------

CMD_MASTER_VOLUME = 6          # In/Out. Master Volume Adjust.
CMD_MONITOR_VOLUME = 8         # In/Out. Monitor Volume Adjust.
CMD_MONITOR_MIX = 17           # In/Out. Monitor Mix Adjust.
CMD_MONITOR_CUE_ON = 119       # In/Out. Monitor Cue On.
CMD_VOLUME = 102               # In/Out. Channel Volume Adjust.
CMD_GAIN = 117                 # In/Out. Gain Adjust (Mixer).
CMD_AUTO_GAIN = 118            # In/Out. Auto-Gain Adjust.
CMD_MICROPHONE_GAIN = 295      # In/Out. Microphone Gain Adjust.
CMD_BALANCE = 127              # In/Out. Balance Adjust.
CMD_AUTO_GAIN_VIEW_ON = 2807   # In/Out. Auto-Gain View On.

# ---------------------------------------------------------------------------
# Mixer - EQ
# ---------------------------------------------------------------------------

CMD_EQ_LOW = 301               # In/Out. Low Adjust.
CMD_EQ_MID = 302               # In/Out. Mid Adjust.
CMD_EQ_HIGH = 303              # In/Out. High Adjust.
CMD_EQ_LOW_KILL = 304          # In/Out. Low Kill.
CMD_EQ_MID_KILL = 305          # In/Out. Mid Kill.
CMD_EQ_HIGH_KILL = 306         # In/Out. High Kill.
CMD_EQ_MID_LOW_KILL = 307      # In/Out. Mid Low Kill.
CMD_EQ_MID_LOW = 316           # In/Out. Mid Low Adjust.

# ---------------------------------------------------------------------------
# Mixer - FX Assignment
# ---------------------------------------------------------------------------

CMD_MIXER_FX1_ON = 321         # In/Out. FX Unit 1 On (send to unit 1).
CMD_MIXER_FX2_ON = 322         # In/Out. FX Unit 2 On.
CMD_MIXER_FX3_ON = 338         # In/Out. FX Unit 3 On.
CMD_MIXER_FX4_ON = 339         # In/Out. FX Unit 4 On.
CMD_MIXER_FILTER_ON = 319      # In/Out. Mixer FX On (inline filter/effect).
CMD_MIXER_FILTER_ADJ = 320     # In/Out. Mixer FX Adjust.
CMD_MIXER_FX_SEL = 349         # In/Out. Mixer FX Selector.
CMD_DECK_EFFECT_ON = 348       # In/Out. Deck Effect On.
CMD_LIMITER_ON = 7             # In/Out. Limiter On.

# ---------------------------------------------------------------------------
# Mixer - Meters (output only)
# ---------------------------------------------------------------------------

CMD_DECK_PREFADER_L = 2688     # Out only. Deck Pre-Fader Level (L).
CMD_DECK_PREFADER_R = 2689     # Out only. Deck Pre-Fader Level (R).
CMD_DECK_POSTFADER_L = 2690    # Out only. Deck Post-Fader Level (L).
CMD_DECK_POSTFADER_R = 2691    # Out only. Deck Post-Fader Level (R).
CMD_DECK_PREFADER_LR = 2712    # Out only. Deck Pre-Fader Level (L+R).
CMD_DECK_POSTFADER_LR = 2713   # Out only. Deck Post-Fader Level (L+R).
CMD_MIXER_LEVEL_L = 2692       # Out only. Mixer Level (L).
CMD_MIXER_LEVEL_R = 2693       # Out only. Mixer Level (R).
CMD_MASTER_OUT_L = 2694        # Out only. Master Out Level (L).
CMD_MASTER_OUT_R = 2695        # Out only. Master Out Level (R).
CMD_MASTER_OUT_CLIP_L = 2696   # Out only. Master Out Clip (L).
CMD_MASTER_OUT_CLIP_R = 2697   # Out only. Master Out Clip (R).
CMD_MASTER_OUT_LR = 2703       # Out only. Master Out Level (L+R).
CMD_MASTER_OUT_CLIP_LR = 2704  # Out only. Master Out Clip (L+R).
CMD_RECORD_IN_L = 2698         # Out only. Record Input Level (L).
CMD_RECORD_IN_R = 2699         # Out only. Record Input Level (R).
CMD_RECORD_IN_CLIP_L = 2700    # Out only. Record Input Clip (L).
CMD_RECORD_IN_CLIP_R = 2701    # Out only. Record Input Clip (R).

# ---------------------------------------------------------------------------
# FX Unit controls (target = FX Unit 0-3, i.e. unit number minus 1)
# ---------------------------------------------------------------------------

CMD_FX_UNIT_ON = 369           # In/Out. FX Unit On.
CMD_FX_DRY_WET = 365           # In/Out. Dry/Wet Adjust (FX Unit).
CMD_FX_KNOB_1 = 366            # In/Out. Knob 1.
CMD_FX_KNOB_2 = 367            # In/Out. Knob 2.
CMD_FX_KNOB_3 = 368            # In/Out. Knob 3.
CMD_FX_BUTTON_1 = 370          # In/Out. Button 1.
CMD_FX_BUTTON_2 = 371          # In/Out. Button 2.
CMD_FX_BUTTON_3 = 372          # In/Out. Button 3.
CMD_FX_EFFECT_1_SEL = 362      # In/Out. Effect 1 Selector.
CMD_FX_EFFECT_2_SEL = 363      # In/Out. Effect 2 Selector.
CMD_FX_EFFECT_3_SEL = 364      # In/Out. Effect 3 Selector.
CMD_FX_MODE_SEL = 2301         # In/Out. FX Unit Mode Selector.
CMD_FX_ROUTING_SEL = 325       # In/Out. Routing Selector.
CMD_FX_STORE_PRESET = 326      # In/Out. FX Store Preset.
CMD_FX_LFO_RESET = 323         # In/Out. Effect LFO Reset.

# ---------------------------------------------------------------------------
# Deck Common - Transport
# ---------------------------------------------------------------------------

CMD_PLAY = 100                 # In/Out. Play/Pause.
CMD_CUE = 206                  # In/Out. Cue.
CMD_CUP = 204                  # In/Out. CUP (Cue Play).
CMD_SYNC = 125                 # In/Out. Sync On.
CMD_TEMPO_SYNC = 122           # In/Out. Tempo Sync (trigger).
CMD_PHASE_SYNC = 124           # In/Out. Phase Sync (trigger).
CMD_REVERSE = 201              # In/Out. Reverse Playback On.
CMD_FLUX_ON = 2350             # In/Out. Flux Mode On.
CMD_FLUX_STATE = 2349          # Out only. Flux State.
CMD_FLUX_REVERSE = 874         # In/Out. Flux Reverse Playback On.
CMD_JOG_TURN = 120             # In/Out. Jog Turn.
CMD_JOG_SCRATCH = 121          # In/Out. Scratch (dug).
CMD_JOG_TOUCH = 2187           # In/Out. Jog Touch On.
CMD_TEMPO_ADJUST = 123         # In/Out. Tempo Adjust.
CMD_TEMPO_BEND = 406           # In/Out. Tempo Bend.
CMD_TEMPO_BEND_STEPLESS = 404  # In/Out. Tempo Bend (stepless).
CMD_TEMPO_RANGE_SEL = 19       # In/Out. Tempo Range Selector.
CMD_SEEK_POSITION = 103        # In/Out. Seek Position.
CMD_PHASE = 512                # Out only. Phase.
CMD_BEAT_PHASE = 513           # Out only. Beat Phase.
CMD_SET_TEMPO_MASTER = 2293    # In/Out. Set As Tempo Master.
CMD_DECK_IS_LOADED = 2591      # Out only. 1=loaded, 0=empty.
CMD_DECK_FLAVOR = 2302         # In/Out. 0=Track, 1=Remix, 2=Stem, 3=LiveInput.
CMD_DECK_SIZE_SEL = 2300       # In/Out. Deck Size Selector.
CMD_ADVANCED_PANEL_TAB = 2298  # In/Out. Advanced Panel Tab Selector.
CMD_ADVANCED_PANEL_TOGGLE = 2299  # In/Out. Advanced Panel Toggle.
CMD_ANALYZE_LOADED = 2798      # In/Out. Analyze Loaded Track.
CMD_LOAD_NEXT = 2176           # In/Out. Load Next.
CMD_LOAD_PREV = 2177           # In/Out. Load Previous.
CMD_LOAD_SELECTED = 3076       # In/Out. Load Selected (Deck Common).
CMD_UNLOAD = 2178              # In/Out. Unload (Deck Common).

# ---------------------------------------------------------------------------
# Deck Common - Loop
# ---------------------------------------------------------------------------

CMD_LOOP_ACTIVE_ON = 202       # In/Out. Loop Active On.
CMD_LOOP_SET = 2192            # In/Out. Loop Set (hold).
CMD_LOOP_SIZE_SEL = 2196       # In/Out. Loop Size Selector.
CMD_LOOP_SIZE_SELECT_SET = 2317   # In/Out. Loop Size Select + Set.
CMD_LOOP_BACKWARD_SIZE_SET = 2318 # In/Out. Backward Loop Size Select + Set.
CMD_LOOP_IN = 2392             # In/Out. Loop In/Set Cue.
CMD_LOOP_OUT = 2393            # In/Out. Loop Out.

# ---------------------------------------------------------------------------
# Deck Common - Move / Beatjump
# ---------------------------------------------------------------------------

CMD_MOVE = 2351                # In/Out. Move.
CMD_MOVE_SIZE_SEL = 2372       # In/Out. Size Selector (Move).
CMD_MOVE_MODE_SEL = 2391       # In/Out. Mode Selector (Move).
CMD_BEATJUMP = 2380            # In/Out. Beatjump.

# ---------------------------------------------------------------------------
# Deck Common - Freeze Mode
# ---------------------------------------------------------------------------

CMD_FREEZE_MODE_ON = 803       # In/Out. Freeze Mode On.
CMD_FREEZE_SLICE_COUNT = 802   # In/Out. Freeze Slice Count Adjust.
CMD_FREEZE_SLICE_SIZE = 804    # In/Out. Freeze Slice Size Adjust.
CMD_FREEZE_SLICE_1 = 810       # In/Out. Slice Trigger 1.
CMD_FREEZE_SLICE_2 = 811       # In/Out. Slice Trigger 2.
CMD_FREEZE_SLICE_3 = 812       # In/Out. Slice Trigger 3.
CMD_FREEZE_SLICE_4 = 813       # In/Out. Slice Trigger 4.
CMD_FREEZE_SLICE_5 = 814       # In/Out. Slice Trigger 5.
CMD_FREEZE_SLICE_6 = 815       # In/Out. Slice Trigger 6.
CMD_FREEZE_SLICE_7 = 816       # In/Out. Slice Trigger 7.
CMD_FREEZE_SLICE_8 = 817       # In/Out. Slice Trigger 8.
CMD_FREEZE_SLICE_9 = 818       # In/Out. Slice Trigger 9.
CMD_FREEZE_SLICE_10 = 819      # In/Out. Slice Trigger 10.
CMD_FREEZE_SLICE_11 = 820      # In/Out. Slice Trigger 11.
CMD_FREEZE_SLICE_12 = 821      # In/Out. Slice Trigger 12.
CMD_FREEZE_SLICE_13 = 822      # In/Out. Slice Trigger 13.
CMD_FREEZE_SLICE_14 = 823      # In/Out. Slice Trigger 14.
CMD_FREEZE_SLICE_15 = 824      # In/Out. Slice Trigger 15.
CMD_FREEZE_SLICE_16 = 825      # In/Out. Slice Trigger 16.

# ---------------------------------------------------------------------------
# Deck Common - Timecode / Scratch Control
# ---------------------------------------------------------------------------

CMD_SCRATCH_CONTROL_ON = 2288  # In/Out. Scratch Control On.
CMD_PLAYBACK_MODE = 5129       # In/Out. Playback Mode Int/Rel/Abs.
CMD_PLATTER_SCOPE_VIEW = 2305  # In/Out. Platter/Scope View Selector.
CMD_CALIBRATE = 5144           # In/Out. Calibrate.
CMD_RESET_TEMPO_OFFSET = 5154  # In/Out. Reset Tempo Offset.

# ---------------------------------------------------------------------------
# Track Deck - Cue / Hotcue
# ---------------------------------------------------------------------------

CMD_HOTCUE_JUMP = 209          # In/Out. Jump to active Cue Point (quantized).
CMD_HOTCUE_SET_NEXT = 213      # In/Out. Set Cue And Store As Next Hotcue.
CMD_HOTCUE_JUMP_NEXT_PREV = 2306  # In/Out. Jump To Next/Prev Cue/Loop.
CMD_HOTCUE_STORE_FLOATING = 2308  # In/Out. Store Floating Cue/Loop As Next Hotcue.
CMD_HOTCUE_DELETE_CURRENT = 2309  # In/Out. Delete Current Hotcue.
CMD_HOTCUE_MAP = 2315          # In/Out. Map Hotcue.
CMD_HOTCUE_CUE_TYPE_SEL = 2327   # In/Out. Cue Type Selector.
CMD_HOTCUE_SELECT_SET_STORE = 2328  # In/Out. Select/Set+Store Hotcue.
CMD_HOTCUE_DELETE = 2331       # In/Out. Delete Hotcue.
CMD_HOTCUE_1_TYPE = 2333       # Out only. Hotcue 1 Type.
CMD_HOTCUE_2_TYPE = 2334       # Out only. Hotcue 2 Type.
CMD_HOTCUE_3_TYPE = 2335       # Out only. Hotcue 3 Type.
CMD_HOTCUE_4_TYPE = 2336       # Out only. Hotcue 4 Type.
CMD_HOTCUE_5_TYPE = 2337       # Out only. Hotcue 5 Type.
CMD_HOTCUE_6_TYPE = 2338       # Out only. Hotcue 6 Type.
CMD_HOTCUE_7_TYPE = 2339       # Out only. Hotcue 7 Type.
CMD_HOTCUE_8_TYPE = 2340       # Out only. Hotcue 8 Type.

# ---------------------------------------------------------------------------
# Track Deck - Key / Pitch
# ---------------------------------------------------------------------------

CMD_KEYLOCK_ON = 400           # In/Out. Keylock On.
CMD_KEYLOCK_PRESERVE = 405     # In/Out. Keylock On (Preserve Pitch).
CMD_KEY_ADJUST = 402           # In/Out. Key Adjust.
CMD_SEMITONE_UP_DOWN = 403     # In/Out. Semitone Up/Down.

# ---------------------------------------------------------------------------
# Track Deck - Grid / BPM
# ---------------------------------------------------------------------------

CMD_AUTOGRID = 2237            # In/Out. Autogrid.
CMD_BPM_ADJUST = 2238          # In/Out. BPM Adjust.
CMD_BEAT_TAP = 2240            # In/Out. Beat Tap (Track Deck - Grid).
CMD_BPM_LOCK_ON = 2241         # In/Out. BPM Lock On.
CMD_GRID_MARKER_SET = 2248     # In/Out. Set Grid Marker.
CMD_GRID_MARKER_DELETE = 2249  # In/Out. Delete Grid Marker.
CMD_GRID_TICK_ON = 2252        # In/Out. Tick On (Track Deck - Grid).
CMD_GRID_MARKER_MOVE = 2253    # In/Out. Move Grid Marker.
CMD_BPM_RESET = 2254           # In/Out. Reset BPM.
CMD_COPY_PHASE_FROM_MASTER = 2255  # In/Out. Copy Phase From Tempo Master.
CMD_BPM_X2 = 2258              # In/Out. BPM x2.
CMD_BPM_DIV2 = 2259            # In/Out. BPM /2.

# ---------------------------------------------------------------------------
# Track Deck - Misc
# ---------------------------------------------------------------------------

CMD_TRACK_END_WARNING = 520    # Out only. Track End Warning.
CMD_POST_FADEOUT_MARKER = 522  # In/Out. Post Fade-Out Marker (dug).
CMD_WAVEFORM_ZOOM = 4162       # In/Out. Waveform Zoom Adjust.
CMD_DAW_VIEW = 4163            # In/Out. DAW View.
CMD_LOAD_LOOP_AND_PLAY = 2395  # In/Out. Load Loop and Play.
CMD_DUPLICATE_DECK_A = 2401    # In/Out. Duplicate Track Deck A.
CMD_DUPLICATE_DECK_B = 2402    # In/Out. Duplicate Track Deck B.
CMD_DUPLICATE_DECK_C = 2403    # In/Out. Duplicate Track Deck C.
CMD_DUPLICATE_DECK_D = 2404    # In/Out. Duplicate Track Deck D.

# ---------------------------------------------------------------------------
# Submix / Stem controls (target encodes deck + slot)
# DeckA slots 1-4 = 0-3, DeckB = 4-7, DeckC = 8-11, DeckD = 12-15.
# Use slot_target(deck, slot) helper below.
# ---------------------------------------------------------------------------

CMD_SLOT_VOLUME = 251          # In/Out. Submix Slot Volume Adjust.
CMD_SLOT_FILTER = 249          # In/Out. Submix Slot Filter Adjust.
CMD_SLOT_FILTER_ON = 250       # In/Out. Submix Slot Filter On.
CMD_SLOT_MUTE = 259            # In/Out. Submix Slot Mute On.
CMD_SLOT_FX_ON = 239           # In/Out. Submix Slot FX On.
CMD_SLOT_FX_AMOUNT = 232       # In/Out. Submix Slot FX Amount.
CMD_SLOT_RETRIGGER = 260       # In/Out. Submix Slot Retrigger.
CMD_SLOT_PREFADER_L = 261      # Out only. Submix Slot Pre-Fader Level (L).
CMD_SLOT_PREFADER_R = 262      # Out only. Submix Slot Pre-Fader Level (R).
CMD_SLOT_PREFADER_LR = 361     # Out only. Submix Slot Pre-Fader Level (L+R).

# ---------------------------------------------------------------------------
# Remix Deck
# ---------------------------------------------------------------------------

CMD_REMIX_QUANTIZE_SEL = 229   # In/Out. Quantize Selector.
CMD_REMIX_QUANTIZE_ON = 230    # In/Out. Quantize On.
CMD_REMIX_LOAD_SET = 233       # In/Out. Load Set From List.
CMD_REMIX_SAVE_SET = 234       # In/Out. Save Remix Set.
CMD_REMIX_SLOT_PUNCH = 235     # In/Out. Slot Punch On.
CMD_REMIX_SLOT_STOP_DELETE_LOAD = 236  # In/Out. Slot Stop/Delete/Load From List.
CMD_REMIX_SLOT_KEYLOCK = 237   # In/Out. Slot Keylock On.
CMD_REMIX_SLOT_MONITOR = 238   # In/Out. Slot Monitor On.
CMD_REMIX_DECK_PLAY = 241      # In/Out. Deck Play (Remix Deck, dug).
CMD_REMIX_SLOT_STATE = 247     # Out only. Slot State.
CMD_REMIX_PLAY_MODE_ALL = 242  # In/Out. Play Mode All Slots.
CMD_REMIX_SLOT_LOAD = 244      # In/Out. Slot Load From List (Legacy).
CMD_REMIX_SLOT_CAPTURE = 245   # In/Out. Slot Capture From Deck (Legacy).
CMD_REMIX_SLOT_UNLOAD = 246    # In/Out. Slot Unload (Legacy).
CMD_REMIX_PLAY_ALL = 255       # In/Out. Play All Slots (Legacy).
CMD_REMIX_TRIGGER_ALL = 256    # In/Out. Trigger All Slots (Legacy).
CMD_REMIX_SLOT_RETRIGGER_PLAY = 258  # In/Out. Slot Retrigger Play (Legacy).
CMD_REMIX_SLOT_CAPTURE_LOOP = 263   # In/Out. Slot Capture From Loop Recorder.
CMD_REMIX_SLOT_COPY = 264      # In/Out. Slot Copy From Slot.
CMD_REMIX_SLOT_PLAY_MODE = 265 # In/Out. Slot Play Mode.
CMD_REMIX_SLOT_SIZE_X2 = 266   # In/Out. Slot Size x2 (Legacy).
CMD_REMIX_SLOT_SIZE_DIV2 = 267 # In/Out. Slot Size /2 (Legacy).
CMD_REMIX_SLOT_SIZE_RESET = 268  # In/Out. Slot Size Reset (Legacy).
CMD_REMIX_SIZE_ADJUST = 2000   # In/Out. Slot Size Adjust (Legacy).
CMD_REMIX_CAPTURE_SRC_SEL = 2002  # In/Out. Capture Source Selector.
CMD_REMIX_SLOT_TRIGGER_TYPE = 2003  # In/Out. Slot Trigger Type.
CMD_REMIX_SLOT_CAPTURE_TRIGGER_MUTE = 2004  # In/Out. Slot Capture/Trigger/Mute.
CMD_REMIX_SAMPLE_PAGE_SEL = 733  # In/Out. Sample Page Selector.

# Remix Deck - Direct Mapping modifiers
CMD_REMIX_CELL_LOAD_MOD = 729  # In/Out. Cell Load Modifier.
CMD_REMIX_CELL_DELETE_MOD = 730  # In/Out. Cell Delete Modifier.
CMD_REMIX_CELL_REVERSE_MOD = 731  # In/Out. Cell Reverse Modifier.
CMD_REMIX_CELL_CAPTURE_MOD = 732  # In/Out. Cell Capture Modifier.

# Remix Deck - Step Sequencer
CMD_REMIX_SEQ_ON = 734         # In/Out. Sequencer On.
CMD_REMIX_SEQ_SWING = 735      # In/Out. Swing Amount.
CMD_REMIX_SEQ_CURRENT_STEP = 736  # Out only. Current Step.
CMD_REMIX_SEQ_PATTERN_LEN = 738   # In/Out. Pattern Length.
CMD_REMIX_SEQ_SELECTED_SAMPLE = 740  # In/Out. Selected Sample.
CMD_REMIX_SEQ_STEP_1 = 741     # In/Out. Enable Step 1.
CMD_REMIX_SEQ_STEP_2 = 742     # In/Out. Enable Step 2.
CMD_REMIX_SEQ_STEP_3 = 743     # In/Out. Enable Step 3.
CMD_REMIX_SEQ_STEP_4 = 744     # In/Out. Enable Step 4.
CMD_REMIX_SEQ_STEP_5 = 745     # In/Out. Enable Step 5.
CMD_REMIX_SEQ_STEP_6 = 746     # In/Out. Enable Step 6.
CMD_REMIX_SEQ_STEP_7 = 747     # In/Out. Enable Step 7.
CMD_REMIX_SEQ_STEP_8 = 748     # In/Out. Enable Step 8.
CMD_REMIX_SEQ_STEP_9 = 749     # In/Out. Enable Step 9.
CMD_REMIX_SEQ_STEP_10 = 750    # In/Out. Enable Step 10.
CMD_REMIX_SEQ_STEP_11 = 751    # In/Out. Enable Step 11.
CMD_REMIX_SEQ_STEP_12 = 752    # In/Out. Enable Step 12.
CMD_REMIX_SEQ_STEP_13 = 753    # In/Out. Enable Step 13.
CMD_REMIX_SEQ_STEP_14 = 754    # In/Out. Enable Step 14.
CMD_REMIX_SEQ_STEP_15 = 755    # In/Out. Enable Step 15.
CMD_REMIX_SEQ_STEP_16 = 756    # In/Out. Enable Step 16.

# Remix Deck - Direct Mapping cell triggers and states (128 entries, skipped individually)
# Slot 1 Cell 1-16 Trigger: IDs 601-616
# Slot 2 Cell 1-16 Trigger: IDs 617-632
# Slot 3 Cell 1-16 Trigger: IDs 633-648
# Slot 4 Cell 1-16 Trigger: IDs 649-664
# Slot 1 Cell 1-16 State:   IDs 665-680
# Slot 2 Cell 1-16 State:   IDs 681-696
# Slot 3 Cell 1-16 State:   IDs 697-712
# Slot 4 Cell 1-16 State:   IDs 713-728
# Use formula: CMD_REMIX_SLOT_CELL_TRIGGER_BASE + (slot-1)*16 + (cell-1)
CMD_REMIX_SLOT1_CELL_TRIGGER_BASE = 601
CMD_REMIX_SLOT2_CELL_TRIGGER_BASE = 617
CMD_REMIX_SLOT3_CELL_TRIGGER_BASE = 633
CMD_REMIX_SLOT4_CELL_TRIGGER_BASE = 649
CMD_REMIX_SLOT1_CELL_STATE_BASE = 665
CMD_REMIX_SLOT2_CELL_STATE_BASE = 681
CMD_REMIX_SLOT3_CELL_STATE_BASE = 697
CMD_REMIX_SLOT4_CELL_STATE_BASE = 713

# ---------------------------------------------------------------------------
# Loop Recorder
# ---------------------------------------------------------------------------

CMD_LOOP_REC_RECORD = 280      # In/Out. Record.
CMD_LOOP_REC_SIZE = 281        # In/Out. Size.
CMD_LOOP_REC_DRY_WET = 282     # In/Out. Dry/Wet Adjust.
CMD_LOOP_REC_PLAY = 283        # In/Out. Play/Pause.
CMD_LOOP_REC_DELETE = 284      # In/Out. Delete.
CMD_LOOP_REC_POSITION = 286    # Out only. Playback Position.
CMD_LOOP_REC_UNDO_REDO = 287   # In/Out. Undo/Redo.
CMD_LOOP_REC_UNDO_STATE = 288  # Out only. Undo State.
CMD_LOOP_REC_STATE = 289       # Out only. State.

# ---------------------------------------------------------------------------
# Master Clock
# ---------------------------------------------------------------------------

CMD_MASTER_CLOCK_AUTO = 60     # In/Out. Auto Master Mode.
CMD_MASTER_CLOCK_INT_EXT = 62  # In/Out. Clock Int/Ext.
CMD_MASTER_TEMPO_SET = 64      # In/Out. Set Master Tempo.
CMD_MASTER_TEMPO_SEL = 69      # In/Out. Master Tempo Selector.
CMD_MASTER_CLOCK_SEND = 2468   # In/Out. Clock Send.
CMD_MASTER_BEAT_TAP = 2469     # In/Out. Beat Tap (Master Clock).
CMD_MASTER_TICK_ON = 2470      # In/Out. Tick On (Master Clock).
CMD_MASTER_MIDI_SYNC = 2473    # In/Out. Clock Trigger MIDI Sync.
CMD_MASTER_TEMPO_BEND_UP = 2476    # In/Out. Tempo Bend Up.
CMD_MASTER_TEMPO_BEND_DOWN = 2477  # In/Out. Tempo Bend Down.
CMD_MASTER_RESET_DOWNBEAT = 2811   # In/Out. Reset Downbeat (Ableton Link).

# ---------------------------------------------------------------------------
# Preview Player
# ---------------------------------------------------------------------------

CMD_PREVIEW_PLAY = 210         # In/Out. Play/Pause (Preview Player).
CMD_PREVIEW_SEEK = 211         # In/Out. Seek Position (Preview Player).
CMD_PREVIEW_UNLOAD = 2179      # In/Out. Unload (Preview Player).
CMD_PREVIEW_LOAD_SELECTED = 3137  # In/Out. Load Selected (Preview Player).
CMD_PREVIEW_LOAD_TO_DECK = 3139   # In/Out. Load Preview Player into Deck.

# ---------------------------------------------------------------------------
# Audio Recorder
# ---------------------------------------------------------------------------

CMD_AUDIO_REC_GAIN = 29        # In/Out. Gain Adjust (Audio Recorder).
CMD_AUDIO_REC_CUT = 2055       # In/Out. Cut.
CMD_AUDIO_REC_RECORD = 2056    # In/Out. Record/Stop.
CMD_AUDIO_REC_LOAD_LAST = 3084 # In/Out. Load Last Recording.

# ---------------------------------------------------------------------------
# Global MIDI Controls
# ---------------------------------------------------------------------------

CMD_MIDI_BUTTON_1 = 850        # In/Out. MIDI Button 1.
CMD_MIDI_BUTTON_2 = 851        # In/Out. MIDI Button 2.
CMD_MIDI_BUTTON_3 = 852        # In/Out. MIDI Button 3.
CMD_MIDI_BUTTON_4 = 853        # In/Out. MIDI Button 4.
CMD_MIDI_BUTTON_5 = 854        # In/Out. MIDI Button 5.
CMD_MIDI_BUTTON_6 = 855        # In/Out. MIDI Button 6.
CMD_MIDI_BUTTON_7 = 856        # In/Out. MIDI Button 7.
CMD_MIDI_BUTTON_8 = 857        # In/Out. MIDI Button 8.
CMD_MIDI_KNOB_1 = 858          # In/Out. MIDI Knob 1.
CMD_MIDI_KNOB_2 = 859          # In/Out. MIDI Knob 2.
CMD_MIDI_KNOB_3 = 860          # In/Out. MIDI Knob 3.
CMD_MIDI_KNOB_4 = 861          # In/Out. MIDI Knob 4.
CMD_MIDI_KNOB_5 = 862          # In/Out. MIDI Knob 5.
CMD_MIDI_KNOB_6 = 863          # In/Out. MIDI Knob 6.
CMD_MIDI_KNOB_7 = 864          # In/Out. MIDI Knob 7.
CMD_MIDI_KNOB_8 = 865          # In/Out. MIDI Knob 8.
CMD_MIDI_FADER_1 = 866         # In/Out. MIDI Fader 1.
CMD_MIDI_FADER_2 = 867         # In/Out. MIDI Fader 2.
CMD_MIDI_FADER_3 = 868         # In/Out. MIDI Fader 3.
CMD_MIDI_FADER_4 = 869         # In/Out. MIDI Fader 4.
CMD_MIDI_FADER_5 = 870         # In/Out. MIDI Fader 5.
CMD_MIDI_FADER_6 = 871         # In/Out. MIDI Fader 6.
CMD_MIDI_FADER_7 = 872         # In/Out. MIDI Fader 7.
CMD_MIDI_FADER_8 = 873         # In/Out. MIDI Fader 8.

# ---------------------------------------------------------------------------
# Global
# ---------------------------------------------------------------------------

CMD_BROADCASTING_ON = 2057     # In/Out. Broadcasting On.
CMD_SNAP_ON = 2311             # In/Out. Snap On.
CMD_QUANT_ON = 2313            # In/Out. Quantize On (Global).
CMD_SHOW_SLIDER_VALUES = 2748  # In/Out. Show Slider Values On.
CMD_TOOL_TIPS_ON = 4211        # In/Out. Tool Tips On.
CMD_SEND_MONITOR_STATE = 3048  # In/Out. Send Monitor State.
CMD_SAVE_SETTINGS = 3072       # In/Out. Save Traktor Settings.
CMD_CRUISE_MODE_ON = 8194      # In/Out. Cruise Mode On.

# ---------------------------------------------------------------------------
# Browser - List
# ---------------------------------------------------------------------------

CMD_BROWSER_LIST_SELECT = 3200       # In/Out. Select Up/Down.
CMD_BROWSER_LIST_PAGE_SELECT = 3201  # In/Out. Select Page Up/Down.
CMD_BROWSER_LIST_TOP_BOTTOM = 3202   # In/Out. Select Top/Bottom.
CMD_BROWSER_LIST_EXTEND_SEL = 3203   # In/Out. Select Extend Up/Down.
CMD_BROWSER_LIST_EXTEND_PAGE = 3204  # In/Out. Select Extend Page Up/Down.
CMD_BROWSER_LIST_EXTEND_TOP = 3205   # In/Out. Select Extend Top/Bottom.
CMD_BROWSER_LIST_SELECT_ALL = 3206   # In/Out. Select All.
CMD_BROWSER_LIST_DELETE = 3211       # In/Out. Delete.
CMD_BROWSER_LIST_RESET_PLAYED = 3212 # In/Out. Reset Played-State.
CMD_BROWSER_LIST_ANALYZE = 3213      # In/Out. Analyze.
CMD_BROWSER_LIST_EDIT = 3215         # In/Out. Edit.
CMD_BROWSER_LIST_RELOCATE = 3216     # In/Out. Relocate.
CMD_BROWSER_LIST_ADD_TO_COLL = 3217  # In/Out. Add As Track To Collection.
CMD_BROWSER_LIST_SEARCH = 3221       # In/Out. Search.
CMD_BROWSER_LIST_SEARCH_CLEAR = 3222 # In/Out. Search Clear.
CMD_BROWSER_LIST_EXPAND_REMIX = 3223 # In/Out. Expand Remix Set.
CMD_BROWSER_LIST_CLEAR = 3224        # In/Out. Clear.
CMD_BROWSER_LIST_ANALYSIS_LOCK = 3231   # In/Out. Analysis Lock.
CMD_BROWSER_LIST_ANALYSIS_UNLOCK = 3232 # In/Out. Analysis Unlock.
CMD_BROWSER_LIST_CONSOLIDATE = 3172  # In/Out. Consolidate.
CMD_BROWSER_LIST_SEARCH_PLAYLISTS = 3357  # In/Out. Search In Playlists.
CMD_BROWSER_LIST_SHOW_IN_EXPLORER = 3358  # In/Out. Show In Explorer.
CMD_BROWSER_LIST_JUMP_TO_CURRENT = 3366   # In/Out. Jump To Current Track.
CMD_BROWSER_LIST_APPEND_PREP = 3460       # In/Out. Append To Preparation List.
CMD_BROWSER_LIST_ADD_NEXT_PREP = 3461     # In/Out. Add As Next To Preparation List.
CMD_BROWSER_LIST_ADD_REMOVE_PREP = 3480   # In/Out. Add or Remove Track from Preparation List.
CMD_BROWSER_LIST_ADD_LOOP_COLL = 3469     # In/Out. Add As Loop To Collection.
CMD_BROWSER_LIST_ADD_ONESHOT_COLL = 3470  # In/Out. Add As One-Shot Sample To Collection.
CMD_BROWSER_LIST_SET_TRACK = 3472         # In/Out. Set To Track.
CMD_BROWSER_LIST_SET_LOOPED = 3473        # In/Out. Set To Looped Sample.
CMD_BROWSER_LIST_SET_ONESHOT = 3474       # In/Out. Set To One-Shot Sample.
CMD_BROWSER_LIST_EXPORT_REMIX = 3475      # In/Out. Export As Remix Set.

# ---------------------------------------------------------------------------
# Browser - Tree
# ---------------------------------------------------------------------------

CMD_BROWSER_TREE_SELECT = 3328        # In/Out. Select Up/Down.
CMD_BROWSER_TREE_EXPAND = 3329        # In/Out. Select Expand/Collapse.
CMD_BROWSER_TREE_DELETE = 3336        # In/Out. Delete.
CMD_BROWSER_TREE_RESET_PLAYED = 3337  # In/Out. Reset Played-State.
CMD_BROWSER_TREE_ANALYZE = 3338       # In/Out. Analyze.
CMD_BROWSER_TREE_EDIT = 3339          # In/Out. Edit.
CMD_BROWSER_TREE_RELOCATE = 3340      # In/Out. Relocate.
CMD_BROWSER_TREE_IMPORT_FOLDERS = 3345  # In/Out. Import Music Folders.
CMD_BROWSER_TREE_EXPORT = 3346          # In/Out. Export.
CMD_BROWSER_TREE_EXPORT_PRINT = 3348    # In/Out. Export Printable.
CMD_BROWSER_TREE_RENAME = 3349          # In/Out. Rename Playlist Or Folder.
CMD_BROWSER_TREE_IMPORT_COLL = 3353     # In/Out. Import Collection.
CMD_BROWSER_TREE_SAVE_COLL = 3214       # In/Out. Save Collection.
CMD_BROWSER_TREE_CHECK_CONSISTENCY = 3077  # In/Out. Check Consistency.
CMD_BROWSER_TREE_REFRESH_EXPLORER = 3233   # In/Out. Refresh Explorer Folder Content.
CMD_BROWSER_TREE_RESTORE_AUTOGAIN = 3367   # In/Out. Restore AutoGain.
CMD_BROWSER_TREE_CREATE_PLAYLIST = 3373    # In/Out. Create Playlist.
CMD_BROWSER_TREE_DELETE_PLAYLIST = 3374    # In/Out. Delete Playlist.
CMD_BROWSER_TREE_CREATE_FOLDER = 3375      # In/Out. Create Playlist Folder.
CMD_BROWSER_TREE_DELETE_FOLDER = 3376      # In/Out. Delete Playlist Folder.
CMD_BROWSER_TREE_ADD_MUSIC_FOLDER = 3458   # In/Out. Add Folder To Music Folders.
CMD_BROWSER_TREE_ANALYSIS_LOCK = 3477      # In/Out. Analysis Lock.
CMD_BROWSER_TREE_ANALYSIS_UNLOCK = 3478    # In/Out. Analysis Unlock.

# ---------------------------------------------------------------------------
# Browser - Favorites
# ---------------------------------------------------------------------------

CMD_BROWSER_FAVORITES_SEL = 3456      # In/Out. Selector (Browser Favorites).
CMD_BROWSER_FAVORITES_ADD_FOLDER = 3457  # In/Out. Add Folder To Favorites.

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


def deck_target(deck: str) -> int:
    """Deck target value for transport/mixer commands.

    Args:
        deck: 'A', 'B', 'C', or 'D'.

    Returns:
        Target value 0-3.
    """
    return {'A': 0, 'B': 1, 'C': 2, 'D': 3}[deck.upper()]


def remix_cell_trigger(slot: int, cell: int) -> int:
    """Remix Deck Direct Mapping cell trigger command ID.

    Args:
        slot: Slot number 1-4.
        cell: Cell number 1-16.

    Returns:
        Command ID.
    """
    base = {1: 601, 2: 617, 3: 633, 4: 649}
    return base[slot] + (cell - 1)


def remix_cell_state(slot: int, cell: int) -> int:
    """Remix Deck Direct Mapping cell state command ID (output only).

    Args:
        slot: Slot number 1-4.
        cell: Cell number 1-16.

    Returns:
        Command ID.
    """
    base = {1: 665, 2: 681, 3: 697, 4: 713}
    return base[slot] + (cell - 1)
