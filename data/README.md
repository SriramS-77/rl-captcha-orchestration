# Data

## `recordings/`: our mouse recordings (included)

156 sessions recorded on a playground blog website (navigation, reading, form filling). Each
session is about 120 s of `mousemove` events, logged with a minimum gap of 10 ms.

| Folder | Campaign | Sessions | Humans | Bots |
|---|---|---|---|---|
| `campaign_a/` | Aug 2025 | 83 | 12 | 71 |
| `campaign_b/` | Nov 2025 | 73 | 32 | 41 |

The human recordings come from 3 participants. The bots are the four tiers of the paper (§III-B):
`NaiveBot`, `HumanishBot` (straight lines at constant speed), `MimicBot` (Bézier curves) and
`FallibleBot` (adds errors, hesitations and corrections). The file name gives the class and, for
bots, the tier: `human_data_<time>.json` or `bot_<Tier>_data_<time>.json`.

Each file holds only what the experiments read:

```json
{
  "bot_info": null,
  "timestamps": {"start": 1755279032645, "end": ...},
  "mouse_movements": [{"x": 230, "y": 496, "timestamp": 1755279033328}, ...]
}
```

`timestamps.start` anchors the 10 s chunks (`end` is not used). `bot_info` is `null` for humans and `{"bot_id", "bot_name", "session_timestamp"}` for bots. Click,
scroll and keystroke logs were removed before release. Only anonymous cursor trajectories are
published.

The split into scorer, RL and evaluation blocks is `experiments/results/rotation.json`; the
experiments use fold 2. Recordings are matched by file name, so the `path` fields there are
informational only.

## `external/`: third-party datasets (not included)

The web bot detection dataset of Iliou et al. (2021) and the Balabit Mouse Dynamics Challenge
are used for the benchmark (Table 3) and the drift study (Fig. 4, Tables 5 and 6). They are not
redistributed here. [`external/README.md`](external/README.md) explains how to download them and
build the cache the experiments read.
