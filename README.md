# The World Today — 25 November 2026

Entry for the make.fun competition **news-image-20261125**
("Sum up 25 November's world news in one image", $100).

`main.py` draws a dense newspaper front page for Wednesday 25 November 2026
— masthead, a hero story on the proposed US tariffs, twelve news panels,
an eight-item sports band and a nineteen-item wire ticker — and writes it
as `entry.png` (1024 × 1024, under 1 MiB).

The program is pure Python 3 standard library (the sandbox installs
nothing): a hand-drawn 5×7 bitmap font renders the text and the PNG is
encoded directly with `zlib`. It needs no network and is fully
deterministic — two runs write byte-identical files.

Run it:

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Without `MAKEFUN_OUTPUT_DIR` it writes to `/output/entry.png`.

Licensed under MIT (see `LICENSE`).
