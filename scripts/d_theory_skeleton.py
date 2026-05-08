"""
Skeleton for contest theoretical delay D_theory (Table-2 gate weights, weighted longest path).

Full STR evaluation requires parsing your hierarchical gate netlist into a DAG; this module
loads weights and documents the recurrence you must implement once wires are known.

Contest reminder (PDF): primary inputs pass through BUF or INV before feeding other gates when
modeling their reference STR example.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "gate_delays_ps.json"


def load_gate_delays_ps() -> dict[str, float]:
    obj = json.loads(DATA.read_text(encoding="utf-8"))
    out: dict[str, float] = {}
    for name, spec in obj["gates"].items():
        out[name.upper()] = float(spec["delay_ps"])
    return out


def longest_path_chain(delays: dict[str, float], gates: list[str]) -> float:
    """Toy helper: sum delays along a named gate chain (no fanout / PI buffering)."""
    return sum(delays[g.upper()] for g in gates)


def main() -> int:
    if not DATA.exists():
        print(f"missing {DATA}", file=sys.stderr)
        return 1
    d = load_gate_delays_ps()
    print("Loaded gate delays (ps):", len(d), "types")
    # Example from contest PDF-style NAND STR depth-3 from buffered PI:
    # BUF -> NAND2 -> NAND2  vs INV -> NAND2 -> NAND2
    ex_buf = longest_path_chain(d, ["BUF", "NAND2", "NAND2"])
    ex_inv = longest_path_chain(d, ["INV", "NAND2", "NAND2"])
    print(f"example chain BUF+NAND2+NAND2 = {ex_buf:.3f} ps")
    print(f"example chain INV+NAND2+NAND2 = {ex_inv:.3f} ps")
    print()
    print("Next step: build DAG from STR Verilog (instances + nets),")
    print("add PI BUF/INV sources per contest rule, run longest-path DP per output bit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
