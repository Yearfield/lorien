# WSL Setup Notes

- Keep your repo under Linux FS, e.g., `~/projects/lorien` (avoid editing under `/mnt/c/...` for perf).
- Use a local `.venv`:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

- If Streamlit file watchers complain, we set:
```toml
# ui_streamlit/.streamlit/config.toml:
[server]
fileWatcherType = "poll"
runOnSave = false
```

- SQLite DB lives under `~/.local/share/lorien/app.db` unless `DB_PATH` overrides it.
