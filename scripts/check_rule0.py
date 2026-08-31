#!/usr/bin/env python3
"""Run numeric/API Rule 0 checks plus structural prose and Experiment 001 amendment checks."""

from __future__ import annotations

from check_rule0_core import main as core_main
from exp001_pilot_contract import PilotContractError, validate_exp001_pilot_contract
from rule0_surface_contract import SurfaceContractError, validate_surface_contract


def main() -> None:
    try:
        validate_surface_contract()
        validate_exp001_pilot_contract()
    except (SurfaceContractError, PilotContractError) as exc:
        raise SystemExit(f"Rule 0 contract failed: {exc}") from exc
    core_main()


if __name__ == "__main__":
    main()
