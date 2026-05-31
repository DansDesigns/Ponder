# Ponder

A local-first search tool. Web results without tracking, local file search, and Wikipedia — all from your browser at `localhost:7000`.

## Quick start

```bash
git clone https://github.com/DansDesigns/ponder
cd ponder
chmod +x install.sh && ./install.sh
ponder
```

## Structure

```
ponder/
  main.py          FastAPI app and all routes
  config.py        Config load/save (~/.config/ponder/config.json)
  indexer.py       Whoosh local file indexer + watchdog watcher
  web_search.py    DDG / Brave / SearXNG backends
  wiki.py          Wikipedia API
  static/
    index.html     Full UI — served directly from FastAPI
  requirements.txt
  install.sh
```

## Config

Edit `~/.config/ponder/config.json` or use the in-app settings panel.

| Key | Default | Notes |
|---|---|---|
| `web_backend` | `"ddg"` | `ddg`, `brave`, or `searxng` |
| `brave_api_key` | `""` | Free at search.brave.com |
| `searxng_url` | `"http://localhost:8080"` | Your SearXNG instance |
| `watch_dirs` | `["~/Documents","~/Projects"]` | Dirs to index |
| `exclude_patterns` | `["*.pyc",".git",…]` | Glob patterns to skip |
| `max_file_mb` | `10` | Skip files larger than this |
| `port` | `7000` | Local port |
| `open_browser` | `true` | Auto-open on start |

## Supported file types

Text/code files are indexed and previewed inline. PDFs and `.docx` files are text-extracted. All other files are indexed by filename only.

## Backends

- **DuckDuckGo** — default, no setup, no API key
- **Brave Search** — cleaner results, 2 000 free queries/month — get a key at https://api.search.brave.com
- **SearXNG** — self-hosted meta-search, full privacy — https://github.com/searxng/searxng

## Running as a service (Devuan / SysVinit)

Add to `/etc/rc.local` before `exit 0`:

```bash
su -c "ponder &" YOUR_USERNAME
```

Or create an LSB init script in `/etc/init.d/` pointing to the `ponder` launcher.

## Licence

MIT
