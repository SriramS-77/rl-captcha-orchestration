"""Where everything lives.

`expkit` imports the core package `rlcaptcha` (at the repository root) and extends it.
Every artefact it writes goes under `experiments/results/`.
"""

from __future__ import annotations

import sys
from pathlib import Path

EXP_ROOT = Path(__file__).resolve().parent.parent      # experiments/
REPO_ROOT = EXP_ROOT.parent                             # repository root
PROJECT_ROOT = REPO_ROOT

# Make `import rlcaptcha` work from any script under experiments/.
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DATA = REPO_ROOT / "data"
CAMPAIGN_A = DATA / "recordings" / "campaign_a"         # Aug 2025, 83 sessions
CAMPAIGN_B = DATA / "recordings" / "campaign_b"         # Nov 2025, 73 sessions
EXTERNAL = DATA / "external"                            # third-party datasets (not shipped)

RESULTS = EXP_ROOT / "results"
MODELS = EXP_ROOT / "models"
PARTITION_JSON = RESULTS / "partition.json"
SCORERS = RESULTS / "scorers"
AGENTS = RESULTS / "agents"

RESULTS.mkdir(parents=True, exist_ok=True)
