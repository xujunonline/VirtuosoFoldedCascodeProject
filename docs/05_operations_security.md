# 运行、维护与安全

## 常用命令

```powershell
.\scripts\verify_remote.ps1
.\scripts\test.ps1
.\scripts\run_ocean.ps1 circuit\ocean\smoke.ocn
.\scripts\run_ocean.ps1 circuit\ocean\verify_schematic.ocn
.\scripts\run_final_sweep.ps1
```

## 虚拟机 IP 变化

如果 VMware NAT 重新分配 IP，需要同步修改：

- `project.json`
- `scripts/*.ps1`

也可以直接调用 Python 脚本并传入 `--host`。

## 密钥轮换

1. 在主机生成新的 ed25519 密钥；
2. 把新公钥加入来宾 `/home/userone/.ssh/authorized_keys`；
3. 验证新密钥登录；
4. 从 `authorized_keys` 删除旧公钥；
5. 替换 `.secrets/virtuoso_vm_ed25519`；
6. 保持 `.secrets` 不进入 Git 或同步盘。

项目内不保存 root 或 userone 密码。曾在聊天中披露的密码应当轮换。

## 恢复 `.bashrc`

如需撤销非交互欢迎图修复：

```bash
cp -p ~/.bashrc.codex-backup-20260719 ~/.bashrc
```

恢复后 SCP 可能再次因欢迎图输出而失败。

## 清理远程运行目录

仿真会在 `/home/userone/codex_*sweeps` 下产生目录。删除前应确认结果已下载；
本项目不会自动删除远程数据。

