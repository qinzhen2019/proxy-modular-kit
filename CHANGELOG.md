# Changelog

本项目遵循 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/) 的结构。

## [Unreleased]

### Added

- 建立 Shadowrocket、Stash 与 Clash Verge Rev / Mihomo 的模块化目录。
- 以 `RuleSets/manifest.json` 和本地规则清单作为统一构建源。
- 增加固定出口的美股交易策略，以及 AI、GitHub、Google、媒体等独立策略。
- 增加构建、上游锁定、规则校验和敏感信息扫描脚本。
- 增加 GitHub Actions 校验与上游规则更新 PR 工作流。
- 增加 FlClash 脚本覆写和 Clash Meta for Android 完整配置模板。
- 增加 Clash Verge Rev 直接导入 JMS 官方 Mihomo 订阅的独立接入与排错指南。
- 敏感信息扫描新增 JMS 订阅端点和 UUID 查询凭证检测。

### Changed

- Clash/Mihomo 文档统一改用 JMS 官方 Mihomo / Clash.Meta YAML 订阅，不再把公共转换站作为链路组成部分。
- Android 模板使用更明确的 Mihomo 订阅占位符，并扩展本地私密配置的忽略规则。

### Fixed

- 修正 Stash 将远程规则 URL 误当作 `RULE-SET` 名称的问题，改为原生 `rule-providers` 引用。
- Stash 策略组改为直接包含全部节点，交易组不再依赖外部组名或提供 DIRECT 候选。
