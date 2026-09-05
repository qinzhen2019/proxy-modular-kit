# Android 配置

本目录支持 FlClash v0.8.94 和 Clash Meta for Android v2.11.32。两种方式都只在手机本地保存 JMS 订阅，不要把订阅 URL 提交到 GitHub。

## FlClash（推荐）

FlClash 可以在原始订阅上执行 JavaScript 覆写，因此不需要复制或改写 JMS 订阅地址。

1. 在“配置”中直接导入 JMS 官方的 Mihomo / Clash.Meta YAML 订阅，并确认节点能正常连接；不要经过订阅转换网站。
2. 打开“工具/配置脚本”，新增脚本，将 [`FlClash/override.js`](FlClash/override.js) 的内容粘贴进去并保存为 `Proxy Modular Kit`。脚本编辑器也支持从远程地址下载。
3. 回到该 JMS 配置的“覆写”，选择“脚本”，勾选刚保存的 `Proxy Modular Kit`。
4. 预览最终配置，确认出现 `📈 美股交易`、`🤖 AI`、`💻 GitHub`、`🌍 Google` 和 `📺 媒体`。
5. 启动 VPN，在 `📈 美股交易` 中直接选一个稳定美国节点。不要选择自动测速或故障转移组。

脚本会将本仓库规则放在订阅原规则之前，同时保留订阅原有节点、策略组和兜底规则。以后刷新 JMS 订阅时，覆写会重新应用。

脚本 Raw 地址：

```text
https://raw.githubusercontent.com/qinzhen2019/proxy-modular-kit/main/Android/FlClash/override.js
```

## Clash Meta for Android

该客户端没有 FlClash 同类的 JavaScript 覆写入口，因此使用完整配置模板：

1. 下载 [`Clash-Meta/config.template.yaml`](Clash-Meta/config.template.yaml)，复制成一个仅保存在手机本地的新文件。
2. 用文本编辑器将 `REPLACE_WITH_JMS_MIHOMO_SUBSCRIPTION_URL` 替换为 JMS 官方的 Mihomo / Clash.Meta YAML 订阅 URL，保留模板已有的双引号，不要上传修改后的文件。
3. 在 Clash Meta for Android 中从本地文件导入修改后的 YAML，选中它并启动 VPN。
4. 打开 provider 页面，确认 `JMS` 和 `blackmatrix7-*` 都能刷新成功。
5. 在 `📈 美股交易` 中直接选择一个具体美国节点，然后清空日志并重新启动富途或长桥做命中测试。

JMS URL 必须返回 Clash/Mihomo YAML，并包含顶层 `proxies:`。如果 provider 报格式错误，请在 JMS 后台选择 Clash/Mihomo 输出格式；不要使用仅包含单节点 URI 的纯文本/Base64 订阅。

模板 Raw 地址：

```text
https://raw.githubusercontent.com/qinzhen2019/proxy-modular-kit/main/Android/Clash-Meta/config.template.yaml
```

## 交易验证

无论使用哪个客户端，都要确认富途、moomoo 和长桥相关连接命中 `📈 美股交易`，而不是 DIRECT、China、GEOIP CN 或 MATCH。交易期间不要切换策略节点、VPN 或 Wi-Fi/蜂窝网络。
