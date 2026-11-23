# Virtuoso 折叠共源共栅差分 OTA 自动化项目

这是一个可复现的 Cadence Virtuoso / OCEAN / Spectre 项目，用于在 TSMC
40 nm CRN40LP PDK 上创建折叠共源共栅全差分 OTA、扫描 MOS W/L，并自动
提取低频增益、0 dB 频率、相位裕度、输出共模和电源电流。

## 已验证结果

最终 CMFB W/L 扫描的最佳点为：

| 指标 | 结果 |
|---|---:|
| 低频差模增益 | 36.93 dB |
| 0 dB/单位增益频率 | 25.47 MHz |
| 相位裕度 | 89.35° |
| 输出共模 | 0.554 V |
| 电源电流 | 66.0 µA |
| 负载 | 1 pF/输出 |

Virtuoso 来宾中已创建并验证：

- Library：`codex_fc_ota`
- Cell/View：`folded_cascode_ota/schematic`
- 11 个 MOS、16 个网络、11 个端口

## 快速开始

先确认 VMware 中的 RedHat 虚拟机已启动，地址仍为 `192.168.44.128`。
SSH 私钥默认从 `%USERPROFILE%\.ssh\virtuoso_vm_ed25519` 读取，也可设置
`VIRTUOSO_SSH_KEY` 指向其他受保护的 NTFS 路径。

```powershell
cd F:\VirtuosoFoldedCascodeProject
.\scripts\verify_remote.ps1
.\scripts\test.ps1
.\scripts\run_final_sweep.ps1
```

结果会写入 `results/generated/`，不会覆盖已验证的 `results/final/`。

重新创建 Virtuoso OA schematic：

```powershell
.\scripts\run_ocean.ps1 circuit\ocean\create_schematic.ocn
```

## 项目结构

```text
VirtuosoFoldedCascodeProject/
├─ src/python/          Python 远程调用、扫参及 PSFASCII 解析
├─ circuit/ocean/       OCEAN/SKILL 原理图创建与验证脚本
├─ circuit/spectre/     Spectre 电路与测试平台模板
├─ config/              W/L 扫描配置
├─ results/final/       最终 CMFB 扫描数据
├─ results/reference/   拓扑演进的对照结果
├─ results/runs/        最终各扫描点的网表、PSFASCII 和日志
├─ pdk/                 PDK 安装要求；受限 PDK/CDF 报告不进入 Git
├─ ssh/                 来宾初始化脚本和公钥
├─ scripts/             一键验证、仿真和测试入口
├─ tests/               Python 单元测试
├─ docs/                设计、环境、自动化及结果文档
└─ .secrets/            密钥位置说明；F 盘中不保存私钥
```

## 重要说明

- 本项目不包含 TSMC PDK 模型文件或 Cadence 软件；运行时使用虚拟机内已有安装。
- `pdk/pdk_device_report.txt`、Spectre 本机日志、`.secrets/` 内容和完整聊天归档
  仅保留在本地，已通过 `.gitignore` 排除，不上传 GitHub。
- 相位裕度由差模开环 AC 在第一个下降沿 0 dB 交点计算。指定完整闭环网络后，
  可进一步增加 `iprobe + stb` 交叉验证。
- 理想连续时间 CMFB 仅用于保持不同 W/L 组合具有可比较的输出共模；核心 OA
  schematic 将 `VBPL` 暴露为端口，便于替换为晶体管级 CMFB。
- 登录密码未写入项目。F 盘为 exFAT，项目不在 F 盘保存私钥；私钥位于受 ACL
  保护的用户 `.ssh` 目录，且仅对应这台来宾。

更多信息见 [docs/](docs/00_index.md)。
