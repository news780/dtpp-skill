# Prompt Templates

## User-facing target-mode prompt

```text
进入目标模式。请根据我上传的产品图，先提取 target_contract.md，不要直接建模。
然后给出可执行计划：如何从设计图拆成功能结构、外观壳体、打印约束、验证清单和版本输出。
确认没有关键问题后，再用 Blender 脚本生成可打印 STL、预览图、design_manifest.json 和 check_report.md。
```

## Implementation prompt

```text
按已确认的 target_contract.md 实施建模。
要求：
1. 新建 generated_vN，不覆盖旧版本；
2. 从模板创建 design_manifest.json，并把全部关键参数写入其中；
3. 用参数化 Blender 脚本先做功能骨架，再做外观壳体；
4. 导出所有 STL 和 preview.blend；
5. 重新导入 STL，按连通组件独立验证；
6. 对 3MF 生成 3mf_manifest.json，确认引用的是当前 STL 哈希；
7. 输出 front、side、top、three-quarter、function 预览图；
8. 完成 check_report.md、视觉验收表和 summary.json；
9. 只报告实际达到的证据等级；只有实物功能测试通过后，才能说“功能已验证”。
```

## Diagnostic prompt for failed prints

```text
用户反馈打印失败。不要先改切片参数。
请先判断失败属于：目标理解、几何拓扑、装配尺寸、打印方向、支撑、材料或切片配置中的哪一类。
检查 STL、blend、3MF 实际引用文件、3mf_manifest.json 与验证报告；输出根因证据，再给最小修改计划。
如果是容器或滴灌件，必须检查连续储液腔、注水/排液/通气路径、壁厚和实物漏水测试，不能只用 manifold 结论代替储水验证。
```

## Visual rejection prompt

```text
当前结构可能通过，但用户认为外观不可用。
不要继续微调同一种失败范式。先总结外观失败原因，识别导致失败的建模范式，提出新的外观生成方法。
功能骨架不动，重做外观壳体，并按 visual-acceptance.md 重新做视觉验收。
```

## Missing-data prompt

```text
我可以继续，但以下约束会影响模型能否真实打印和使用：
1. 目标总尺寸或必须适配对象的尺寸；
2. 打印机、喷嘴和材料；
3. 是否允许支撑；
4. 功能件承受的水、热、载荷或宠物/儿童接触要求。
如果你暂时不补充，我会按默认值继续，并把它们标为 needs confirmation 写入假设表。
```

## Short alias

The shorthand `dtpp` is accepted case-insensitively. Any capitalization means: run the design-to-printable-product-modeling workflow from target contract through validated printable outputs.
