// STR skeleton — contest SB(input [5:0] x, output [5:0] y).
// Replace LUT SB by structural NanGate cells (match liberty pin names in YOUR library).
//
// Typical NanGate pin naming (verify against lib/*.lib): BUF INV NAND NOR AOI OAI MUX...
// Example patterns (syntax illustrative only):
//
//   wire x0_b, x0_n;
//   BUF_X1   ib0 (.A(x[0]), .Z(x0_b));
//   INV_X1   in0 (.A(x[0]), .ZN(x0_n));
//   NAND2_X1 g01 (... .ZN(net01));
//
// Drive each y[k] from a net fed only by allowed cells; duplicate shared nodes explicitly
// if your mapper does not retain sharing across outputs.
//
// Workflow:
//   1) python scripts/coords_anf.py           → algebraic starting point
//   2) factor into NAND/OAI-heavy forms       → lower XOR/OR chains
//   3) python scripts/d_theory_skeleton.py    → weights sanity (full DAG TBD)
//   4) yosys_map_nangate_run + sta_sb_run    → D_STA iteration
//
// Until STR is finished, keep using module SB in rtl/sb_lut_baseline.v as golden.

module SB_STR_SKEL (
    input  wire [5:0] x,
    output wire [5:0] y
);
    SB u_golden (
        .x(x),
        .y(y)
    );
endmodule
