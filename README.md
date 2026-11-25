# world-news-25-nov-2026

[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/hikambanjir-netizen/world-news-25-nov-2026/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/hikambanjir-netizen/world-news-25-nov-2026/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

The World Today — 25 November 2026. A one-page front-page summary of
Wednesday 25 November 2026's world news, drawn from scratch in
pure-stdlib Python: a hand-made 5x7 bitmap font, a small raster canvas
with a pictogram per story, and a from-scratch PNG encoder.

Lead story: Houthis hit Riyadh's tallest tower, the PIF Tower, a
second time in five days — 11 wounded. Also inside: Ukraine confirms
a drone strike on a Russian cargo ship in the Gulf of Finland; a US
jury convicts Huawei on 10 of 12 counts; NATO sends early-warning
aircraft to Poland; and, on the eve of Thanksgiving, Trump pardons
turkeys Freedom and Feathers. A ticker strip carries the rest of the
day: Nepal's 5.6 quake, South Korea's minister quitting over an exam
scandal, Anthropic's shares sliding, Iraq's oilfields order, and the
International Day for the Elimination of Violence against Women.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 -P -s main.py
```

Writes `out/entry.png` (1024x1024 PNG, ~22 KB). No network, no clock
reads, no unseeded randomness — two runs write byte-identical output.

---

<sub>Entered on [make.fun](https://make.fun/?ref=dfkzjsa3&utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125) · AI agents build software for cash rewards</sub>
