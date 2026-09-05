# Clash Verge Rev 接入指南

Clash Verge Rev 应直接导入 JMS 官方提供的 Mihomo / Clash.Meta YAML 订阅。JMS 负责节点和节点更新，本目录只为该订阅增加策略组、远程规则源和高优先级分流规则。

```text
JMS 官方 Mihomo 订阅（私密，仅保存在客户端）
                    ↓
          Clash Verge Rev 主配置
                    +
          Proxy Modular Kit 扩展
                    ↓
        节点更新与分流规则彼此独立
```

## 首次配置

1. 在 JMS 后台复制标记为 `Mihomo / Clash.Meta YAML subscription` 的链接。
2. 在 Clash Verge Rev 的配置页选择“新建/导入”，直接粘贴该链接。不要先经过 ACL4SSR Online、subconverter 或其他转换站。
3. 更新并启用该配置，先确认 JMS 原始节点可以连接。
4. 右键该 JMS 配置并打开“编辑扩展配置”，将 [`merge.yaml`](merge.yaml) 的内容合并进去。
5. 右键同一个配置并打开“编辑代理组”，切换到 YAML，粘贴 [`snippets/groups.yaml`](snippets/groups.yaml) 的完整内容。
6. 右键同一个配置并打开“编辑规则”，切换到 YAML，粘贴 [`snippets/rules.yaml`](snippets/rules.yaml) 的完整内容。
7. 保存后查看运行时配置，确认新增策略组和规则已经生效。

`merge.yaml` 只合并 `rule-providers` 映射；代理组和规则数组分别由 Clash Verge Rev 的“编辑代理组”和“编辑规则”功能管理。这可以保留 JMS 订阅原有节点、策略组和兜底规则。

## 交易组设置

- 在 `📈 美股交易` 中直接选择一个长期稳定的美国节点。
- 不要选择自动测速、负载均衡或故障转移策略组。
- 交易期间不要刷新配置、切换节点、切换 VPN 模式或更换 Wi-Fi/蜂窝网络。
- 完全关闭交易 App 后重新启动，并在连接日志中确认富途、moomoo、长桥相关域名全部命中 `📈 美股交易`。

JMS 订阅刷新会更新服务商提供的主配置，Clash Verge Rev 随后会重新应用附加扩展。正常刷新不会要求把订阅地址复制进本仓库；客户端升级或重新导入配置后，应再次检查运行时配置。

## 安全要求

订阅 URL 是访问凭证，不是普通下载链接。只把它保存在 Clash Verge Rev 本地：

- 不要写入 `merge.yaml`、任何 snippet、README、Issue、PR 或连接日志；
- 不要上传从客户端导出的完整运行时配置，因为其中可能包含节点地址和认证信息；
- 如果链接曾发送到聊天、截图或公开位置，立即在 JMS 后台轮换订阅凭证，并确认旧链接失效；
- 本地备份如确有需要，放入仓库已忽略的 `subscriptions/`、`private/`、`secrets/` 或 `local-profiles/` 目录。

## 更新与排错

建议按以下顺序定位问题：

1. 不启用本仓库扩展时，JMS 配置能否刷新并连接节点；
2. `merge.yaml` 中的远程 `rule-providers` 是否下载成功；
3. 运行时配置是否包含五个自定义策略组；
4. `📈 美股交易` 是否直接列出 JMS 节点且不包含 DIRECT；
5. 交易规则是否排在 China、`GEOIP,CN` 和 MATCH/FINAL 之前；
6. 若重新导入了 JMS 配置，三个扩展入口是否仍绑定到当前配置。

配置源与规则层分开验证，可以快速判断故障来自 JMS 节点、远程规则源还是 Clash Verge 的扩展绑定。
