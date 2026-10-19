# External datasets

Two public datasets are used. They are not redistributed here; download them yourself under
their own terms:

| Dataset | Used for | Source |
|---|---|---|
| Web bot detection dataset, Iliou et al., *Digital Threats* 2021 ([doi:10.1145/3447815](https://doi.org/10.1145/3447815)) | Phase 1 D1/D2: Table 3. Phase 2 advanced bots: covert bots in the drift study | the dataset's release page (Bournemouth University data repository) |
| Balabit Mouse Dynamics Challenge (Fülöp et al., 2016) | bot-like humans in the drift study | <https://github.com/balabit/Mouse-Dynamics-Challenge> |

## Layout

Put both under `data/external/raw/`, keeping their own folder structure:

```text
data/external/raw/
├── balabit_dataset/
│   └── test_files/user7/session_..., user9/..., ...          (10 users)
└── web_bot_detection_dataset/
    ├── phase1/
    │   ├── annotations/humans_and_moderate_bots/{train,test}
    │   ├── annotations/humans_and_advanced_bots/{train,test}
    │   └── data/mouse_movements/humans_and_{moderate,advanced}_bots/<session>/mouse_movements.json
    └── phase2/
        └── data/mouse_movements/
            ├── humans/mouse_movements_humans.json
            └── bots/mouse_movements_{advanced,moderate}_bots.json
```

A different location can be given with `EXTERNAL_RAW=<dir>`.

## Build the drift-study cache

From `experiments/`:

```bash
python -m expkit.external --build --check
```

This applies the fixed cleaning rules of the paper (§III-B, *Preparation of External Data*) and
writes `data/external/external_sessions.json.gz`: 300 Balabit sessions from 10 users and 120
Phase-2 advanced-bot sessions, each split into a training (INJECT) and an evaluation (HELD-OUT)
half. `--check` compares the file with the SHA-256 pinned in `expkit/external.py`; it must print
`OK`. The build is byte-for-byte deterministic, as long as the output keeps the file name
`external_sessions.json.gz`, because gzip stores the name in its header.

Table 3 (`paper/webbot_finetune.py`) reads Phase 1 directly from `raw/` and needs no cache.
