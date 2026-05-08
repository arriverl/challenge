"""
Algebraic normal form (ANF / Reed–Muller) for each coordinate y[k] of S0.

Variable convention matches Verilog ``x[5:0]``: integer input ``w`` uses bit ``j`` as ``x[j]``
(w = sum_j x[j]*2^j, so x[0] is LSB).

Also optionally writes Espresso-compatible PLA files (one output bit per file).
"""
from __future__ import annotations

import argparse
from pathlib import Path

from truth_table import coord_truth


def mobius_anf_6var(fv: list[int]) -> list[int]:
    """GF(2) Möbius transform: fv[mask] becomes ANF coefficient for monomial Π_{i:mask_i} x_i."""
    if len(fv) != 64:
        raise ValueError("need length-64 truth table")
    a = fv[:]
    for i in range(6):
        bit = 1 << i
        for idx in range(64):
            if idx & bit:
                a[idx] ^= a[idx ^ bit]
    return a


def mask_to_monomial(mask: int) -> str:
    parts = []
    for i in range(6):
        if mask & (1 << i):
            parts.append(f"x{i}")
    return "*".join(parts) if parts else "1"


def anf_string(coeffs: list[int]) -> str:
    terms = [mask for mask in range(64) if coeffs[mask] & 1]
    if not terms:
        return "0"
    return " ^ ".join(mask_to_monomial(m) for m in terms)


def pla_write_one_hot_minterms(path: Path, fv: list[int]) -> None:
    """PLA: one output; rows are input cubes where f=1 (full minterms, no merge)."""
    lines = [
        ".i 6",
        ".o 1",
        ".ilb x5 x4 x3 x2 x1 x0",
        ".ob y",
        "",
    ]
    for w in range(64):
        if fv[w]:
            bits = [(w >> i) & 1 for i in reversed(range(6))]
            pat = "".join(str(b) for b in bits)
            lines.append(f"{pat} 1")
    lines.append(".e")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description="ANF / PLA export for S0 coordinates")
    ap.add_argument("--pla-dir", type=Path, default=None, help="write y0.pla..y5.pla here")
    args = ap.parse_args()

    for k in range(6):
        fv = coord_truth(k)
        coeffs = mobius_anf_6var(fv)
        print(f"# y[{k}] ANF (xor of monomials)")
        print(anf_string(coeffs))
        print()

    if args.pla_dir:
        args.pla_dir.mkdir(parents=True, exist_ok=True)
        for k in range(6):
            pla_write_one_hot_minterms(args.pla_dir / f"y{k}.pla", coord_truth(k))
        print(f"Wrote PLA files under {args.pla_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
