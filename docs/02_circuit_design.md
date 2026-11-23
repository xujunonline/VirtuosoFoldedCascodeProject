# 电路设计

## 拓扑

最终电路为 PMOS 输入的全差分折叠共源共栅 OTA：

1. `MINP/MINN` 构成 PMOS 差分输入对；
2. `MTAIL` 提供输入对尾电流；
3. `MSINKP/MSINKN` 提供折叠节点下拉偏置；
4. `MFOLDP/MFOLDN` 为 NMOS 折叠共栅器件；
5. `MLOADP/MLOADN` 为 PMOS 上拉电流源；
6. `MCASP/MCASN` 级联 PMOS 负载，提高输出电阻；
7. `OUTP/OUTN` 为全差分输出。

核心 OA schematic 不含理想 CMFB，而是暴露 `VBPL`。测试平台使用行为源根据
`(V(OUTP)+V(OUTN))/2` 调整 `VBPL`，把输出共模稳定在约 0.55 V。这样不同
W/L 扫描点具有可比较的 DC 工作点，同时不影响差模传递函数。

## 最佳尺寸

| 器件组 | W | L | nf |
|---|---:|---:|---:|
| MINP/MINN | 40 µm | 400 nm | 6 |
| MTAIL | 20 µm | 480 nm | 4 |
| MFOLDP/MFOLDN | 20 µm | 480 nm | 4 |
| MSINKP/MSINKN | 10 µm | 480 nm | 2 |
| MLOADP/MLOADN | 20 µm | 640 nm | 4 |
| MCASP/MCASN | 20 µm | 480 nm | 4 |

## 测试条件

| 条件 | 值 |
|---|---:|
| VDD | 1.1 V |
| 输入共模 | 0.55 V |
| 输出目标共模 | 0.55 V |
| 差模 AC 输入 | 1 V 总差模幅度 |
| 输出负载 | 1 pF/输出 |
| AC 扫描 | 1 Hz–100 GHz，50 点/十倍频 |
| 工艺角 | top_tt，27 °C |

## Virtuoso 数据库

来宾中已持久化：

```text
Library: codex_fc_ota
Cell:    folded_cascode_ota
View:    schematic
Path:    /home/userone/codex_fc_ota
```

新的 OCEAN 进程验证结果为：11 个实例、16 个网络、11 个端口。

