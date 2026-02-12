# Voice options ported from tts-bot
TIKTOK_VOICES: list[tuple[str, str]] = [
    # Disney Characters
    ("en_us_ghostface", "Ghost Face"),
    ("en_us_c3po", "C3PO"),
    ("en_us_stitch", "Stitch"),
    ("en_us_stormtrooper", "Stormtrooper"),
    ("en_us_rocket", "Rocket"),
    ("en_female_madam_leota", "Madame Leota"),
    ("en_male_ghosthost", "Ghost Host"),
    ("en_male_pirate", "Pirate"),
    # Standard Voices
    ("en_us_001", "English US (Default)"),
    ("en_us_002", "Jessie"),
    ("en_us_006", "Joey"),
    ("en_us_007", "Professor"),
    ("en_us_009", "Scientist"),
    ("en_us_010", "Confidence"),
    # Character Voices
    ("en_male_jomboy", "Game On"),
    ("en_female_samc", "Empathetic"),
    ("en_male_cody", "Serious"),
    ("en_female_makeup", "Beauty Guru"),
    ("en_female_richgirl", "Bestie"),
    ("en_male_grinch", "Trickster"),
    ("en_male_narration", "Story Teller"),
    ("en_male_deadpool", "Mr. GoodGuy"),
    ("en_male_jarvis", "Alfred"),
    ("en_male_ashmagic", "ashmagic"),
    ("en_male_olantekkers", "olantekkers"),
    ("en_male_ukneighbor", "Lord Cringe"),
    ("en_male_ukbutler", "Mr. Meticulous"),
    ("en_female_shenna", "Debutante"),
    ("en_female_pansino", "Varsity"),
    ("en_male_trevor", "Marty"),
    ("en_female_betty", "Bae"),
    ("en_male_cupid", "Cupid"),
    ("en_female_grandma", "Granny"),
    ("en_male_wizard", "Magician"),
    # Regional Voices
    ("en_uk_001", "Narrator"),
    ("en_uk_003", "Male English UK"),
    ("en_au_001", "Metro"),
    ("en_au_002", "Smooth"),
    ("es_mx_002", "Warm"),
]

# Standard gTTS languages as fallback
GTTS_VOICES: list[tuple[str, str]] = [
    ("en", "English (gTTS)"),
    ("it", "Italian (gTTS)"),
    ("fr", "French (gTTS)"),
    ("es", "Spanish (gTTS)"),
    ("de", "German (gTTS)"),
]

ALL_VOICES: list[tuple[str, str]] = TIKTOK_VOICES + GTTS_VOICES
TIKTOK_VOICE_IDS = [v[0] for v in TIKTOK_VOICES]

TIKTOK_TTS_URL = "https://tiktok-tts.weilnet.workers.dev/api/generation"
