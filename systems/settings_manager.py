# systems/settings_manager.py
# ─────────────────────────────────────────────────────────────────────────────
# Central settings store for Look Away.
# Import 'settings' from this module anywhere in the game.
# Values are session-only — they reset to defaults each launch.
# ─────────────────────────────────────────────────────────────────────────────

settings = {
    # DISPLAY
    "fullscreen":       True,
    "show_fps":         True,

    # AUDIO
    "music_volume":     0.5,    # 0.0 = mute, 1.0 = 100%
    "sfx_volume":       1.0,   # placeholder — wired up when SFX are added

    # GAMEPLAY
    "screen_shake":     True,
    "dialogue_speed":   "NORMAL",   # "NORMAL" or "FAST"
}
