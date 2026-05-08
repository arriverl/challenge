"""
Estimate weighted critical delay on a *flattened* NanGate-style verilog netlist.

Uses max-plus arrival at each gate output: arr[out] = delay(cell) + max(arr[in]).
Weights from data/gate_delays_ps.json (contest Table 2 names); maps OAI211_X1 -> OAI21 etc.

This approximates contest D_theory structure when your mapped cells align with Table-2 classes.
Does not model distinct BUF/INV branches per PI fanout rule in full detail — refine if needed.

Usage:
  python d_theory_mapped.py [path/to/sb_mapped_nangate.v]
Default: ../build/sb_mapped_nangate.v relative to project root.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATES_JSON = ROOT / "data" / "gate_delays_ps.json"

ALIASES = {
    "OAI211": "OAI21",
    "AOI211": "AOI21",
    "OAI221": "OAI22",
    "AOI221": "AOI22",
}


def load_delays_ps() -> dict[str, float]:
    obj = json.loads(GATES_JSON.read_text(encoding="utf-8"))
    return {k.upper(): float(v["delay_ps"]) for k, v in obj["gates"].items()}


def strip_strength(name: str) -> str:
    return re.sub(r"_X\d+$", "", name)


def delay_for_cell(cell: str, delays: dict[str, float]) -> float:
    raw = strip_strength(cell).upper()
    if raw in delays:
        return delays[raw]
    if raw in ALIASES:
        return delays[ALIASES[raw]]
    for key in sorted(delays.keys(), key=len, reverse=True):
        if raw.startswith(key):
            return delays[key]
    raise KeyError(f"no contest delay for cell {cell} -> {raw}")


def strip_comments(src: str) -> str:
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.DOTALL)
    src = re.sub(r"//[^\n]*", "", src)
    return src


OUTPUT_PORTS = frozenset({"Z", "ZN", "S", "CO", "QN"})


def parse_instances(src: str) -> list[tuple[str, dict[str, str]]]:
    """Return list of (cell_type, {port: net})."""
    src = strip_comments(src)
    out: list[tuple[str, dict[str, str]]] = []
    # Robust split by statements to tolerate escaped identifiers and multiline pins.
    for stmt in src.split(";"):
        s = stmt.strip()
        if not s or "(" not in s or "." not in s:
            continue
        # Skip declarations/assign/module headers.
        if re.match(r"^(module|endmodule|input|output|wire|assign|always|if|for)\b", s):
            continue
        m = re.match(r"^([A-Za-z_\\$][A-Za-z0-9_\\$]*)\s+(.+?)\s*\((.*)\)\s*$", s, re.DOTALL)
        if not m:
            continue
        ctype, _inst, blob = m.groups()
        ports: dict[str, str] = {}
        for pm in re.finditer(r"\.([A-Za-z0-9_]+)\s*\(\s*([^)]+?)\s*\)", blob):
            pin, net = pm.groups()
            ports[pin.strip()] = net.strip()
        if ports:
            out.append((ctype, ports))
    return out


def pick_output_net(ports: dict[str, str]) -> tuple[str, str] | None:
    for pref in ("ZN", "Z"):
        if pref in ports:
            return pref, ports[pref]
    for p, n in ports.items():
        if p in OUTPUT_PORTS:
            return p, n
    return None


def main() -> int:
    default_v = ROOT / "build" / "sb_mapped_nangate.v"
    vpath = Path(sys.argv[1]) if len(sys.argv) > 1 else default_v
    if not vpath.exists():
        print(f"missing {vpath}", file=sys.stderr)
        return 1
    delays = load_delays_ps()
    text = vpath.read_text(encoding="utf-8", errors="replace")
    mod_m = re.search(r"\bmodule\s+(\w+)", text)
    top = mod_m.group(1) if mod_m else "?"
    insts = parse_instances(text)

    arrivals: dict[str, float] = {}
    const_nets = {"1'b0", "1'b1", "1'hx", "1'bz"}

    # Primary inputs: \\x [ bit ] style from Yosys sometimes — normalize common patterns
    pi_re = re.compile(r"^\\?x(\[\d+\])$|^x(\[\d+\])$")

    def ensure_pi(net: str) -> None:
        net_clean = net.replace(" ", "")
        if pi_re.match(net_clean) or re.match(r"^\\?x_\d+$", net_clean):
            if net_clean not in arrivals:
                arrivals[net_clean] = 0.0
        if net_clean in const_nets:
            arrivals.setdefault(net_clean, 0.0)

    remaining = list(insts)
    safety = len(remaining) + 5
    while remaining and safety:
        safety -= 1
        progressed = False
        next_round: list[tuple[str, dict[str, str]]] = []
        for ctype, ports in remaining:
            out_pick = pick_output_net(ports)
            if not out_pick:
                continue
            _op, out_net = out_pick
            in_nets = [ports[p] for p in ports if p != out_pick[0]]
            bad = False
            mx = 0.0
            for n in in_nets:
                ensure_pi(n)
                nc = n.replace(" ", "")
                if nc not in arrivals and nc not in const_nets:
                    bad = True
                    break
                mx = max(mx, arrivals.get(nc, 0.0))
            if bad:
                next_round.append((ctype, ports))
                continue
            d = delay_for_cell(ctype, delays)
            arrivals[out_net.replace(" ", "")] = d + mx
            progressed = True
        remaining = next_round
        if not progressed:
            break

    def arrival_for_net(net: str) -> float:
        net = net.strip()
        if net in arrivals:
            return arrivals[net]
        if net.startswith("\\"):
            return arrivals.get(net[1:], float("nan"))
        return arrivals.get("\\" + net, float("nan"))

    ys_est: list[float] = []
    for k in range(6):
        m = re.search(rf"assign\s+y\s*\[\s*{k}\s*\]\s*=\s*([^;]+);", text)
        val = float("nan")
        if m:
            rhs = m.group(1).strip().split()[0]
            val = arrival_for_net(rhs)
        if val != val:
            key = f"y[{k}]"
            val = arrivals.get(key, float("nan"))
        if val != val:
            alt = [arrivals[a] for a in arrivals if re.search(rf"y\s*\[\s*{k}\s*\]", a)]
            val = max(alt) if alt else float("nan")
        ys_est.append(val)

    finite = [z for z in ys_est if z == z]
    worst = max(finite) if finite else float("nan")

    print(f"file: {vpath}")
    print(f"top module (guess): {top}")
    print(f"instances parsed: {len(insts)}")
    print(f"arrival nets resolved: {len(arrivals)}")
    if finite:
        print(f"per-output estimate (ps): " + ", ".join(f"{z:.2f}" if z == z else "nan" for z in ys_est))
        print(f"max over outputs (estimate): {worst:.3f} ps")
    else:
        print("could not resolve output arrivals — parser may need net-name tweaks for your yosys output")
        return 2
    if remaining:
        print(f"warning: {len(remaining)} instances left unordered (cycles or unknown pins)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
