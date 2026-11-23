# PDK 说明

本目录不随 Git 仓库分发任何 TSMC PDK、模型、技术文件或从受限 PDK
导出的完整 CDF 报告。

运行本项目需要在授权的 Linux/Cadence 环境中预先安装 TSMC 40 nm
CRN40LP PDK，并使 Virtuoso 能解析逻辑库 `tsmcN40`，Spectre 能读取：

```text
/PDKS/TSMC40nm/models/spectre/toplevel.scs
```

本地开发环境可以保留 `pdk_device_report.txt` 供器件端口和 CDF 参数核对，
但该文件已由 `.gitignore` 排除，不应上传、复制或公开分发。
