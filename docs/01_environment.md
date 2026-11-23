# 环境与远程通道

## 主机与来宾

- Windows 主机运行 VMware Workstation；
- 虚拟机：`RedHat_9_7_A_and_D_10T`；
- NAT IP：`192.168.44.128`；
- SSH 用户：`userone`；
- VMware 共享目录：来宾 `/mnt/hgfs/Share-2`；
- 主机原共享目录：`F:\ic25\RedHat_9_7_A_and_D_10T\Share`。

## Cadence 路径

| 工具 | 来宾路径 |
|---|---|
| OCEAN | `/opt/eda/cadence/IC251/tools/dfII/bin/ocean` |
| Virtuoso | `/opt/eda/cadence/IC251/tools/dfII/bin/virtuoso` |
| Spectre | `/opt/eda/cadence/SPECTRE251/bin/spectre` |

当前 Cadence 的 `-nograph` 包装器依赖来宾未安装的 Xvfb。因此 OCEAN 默认
复用 GNOME 会话：

```text
DISPLAY=:1
XAUTHORITY=/run/user/1000/gdm/Xauthority
```

Spectre 命令行仿真不依赖 X 会话。

## SSH 初始化

`ssh/bootstrap_guest.sh` 将项目公钥幂等加入来宾当前用户的
`~/.ssh/authorized_keys`。来宾 `.bashrc` 原先在非交互会话打印彩色欢迎图，
会破坏 SCP；`ssh/fix_noninteractive_bash.sh` 仅对欢迎图增加交互判断，并留下：

```text
/home/userone/.bashrc.codex-backup-20260719
```

密码只在第一次公钥安装时使用，没有存入项目。

## PDK

- Library：`tsmcN40`
- 工艺：TSMC 40 nm CRN40LP
- 模型入口：`/PDKS/TSMC40nm/models/spectre/toplevel.scs`
- 模型角：`top_tt`
- 标准器件：`nch`、`pch`，额定 1.1 V

本地文件 `pdk/pdk_device_report.txt` 保存了通过 OCEAN 读取的端口和关键 CDF
参数，但它属于 PDK 派生资料，已排除在 Git 仓库之外。公开仓库只保留
`pdk/README.md` 中的安装要求。

