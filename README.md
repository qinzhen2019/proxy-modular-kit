# Proxy Modular Kit

面向 Shadowrocket、Stash、FlClash、Clash Meta for Android 和 Clash Verge Rev / Mihomo 的模块化代理规则仓库。它把“节点”和“流量策略”分离：Just My Socks（JMS）原始订阅只在客户端本地提供节点，本仓库只维护策略组、规则、覆写和扩展片段。

项目的首要目标是让富途、moomoo、长桥在一次完整会话中使用同一个固定出口 IP，同时让 AI、GitHub、Google、媒体等流量可以独立选择节点。仓库不依赖 ACL4SSR Online 或其他公共订阅转换后端。

> [!WARNING]
> 代理配置不能消除券商风控、网络中断或交易风险。交易前务必在客户端日志中验证规则命中；交易期间不要切换节点、代理模式或网络出口。

## 支持范围

| 流量类别 | 默认策略 | 设计意图 |
| --- | --- | --- |
| 📈 美股交易 | 手动 `select` | 固定一个稳定美国节点，不测速、不负载均衡、不自动切换 |
| 🤖 AI | 手动 `select` | ChatGPT、Claude、Gemini、Cursor、Windsurf、Copilot 等独立切换 |
| 💻 GitHub | 手动 `select` | Web、Git、Raw、Container Registry、Releases |
| 🌍 Google | 手动 `select` | Google、Gmail、Drive、Translate、API |
| 📺 媒体 | 手动 `select` | YouTube、Netflix、Disney+ |
| Apple | `DIRECT` | App Store、iCloud、Push、Music、Maps 与系统服务 |
| China / LAN | `DIRECT` | 中国大陆网站、国内 App 和局域网 |
| Advertising / Privacy | `REJECT` | 常见广告与追踪域名 |

Apple Intelligence 暂未混入 Apple 直连规则；需要时应单独建立代理模块。TradingView、Yahoo Finance、Nasdaq、Seeking Alpha 等也没有默认绑定交易 IP，避免无谓扩大身份关联范围。

## 仓库结构

```text
RuleSets/manifest.json         模块、策略和上游源的统一清单
RuleSets/*.list                本仓库维护的最小本地规则
RuleSets/upstream-lock.json    blackmatrix7 内容摘要与变更追踪
Scripts/build_configs.py       从统一清单生成桌面与移动端配置
Scripts/validate_rules.py      语法、引用、重复项和敏感信息校验
Scripts/update_rules.py        拉取上游内容并刷新锁文件
Shadowrocket/                  Base.conf 与独立模块
Stash/Overrides/               全量和独立 Override
Clash-Verge/                   现行扩展配置和可视化编辑器片段
Android/FlClash/               FlClash 脚本覆写
Android/Clash-Meta/            Clash Meta for Android 完整配置模板
```

公共服务规则引用活跃维护的 [blackmatrix7/ios_rule_script](https://github.com/blackmatrix7/ios_rule_script)。交易域名和用户补充域名由本仓库维护。所有生成文件都带有 `Generated` 文件头，不应直接编辑。

## 开始使用前

1. 在对应客户端中直接导入 JMS 原始订阅，让 JMS 只负责节点更新。
2. 不要把订阅 URL 复制到本仓库、Issue、PR、截图或日志。
3. 选择一个长期稳定的美国节点供 `📈 美股交易` 使用。
4. 如果 JMS 凭证曾暴露，先重置 Service Password，使旧链接失效。

## Shadowrocket

### 导入完整基础配置

1. 在 Shadowrocket 中保留或添加 JMS 原始订阅。
2. 导入 [`Shadowrocket/Base.conf`](Shadowrocket/Base.conf)。
3. 如果策略组只显示 `PROXY` 而没有具体节点，可在 Shadowrocket 内把 JMS 节点加入对应策略组，或单独启用 `Modules/` 中需要的模块。
4. 在 `📈 美股交易` 中直接选择一个具体美国节点。不要让它长期嵌套自动测速组。

`Base.conf` 的规则顺序是 LAN → 美股交易 → AI / GitHub / Google / 媒体 → Apple / China → 广告与隐私 → 通用代理 → `GEOIP,CN` → `FINAL`。交易规则因此会在中国区域与兜底规则之前命中。

### 只导入模块

`Shadowrocket/Modules/` 包含九个独立模块。只需要固定交易出口时，可启用 `US-Trade.module`，并确保当前配置已存在同名的 `📈 美股交易` 策略组。

## Stash

1. 保留现有 JMS 或其他节点订阅。
2. 如果希望一次启用全部模块，导入 `Stash/Overrides/all.stoverride`；也可只导入某个独立 Override。
3. 新增策略组使用 `include-all: true`，会直接列出当前配置的全部节点与远程节点集，不依赖 ACL4SSR 的策略组名称。
4. 确认 Override 将规则插入原规则顶部；不要对原配置的整个 `rules` 数组做 replace。
5. 在 `📈 美股交易` 中直接选择具体节点；交易组不提供 DIRECT 候选。

不同 Stash 版本或订阅模板对 Override 合并细节可能不同。导入后必须在最终配置预览中确认新增策略组存在，且交易规则位于 `GEOIP,CN,DIRECT` 和 MATCH / FINAL 之前。

## Clash Verge Rev / Mihomo

本仓库按 Clash Verge Rev **v2.5.1** 的现行扩展机制生成配置。官方文档说明：从 v1.7 起，扩展配置只负责映射项覆写/合并，数组的 prepend / append 已移到订阅右键菜单的可视化编辑器。因此不要把旧式 `prepend-rules` 或 `prepend-proxy-groups` 直接粘进 Merge 配置。

完整导入步骤：

1. 右键订阅，打开“编辑扩展配置”，合并 `Clash-Verge/merge.yaml`。它只增加 `rule-providers` 映射，不覆盖订阅原有的规则或策略组数组。
2. 右键订阅，打开“编辑代理组”，切换到 YAML，将 `Clash-Verge/snippets/groups.yaml` 的完整内容粘贴进去。
3. 右键订阅，打开“编辑规则”，切换到 YAML，将 `Clash-Verge/snippets/rules.yaml` 的完整内容粘贴进去。
4. 保存并查看运行时配置，确认 `📈 美股交易` 位于规则顶部。
5. `include-all: true` 会把订阅节点列入手动选择组；交易组不提供 DIRECT 候选，导入后仍须直接选择并核对具体美国节点。

每个 `Clash-Verge/snippets/<module>.yaml` 是便于审阅和选择性导入的 bundle。它包含 `proxy-groups` 与 `rules` 两个子映射；分别把子映射的 `prepend` / `append` / `delete` 内容粘贴到对应的“编辑代理组”和“编辑规则”编辑器。完整导入时优先使用聚合的 `groups.yaml` 和 `rules.yaml`。

参考：[Clash Verge Rev 扩展配置官方说明](https://clash-verge-rev.github.io/guide/extend.html)。

## Android

Android 客户端的完整步骤见 [`Android/README.md`](Android/README.md)。当前配置针对
[FlClash v0.8.94](https://github.com/chen08209/FlClash/releases/tag/v0.8.94) 和
[Clash Meta for Android v2.11.32](https://github.com/MetaCubeX/ClashMetaForAndroid/releases/tag/v2.11.32)。

- FlClash：先导入 JMS Clash/Mihomo 订阅，再把 `Android/FlClash/override.js` 设为该订阅的脚本覆写。脚本只合并策略组、规则源与高优先级规则，保留原订阅节点和兜底规则。
- Clash Meta for Android：复制 `Android/Clash-Meta/config.template.yaml`，只在手机本地替换 JMS 占位符，然后导入这个本地文件。模板本身不保存任何订阅凭证。

两端的 `📈 美股交易` 都是手动 `select`，直接列出 JMS 节点且不提供 DIRECT。JMS provider 的健康检查只测可用性，不会替手动策略组自动切换出口。

## 为什么不能只代理“下单请求”

交易 App 的启动、登录、设备鉴权、行情、订单提交和订单回报可能使用不同域名，也可能复用长连接。只代理看起来像下单接口的一小部分请求，容易造成同一会话出现不同出口 IP、鉴权状态不一致或额外风控验证。因此富途、moomoo 和长桥应从启动到退出全程命中 `📈 美股交易`。

## 查看连接日志和补充遗漏域名

每个客户端的菜单名称略有不同，通常位于“连接 / Connections”“日志 / Logs”或“请求记录”。按以下流程验证：

1. 清空连接日志并完全关闭交易 App 后台。
2. 启动代理，重新打开富途或长桥。
3. 依次完成登录、查看行情、打开订单页。
4. 按 App 名、已知域名或策略名 `📈 美股交易` 过滤连接。
5. 确认相关请求没有命中 DIRECT、China、MATCH 或 FINAL。
6. 对未知域名确认所有权和用途，只记录其可复用的根域名，不记录完整 URL、查询参数或凭证。
7. 将确认后的规则加入 `RuleSets/US-Trade.list`，运行构建和校验，再从头复测。

不要因为域名在交易 App 打开期间出现，就直接将其归入交易组；广告、统计、系统服务或第三方资讯也可能同时连接。

## 本地开发

需要 Python 3.11 或更高版本：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python Scripts/build_configs.py
.venv/bin/python Scripts/build_configs.py --check
.venv/bin/ruff check Scripts
.venv/bin/python Scripts/validate_rules.py
```

修改规则时只编辑 `RuleSets/*.list` 或 `RuleSets/manifest.json`，然后重新运行构建器。`--check` 用于 CI，检测生成文件是否过期。

手动检查并刷新 blackmatrix7 上游摘要：

```bash
.venv/bin/python Scripts/update_rules.py --check
.venv/bin/python Scripts/update_rules.py
```

每周工作流会检查上游内容摘要。发生变化时，它会更新锁文件、重新构建、校验，并创建草稿 PR，不会自动合并到 `main`。

## 安全边界

本仓库禁止提交：

- JMS 原始订阅链接和 Service Password；
- 节点服务器地址、端口、UUID、协议 URI 或完整客户端导出；
- 私有 Token、Cookie、账户信息和包含查询凭证的连接日志；
- `subscriptions/`、`private/`、`secrets/` 等本地目录。

`.gitignore` 只能降低误提交概率，不能让已经提交或截图暴露的凭证重新安全。发生暴露后必须在服务端轮换凭证，并确认旧链接失效。CI 的敏感信息扫描是最后一道辅助检查，不替代人工审阅。

## 配置失效排查

按以下顺序检查：

1. JMS 原始订阅是否能在客户端直接刷新，节点是否可单独连通。
2. 客户端运行时配置中是否实际存在本仓库的策略组和规则。
3. Stash 的 `📈 美股交易` 是否通过 `include-all` 正确列出订阅节点。
4. FlClash 的订阅是否已切到“脚本”覆写，并选中本仓库脚本。
5. Clash Meta for Android 的 JMS 占位符是否已在手机本地替换，provider 是否刷新成功。
6. Clash Verge 是否把 `merge.yaml`、`groups.yaml`、`rules.yaml` 放进了各自对应的编辑器。
7. 远程 rule provider 是否下载成功；失败时查看 GitHub Raw 网络连接和客户端日志。
8. 交易规则是否在 China、GEOIP CN、MATCH 和 FINAL 之前。
9. 客户端 DNS / Fake-IP 模式是否导致日志只显示 IP；必要时同时查看 DNS 日志和嗅探结果。
10. 更新客户端或订阅后，重新预览最终运行时配置，而不是只检查源文件。

## 许可证与上游规则

本仓库代码采用 MIT License。blackmatrix7 规则仍受其上游仓库许可证和声明约束，本仓库只记录来源与内容摘要，不重新授权上游内容。
