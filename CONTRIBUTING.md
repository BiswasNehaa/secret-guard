# Contributing to secret-guard

Thanks for helping make secret-guard better! Every PR counts, no matter how
small.

## Getting started

```bash
git clone https://github.com/taksh1507/secret-guard.git
cd secret-guard
python -m unittest discover -s tests -v
```

## How to add a detection rule

1. Open `secretguard/rules.py`.
2. Add a `_r(...)` entry with a regex, name, `severity` (`low`, `medium`,
   `high`, `critical`) and a description.
3. Add a matching test in `tests/test_rules.py` using a realistic sample.
4. Run the test suite and make sure everything passes.

### Rule-writing tips

- Make patterns specific enough to avoid false positives.
- Never match on the generic word `password` alone — require an assignment
  shape (`password = ...`) and a non-trivial value.
- For patterns that vary, prefer entropy detection over a brittle regex.

## Issues and PRs

- Use clear, descriptive titles.
- Keep PRs focused on one change.
- Add tests for new behavior.

## Code of conduct

Be kind and constructive. That's it.