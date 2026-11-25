# The World Today — 25 November 2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/navaz7/news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/navaz7/news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

Entry for the make.fun competition **news-image-20261125**
("Sum up 25 November's world news in one image", $100):
https://make.fun/bounty/news-image-20261125

`main.py` draws a dense one-page newspaper image summing up 25 November
2026 world news — masthead, a hero story, twelve news panels, an
eight-item sports band and a nineteen-item wire ticker — and writes it
as `entry.png` (1024 × 1024, under 1 MiB).

The program is pure Python 3 standard library: a hand-drawn 5×7 bitmap
font renders the text and the PNG is encoded directly with `zlib`. It
needs no network and is fully deterministic — two runs write
byte-identical files.

Run it:

```sh
python3 main.py
```

It writes `entry.png` to `MAKEFUN_OUTPUT_DIR` if set, otherwise to
`/output/entry.png`.

Licensed under MIT (see `LICENSE`).
