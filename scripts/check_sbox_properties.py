"""Sanity: bijection (permutation) and differential uniformity for S0."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from truth_table import s0, table_64  # noqa: E402


def is_permutation(vals: list[int]) -> bool:
    return len(vals) == 64 and len(set(vals)) == 64


def differential_uniformity(vals: list[int]) -> tuple[int, tuple[int, int, int] | None]:
    """
    DU = max_{a!=0,b} #{x : S(x) ^ S(x^a) = b}.
    APN S-box on F2^n (n even): DU = 2 for non-bent APN vectorial; contest states APN.
    """
    n = 6
    best = 0
    worst: tuple[int, int, int] | None = None
    for a in range(1, 1 << n):
        for b in range(1 << n):
            cnt = 0
            for x in range(1 << n):
                if (vals[x] ^ vals[x ^ a]) == b:
                    cnt += 1
            if cnt > best:
                best = cnt
                worst = (a, b, cnt)
    return best, worst


def main() -> int:
    t = table_64()
    if not is_permutation(t):
        print("FAIL: not a permutation")
        return 1
    du, worst = differential_uniformity(t)
    print(f"OK: permutation on 0..63")
    print(f"Differential uniformity max count = {du}", end="")
    if worst:
        print(f" (example a={worst[0]:#04x} b={worst[1]:#04x} count={worst[2]})")
    else:
        print()
    if du != 2:
        print("NOTE: expected DU=2 for this APN S-box; double-check table if not 2.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
