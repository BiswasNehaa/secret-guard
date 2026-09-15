# Fixture intent: Unicode + RTL (Arabic/Hebrew) text surrounding a real
# secret pattern, to prove UTF-8 decoding and byte-vs-character offsets
# don't throw off line numbers or matching.
# مرحبا بالعالم - hello world in Arabic
COMMENT = "שלום עולם"  # hello world in Hebrew
TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
EMOJI_NOISE = "🔒🔑🛡️ מפתח סודי غير حقيقي"
