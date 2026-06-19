This file provides guidance to AI agents when working with code in this repository.

## Session Memory Protocol

At the START of every session:
1. Read `runbook/README.md`
2. Read the most recent file in `runbook/session-logs/`
3. Read `runbook/references/open-decisions.md`

At the END of every session (when user says "save session" or before closing):
1. Write a new session log to `runbook/session-logs/YYYY-MM-DD-N.md` covering what was done, issues found, decisions made, and current state
2. Update `runbook/references/open-decisions.md` if anything was resolved or new decisions came up
3. Push to the repo:
```bash
cd /tmp/so101-clean && git add runbook/ && git commit -m "Session log YYYY-MM-DD" && git push origin main
```

> **User-facing help → [`AGENT_GUIDE.md`](./AGENT_GUIDE.md)** (SO-101 setup, recording, picking a policy, training duration, eval — with copy-pasteable commands).

## Project Overview

LeRobot is a PyTorch-based library for real-world robotics, providing datasets, pretrained policies, and tools for training, evaluation, data collection, and robot control. It integrates with Hugging Face Hub for model/dataset sharing.

## Tech Stack

Python 3.12+ · PyTorch · Hugging Face (datasets, Hub, accelerate) · draccus (config/CLI) · Gymnasium (envs) · uv (package management)

## Development Setup

```bash
uv sync --locked                            # Base dependencies
uv sync --locked --extra test --extra dev   # Test + dev tools
uv sync --locked --extra all                # Everything
git lfs install && git lfs pull             # Test artifacts
```

## Key Commands

```bash
uv run pytest tests -svv --maxfail=10                 # All tests
DEVICE=cuda make test-end-to-end                      # All E2E tests
pre-commit run --all-files                           # Lint + format (ruff, typos, bandit, etc.)
```

## Architecture (`src/lerobot/`)

- **`scripts/`** — CLI entry points (`lerobot-train`, `lerobot-eval`, `lerobot-record`, etc.), mapped in `pyproject.toml [project.scripts]`.
- **`configs/`** — Dataclass configs parsed by draccus. `train.py` has `TrainPipelineConfig` (top-level). `policies.py` has `PreTrainedConfig` base. Polymorphism via `draccus.ChoiceRegistry` with `@register_subclass("name")` decorators.
- **`policies/`** — Each policy in its own subdir. All inherit `PreTrainedPolicy` (`nn.Module` + `HubMixin`) from `pretrained.py`. Factory with lazy imports in `factory.py`.
- **`processor/`** — Data transformation pipeline. `ProcessorStep` base with registry. `DataProcessorPipeline` / `PolicyProcessorPipeline` chain steps.
- **`datasets/`** — `LeRobotDataset` (episode-aware sampling + video decoding) and `LeRobotDatasetMetadata`.
- **`envs/`** — `EnvConfig` base in `configs.py`, factory in `factory.py`. Each env subclass defines `gym_kwargs` and `create_envs()`.
- **`robots/`, `motors/`, `cameras/`, `teleoperators/`** — Hardware abstraction layers.
- **`types.py`** and **`configs/types.py`** — Core type aliases and feature type definitions.

## Repository Structure (outside `src/`)

- **`tests/`** — Pytest suite organized by module. Fixtures in `tests/fixtures/`, mocks in `tests/mocks/`. Hardware tests use skip decorators from `tests/utils.py`. E2E tests via `Makefile` write to `tests/outputs/`.
- **`.github/workflows/`** — CI: `quality.yml` (pre-commit), `fast_tests.yml` (base deps, every PR), `full_tests.yml` (all extras + E2E + GPU, post-approval), `latest_deps_tests.yml` (daily lockfile upgrade), `security.yml` (TruffleHog), `release.yml` (PyPI publish on tags).
- **`docs/source/`** — HF documentation (`.mdx` files). Per-policy READMEs, hardware guides, tutorials. Built separately via `docs-requirements.txt` and CI workflows.
- **`examples/`** — End-user tutorials and scripts organized by use case (dataset creation, training, hardware setup).
- **`docker/`** — Dockerfiles for user (`Dockerfile.user`) and CI (`Dockerfile.internal`).
- **`benchmarks/`** — Performance benchmarking scripts.
- **Root files**: `pyproject.toml` (single source of truth for deps, build, tool config), `Makefile` (E2E test targets), `uv.lock`, `CONTRIBUTING.md` & `README.md` (general information).

## Notes

- **Mypy is gradual**: strict only for `lerobot.envs`, `lerobot.configs`, `lerobot.optim`, `lerobot.model`, `lerobot.cameras`, `lerobot.motors`, `lerobot.transport`. Add type annotations when modifying these modules.
- **Optional dependencies**: many policies, envs, and robots are behind extras (e.g., `lerobot[aloha]`). New imports for optional packages must be guarded or lazy. See `pyproject.toml [project.optional-dependencies]`.
- **Video decoding**: datasets can store observations as video files. `LeRobotDataset` handles frame extraction, but tests need ffmpeg installed.
- **Prioritize use of `uv run`** to execute Python commands (not raw `python` or `pip`).

---

## SO-101 Setup (Ishan's Robot)

### Hardware
- **Follower arm:** SO-101, port `/dev/tty.usbmodem5B610354731`
- **Leader arm:** SO-101, port `/dev/tty.usbmodem5B3D0458801`
- Both arms use Feetech STS3215 motors (model 777), 6 motors each (IDs 1–6)
- Motor ID to joint mapping: 1=shoulder_pan, 2=shoulder_lift, 3=elbow_flex, 4=wrist_flex, 5=wrist_roll, 6=gripper

### Environment
- Conda env: `lerobot` (`conda activate lerobot && cd ~/lerobot`)
- lerobot scripts run under system Python 3.13 (`/Library/Frameworks/Python.framework/Versions/3.13/`)
- `scservo_sdk` is only available under `python3.13`, not the conda env Python

### Key Commands
```bash
bash teleop.sh                          # Run teleoperation
python3.13 check_motors.py             # Ping all 6 follower motors (diagnostic)

# Calibration
lerobot-calibrate --robot.type=so101_follower --robot.port=/dev/tty.usbmodem5B610354731 --robot.id=main
lerobot-calibrate --teleop.type=so101_leader --teleop.port=/dev/tty.usbmodem5B3D0458801 --teleop.id=main
```

### teleop.sh
Uses `max_relative_target=5` to cap per-frame motion to 5° and prevent sudden jumps:
```bash
lerobot-teleoperate --robot.type=so101_follower --robot.port=/dev/tty.usbmodem5B610354731 --robot.id=main --teleop.type=so101_leader --teleop.port=/dev/tty.usbmodem5B3D0458801 --teleop.id=main --robot.max_relative_target=5
```

### Calibration Files
- Follower: `~/.cache/huggingface/lerobot/calibration/robots/so_follower/main.json`
- Leader: `~/.cache/huggingface/lerobot/calibration/teleoperators/so_leader/main.json`
- `calibration_dir: None` in config is fine — lerobot loads from the cache path automatically

### Known Issues & Fixes

**sync_read failures** (`no status packet` / `incorrect status packet`)
- Symptom: Teleop crashes on `ConnectionError: Failed to sync read 'Present_Position'`
- Fix applied: `num_retry=10` added to `sync_read` calls in:
  - `src/lerobot/robots/so_follower/so_follower.py` (lines 181, 215)
  - `src/lerobot/teleoperators/so_leader/so_leader.py` (line 148)
- Cause: USB bus contention at 60Hz; individual pings work but broadcast sync_read fails intermittently

**Motor overload** (motor 5 / wrist_roll on follower)
- Symptom: `[RxPacketError] Overload error!` → full bus failure
- Fix: Full power cycle (unplug barrel jack, not just USB), move arm to relaxed position, restart
- Prevention: Always leave arm in neutral resting position before powering off

**wrist_flex (motor 4) snapping to 2 extreme positions**
- Cause: Calibrated range is 0–4095 (physical limits not detected during calibration)
- Fix: Redo calibration — stop each joint just before it starts resisting, do not push into hard stops

**wrist_flex leader encoder randomly resets to 0 mid-range**
- Cause: Likely loose JST encoder cable inside motor 4 on the leader arm
- May require motor replacement

**Follower continuously drifting without leader movement**
- Cause: Arms not calibrated to the same coordinate system
- Fix: Run calibration on both arms

### GitHub Remote
- Repo: `https://github.com/IshanAhluwalia/SO-101-Policy-Training-.git`
- Remote name: `myrepo`
- Auth not yet configured (needs GitHub PAT or SSH key)
