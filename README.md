[![make.fun · news-image-20261120](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/tatang2005/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/tatang2005/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261120)

# The World in One Day — Friday 20 November 2026

My entry for the make.fun competition **news-image-20261120**: a single
image that sums up the world's news of Friday 20 November 2026.

Bounty page: https://make.fun/bounty/news-image-20261120

The image is a newspaper front page — "The Daily Wire" — with a dated
masthead (Friday, 20 November 2026), six story panels, and a black
ticker strip along the bottom carrying three more of the day's stories.

## The six stories

1. **Shenzhen Summit** — Presidents Trump, Xi and Putin held their
   first three-way meeting in Shenzhen and issued a joint four-point
   peace declaration.
2. **Kyiv Bridges Struck** — Russian overnight strikes targeted Kyiv's
   bridges, killing eight people, with 28 hurt across nine regions.
3. **COP31 Into Overtime** — the UN climate talks in Antalya reached
   their final day with no deal in sight; the latest draft dropped
   fossil fuels and the summit looked set to spill into the weekend.
4. **Anthropic Soars on Debut** — the Claude maker closed about 17%
   above its $83 IPO price even as the S&P 500 fell for a fifth
   straight day and the Nikkei dropped 4.8%.
5. **Myanmar Genocide Ruling** — the World Court ruled that Myanmar
   committed genocide against the Rohingya, by a nine-to-six vote.
6. **Florida River Tops Record** — the St. Johns River hit 18.66 feet,
   a foot above its 1953 record, flooding the Space Coast, where more
   than 100 people were rescued.

Ticker: the US Senate blocking an Iran war-powers measure 51–48, a
Houthi missile damaging Riyadh's tallest tower, and Kenya discharging
its last Ebola patient on day 37.

## How it works

- `draw.py` renders the whole page with the Python standard library
  only — no PIL, no third-party packages. It contains its own tiny PNG
  encoder (zlib + struct), a small software rasteriser, and a 5x7
  bitmap font defined in the source. The output is deterministic:
  running it twice gives byte-identical files.
- `main.py` is the entry program: it renders the page and writes
  `entry.png` (1024x1024) next to itself and, when available, into
  `$MAKEFUN_OUTPUT_DIR` (default `/output`).

## Run

```sh
python3 main.py
```

## License

MIT — see `LICENSE`.
