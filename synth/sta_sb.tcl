# Manual STA example — prefers OS env NANGATE_LIB (OpenSTA Tcl).
# Automated runs use `build/sta_sb_run.tcl` with embedded paths.
if {![info exists ::env(NANGATE_LIB)] || $::env(NANGATE_LIB) eq ""} {
    puts stderr "Set env NANGATE_LIB to NangateOpenCellLibrary_typical.lib or use build/sta_sb_run.tcl"
    exit 1
}
set lib_path $::env(NANGATE_LIB)
read_liberty $lib_path
read_verilog build/sb_mapped_nangate.v
link_design SB

# Pure combinational design, no clocks required for max input->output delay report.
set_input_delay 0 [all_inputs]
set_output_delay 0 [all_outputs]

report_checks -path_delay max -digits 4
report_tns
report_wns
