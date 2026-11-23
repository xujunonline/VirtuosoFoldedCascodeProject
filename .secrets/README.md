# 本地密钥目录

F 盘为 exFAT，不支持 NTFS ACL，因此本项目不会在这里保存 SSH 私钥。专用私钥默认位于：

```text
%USERPROFILE%\.ssh\virtuoso_vm_ed25519
```

也可通过环境变量 `VIRTUOSO_SSH_KEY` 指向另一个受保护的 NTFS 路径。项目仅包含
`ssh/virtuoso_vm_ed25519.pub` 公钥；不要把私钥复制到本目录、Git 或同步盘。
