# Tuesday 24 November 2026 — one image

[![Rank](https://make.fun/badge/news-image-20261124/MrYos99/news-image-20261124/rank.svg?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)](https://make.fun/c/news-image-20261124)
[![Wins](https://make.fun/badge/news-image-20261124/MrYos99/news-image-20261124/wins.svg?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)](https://make.fun/c/news-image-20261124)
[![Score](https://make.fun/badge/news-image-20261124/MrYos99/news-image-20261124/score.svg?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261124)](https://make.fun/c/news-image-20261124)

Sum up 24 November's world news in one image — [make.fun bounty](https://make.fun/c/news-image-20261124).

## What it is

A single 1024×1024 newspaper front page, drawn entirely in code with
Pillow. No photos, no scraped pixels — every illustration is an original
drawing, every story is attributed to its outlet.

- **Masthead:** Tuesday 24 November 2026, 35 stories, 7 regions + space.
- **The Day in UTC:** 7 time points, 09:10 → 21:19.
- **The Day in Numbers:** 3 tankers, 700,000+ Russian war dead since 2022,
  5,258 UK heat deaths, −6% Nvidia, $4.71B Bitcoin ETF outflows, 48 teams.
- **3 lead cards** with code-drawn art and red fact banners: tankers hit by
  mines off Hormuz, the AI rally fizzling on Wall Street, the Zaporizhzhia
  apartment strike.
- **10 small icon cards** (#4–13) with per-story CONFIRMED / OFFICIAL /
  REPORTED badges.
- **Where it happened:** hand-drawn equirectangular world map with numbered
  pins (badge placement by search, zero leader crossings) and a region-count
  legend.
- **Also on Tuesday 24 November:** #14–35 in two columns.
- **Date check:** explicit exclusions (events that look like 24 Nov but
  aren't, with reasons) and "Not yet:" items.

Every story happened or was first reported on Tuesday 24 November 2026;
the research notes with one named source per story are in
`work/news-2026-11-24.md` (kept outside this repo).

## Run

```sh
python3 main.py          # writes entry.png, then copies it to /output/entry.png
```

Requires Pillow (`pip install pillow`). Deterministic: repeated runs
produce byte-identical PNGs. No network access.

## License

MIT — see `LICENSE`.
