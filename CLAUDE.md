# Notes for Claude sessions in this repo

- This is a **paper-trading** bot. Never place real orders, never connect a broker, and never change
  `config.json` `mode` away from `"paper"` unless the owner explicitly asks in their own words.
- Never store broker passwords, TOTP secrets or API keys in this repo.
- Run tests with `python3 -m unittest discover -s tests -v` before committing code changes.
- Daily routine: `python3 run.py paper-day`, then commit `state/` and `reports/` to `main` with a
  message like `paper-day 2026-11-09`, and push.
- Keep the strategy rules in `README.md` in sync with `config.json` and `bot/strategy.py`.
