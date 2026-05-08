# GNU Make — Windows 可用 Git Bash / MSYS2 / WSL
PYTHON ?= python
IVERILOG ?= iverilog
YOSYS ?= yosys

ROOT := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))
SCRIPTS := $(ROOT)scripts
RTL := $(ROOT)rtl
SIM := $(ROOT)sim
SYNTH := $(ROOT)synth
BUILD := $(ROOT)build

.PHONY: all verify gen props sim synth dirs

all: verify

dirs:
	@"$(PYTHON)" -c "import os; os.makedirs(r'$(BUILD)', exist_ok=True)"

verify:
	"$(PYTHON)" "$(SCRIPTS)/verify_sb.py"

gen:
	"$(PYTHON)" "$(SCRIPTS)/gen_lut_verilog.py"

props:
	"$(PYTHON)" "$(SCRIPTS)/check_sbox_properties.py"

sim: dirs
	cd "$(ROOT)" && "$(IVERILOG)" -g2012 -o "$(BUILD)/tb_sb.vvp" \
		"$(RTL)/sb_lut_baseline.v" "$(SIM)/tb_sb.v" && vvp "$(BUILD)/tb_sb.vvp"

synth: dirs
	cd "$(ROOT)" && "$(YOSYS)" -s synth/yosys_sb.ys
