# Ponder

A local-first search app. Search the web, images, video, maps, Wikipedia and your own files — all from a clean browser UI at `http://localhost:7000`. No accounts, no tracking, no ads.

![Ponder](static/logo.png)

---

## Features

- **Web search** — parallel multi-source pipeline (Mojeek, Stract, DuckDuckGo) with automatic fallback tiers
- **Image search** — Openverse, Wikimedia Commons, Wikipedia article images
- **Video search** — DuckDuckGo video results
- **Maps** — OpenStreetMap / Nominatim geocoding, open in OSM or Google Maps
- **Wikipedia** — inline article summaries + full search results
- **Local file search** — Whoosh full-text index of your Documents/Projects folders with live watchdog updates
- **Summary bar** — instant factual answers from Wikipedia and DuckDuckGo Instant Answers
- **Favourites** — bookmark any result with one click
- **Search history** — persisted across restarts, navigate with ↓ arrow
- **Safe search** — math puzzle gate to disable
- **Themes** — Light, Dark, Night (warm amber)
- **Background image** — pick any image from your device, with transparency control
- **Server mode** — expose to your local network for use on phones/tablets/other PCs

---

## Installation

### Windows

1. Download and unzip Ponder
2. Double-click `install.bat`

The installer will:
- Create a Python virtual environment
- Install all dependencies
- Create a silent `Ponder.lnk` shortcut (no CMD window) in your Start Menu and Desktop
- Set up a `http://ponder` hostname alias (optional, requires admin)

To start Ponder after installing, use the Start Menu or Desktop shortcut, or double-click `ponder.bat` for a visible console (useful for debugging).

### Linux

```bash
git clone https://github.com/DansDesigns/Ponder
cd Ponder
python3 install.py
```

Creates a `ponder` CLI launcher in `~/.local/bin` and a `.desktop` entry in the app menu.

---

## Usage

Open `http://localhost:7000` in any browser after starting Ponder.

- **Search** — type and press Enter, or click the search button
- **History** — press `↓` in the search bar to browse past searches
- **Favourites** — click the ★ icon on any result card
- **Settings** — click the ⚙ cog in the top-right corner
- **Keyboard shortcut** — press `/` anywhere to focus the search bar

---

## Settings

All settings are saved to `~/.config/ponder/config.json` and can be changed via the in-app settings panel.

| Setting | Default | Description |
|---|---|---|
| `web_backend` | `ddg` | `ddg`, `brave`, `google`, `serper`, or `searxng` |
| `brave_api_key` | — | Free at [search.brave.com](https://api.search.brave.com) |
| `google_api_key` / `google_cx` | — | Google Custom Search JSON API |
| `serper_api_key` | — | [serper.dev](https://serper.dev) |
| `searxng_url` | `http://localhost:8080` | Your SearXNG instance URL |
| `show_summary` | `true` | Show instant answer bar above results |
| `safe_search` | `false` | Filter explicit content (math puzzle to disable) |
| `dark_mode` | `light` | `light`, `dark`, or `night` |
| `background_image` | `none` | Filename from `static/` folder |
| `bg_opacity` | `15` | Background image opacity (2–80%) |
| `host` | `127.0.0.1` | `0.0.0.0` for network/server mode |
| `port` | `7000` | Port to listen on |
| `open_browser` | `true` | Auto-open browser on start |
| `watch_dirs` | `["~/Documents","~/Projects"]` | Folders to index for local search |
| `max_file_mb` | `10` | Skip files larger than this |

---

## Web Search Pipeline

Results are fetched in parallel from multiple independent sources and deduplicated:

**Tier 1 (parallel):** Mojeek · Stract · DuckDuckGo  
**Tier 2 (sequential fallback):** Yahoo · SearXNG public · Marginalia

Mojeek and Stract have their own indexes independent of Bing/Google, providing genuine diversity of results.

---

## Network / Server Mode

To use Ponder from other devices on your network:

1. Open Settings → **SERVER MODE** → toggle on
2. Click **Restart now**
3. Connect from any device using the URL shown (e.g. `http://192.168.1.50:7000`)

On Android/iOS: open in browser → Add to Home Screen for a full-screen app experience.

To auto-start on boot (Linux/systemd):

```ini
[Unit]
Description=Ponder Search
After=network.target

[Service]
WorkingDirectory=/path/to/Ponder
ExecStart=/path/to/Ponder/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

---

## File Structure

```
Ponder/
  main.py             FastAPI app — all API routes and streaming search
  config.py           Config load/save
  indexer.py          Whoosh local file indexer + watchdog live updates
  web_search.py       Multi-backend web search pipeline
  image_search.py     Parallel image search (Openverse, Wikimedia, DDG)
  video_search.py     DuckDuckGo video search
  wiki.py             Wikipedia API
  map_search.py       Nominatim / OpenStreetMap geocoding
  install.py          Cross-platform installer
  install.bat         Windows installer entry point
  requirements.txt    Python dependencies
  ponder.bat          Windows launcher (visible console)
  ponder_silent.vbs   Windows silent launcher (no CMD window)
  Ponder.lnk          Windows shortcut (created by installer)
  ponder.ico          App icon (multi-size Windows ICO)
  logo.png            App logo (used by shortcuts)
  static/
    index.html        Full UI — all CSS and JS inline
    logo.png          Logo served to browser
    ponder.ico        Favicon served to browser
```

Config, history, favourites and the search index are stored in `~/.config/ponder/`.

---

## Supported File Types (Local Search)

| Type | Indexing |
|---|---|
| Text / code (`.py`, `.js`, `.md`, `.txt`, `.json`, `.yaml`, …) | Full text |
| PDF | Text extracted via pdfminer |
| Word (`.docx`) | Text extracted via python-docx |
| Everything else | Filename only |

---

## Dependencies

- [FastAPI](https://fastapi.tiangolo.com) + [uvicorn](https://www.uvicorn.org)
- [httpx](https://www.python-httpx.org) — async HTTP
- [Whoosh](https://whoosh.readthedocs.io) — full-text search index
- [watchdog](https://python-watchdog.readthedocs.io) — live file watching
- BeautifulSoup4, lxml — HTML parsing
- pdfminer.six, python-docx — document text extraction
- aiofiles, python-multipart — file serving and uploads

---

## Credits

Built by [AlterniTech](http://alternitech.co.uk/)

---

## Licence

MIT
