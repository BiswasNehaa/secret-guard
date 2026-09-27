# Fixture intent: a secret that only exists when two lines are joined
# together. PREFIX alone is too short for the GitHub Token rule's 20-char
# minimum and below the entropy rule's minimum length; SUFFIX alone is
# long but low-entropy (all zeros). No single-line regex ever matches
# across a line break, so a default scan of this file must be clean.
PREFIX = "ghp_123456789"
SUFFIX = "0000000000000000000000000"
