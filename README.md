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
- **OpenSTA 卡住**：脚本末尾已带 `exit 0`，且自动使用 `sta -exit ...`。若仍超时可调 `EXPERIMENT_STA_TIMEOUT_SEC`（秒，`0` 表示不设超时）。
- **OpenSTA 输出 `No paths found`**：纯组合模块须挂虚拟时钟并写 `-clock` 的 `set_input_delay`/`set_output_delay`；生成脚本已包含 `create_clock __sb_virtual ...`。

## 优化用脚本

| 脚本 | 作用 |
|------|------|
| `scripts/coords_anf.py` | 六位坐标布尔函数的 **ANF**（模 2 多项式）；可选 `--pla-dir <dir>` 导出 Espresso PLA |
| `scripts/d_theory_skeleton.py` | 读取 `data/gate_delays_ps.json`，示例链延时；完整 **D_theory** 待你把 STR 编成 DAG |
| `rtl/sb_str_skeleton.v` | STR 手写注释 + 占位模块 `SB_STR_SKEL`（仍例化黄金 `SB`） |

示例：

```bash
cd sbox_challenge2026/scripts
python coords_anf.py
python coords_anf.py --pla-dir ../export_pla
python d_theory_skeleton.py
```

STA 自动生成脚本含 **`report_checks ... -nworst 48`** 便于扫最坏路径。

## 已替你落地的「能做的自动化」

赛题最终最优 STR 仍要你迭代结构，但仓库已可直接产出 **第二条 RTL 候选** 并走同一套综合/STA：

1. **生成 ANF 展开 RTL（模块 `SB_ANF`）**  
   ```bash
   cd scripts && python gen_sb_anf_verilog.py
   # 或 make gen-anf
   ```
   生成文件：`rtl/sb_anf_rtl.v`（与黄金表逐位自检在脚本内完成）。

2. **用该顶层跑映射 + STA（Linux / 虚拟机示例）**  
   ```bash
   export CHALLENGE_RTL="rtl/sb_anf_rtl.v"
   export CHALLENGE_TOP=SB_ANF
   python scripts/run_all_experiments.py
   ```

3. **对映射网表估一条「表2 权重」下的最长路近似**（解析 `build/sb_mapped_nangate.v`）：  
   ```bash
   cd scripts && python d_theory_mapped.py
   # 或 make mapped-theory
   ```
   说明：与人工 STR 逐引脚建模相比仍有近似；正式理论分仍以你提交的 DAG 描述为准。

默认仍综合 **`SB` + `sb_lut_baseline.v`**；不设上述环境变量即可。
