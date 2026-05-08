# 2026 密码数学挑战赛 · 赛题二（6 比特 APN S 盒）

## 目录

- `rtl/sb_lut_baseline.v` — 与表 1 一致的 `SB` 可综合 LUT 基线（功能与评测接口）。
- `rtl/sb_str_stub.v` — STR 占位顶层，当前回连到 LUT；后续改为仅表 2 门实例化。
- `scripts/truth_table.py` — 黄金真值表 `s0(x)`。
- `scripts/verify_sb.py` — 真值表自检。

## 快速检查

```bash
cd sbox_challenge2026/scripts
python verify_sb.py
```

综合/STA 请按赛题附件在 Yosys + NanGate 45 nm 流程中纳入 `rtl/sb_lut_baseline.v` 的 `SB` 模块。

## 一键实验

```bash
cd sbox_challenge2026
python scripts/run_all_experiments.py
```

输出文件：`results/experiment_summary.csv`  
说明：
- Python 功能实验会始终执行；
- 若本机尚未安装 `yosys/opensta/iverilog` 或缺 `NangateOpenCellLibrary_typical.lib`，对应步骤会在结果中标记为 `skip`。
- 在部分 oss-cad-suite Windows 发行版中，OpenSTA 可执行名是 `sta`（不是 `opensta`）。请先运行 `oss-cad-suite\\start.bat` 再开终端，使 `bin` 加入 PATH；`run_all_experiments.py` 也会在 `yosys.exe` 同目录下查找 `sta.exe`。
- **若套件内确实没有 STA**：需另行安装 OpenSTA 并将其加入 PATH，或仅使用 Yosys `stat`/映射结果作为近似（与官方 STA 流程可能不一致）。
- **Yosys 脚本**：`synth/*.ys` 内路径均以**项目根目录**为当前工作目录（运行 `yosys -s synth/yosys_sb.ys` 时 cwd 应为 `sbox_challenge2026/`）。
- **NanGate 映射**：不要在 `.ys` 里写 `$::env(...)`（不会被 Tcl 展开）。一键脚本会生成 `build/yosys_map_nangate_run.ys` 与 `build/sta_sb_run.tcl`。
- **Liberty 报错 `Missing function on output ... CLKGATETST_X1`**：常见原因是时钟门控单元缺少 `function` 字段；生成脚本已使用 `read_liberty -ignore_miss_func`（组合电路映射不需要这些单元）。
- **实验 CSV 过长**：默认会截断 `note` 列；需要完整 Yosys 日志可设置环境变量 `EXPERIMENT_FULL_LOG=1`。
