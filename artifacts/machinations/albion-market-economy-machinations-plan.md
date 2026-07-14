# Albion Market Economy Machinations Plan

## 研究目标

拆解《Albion Online》中“装备销毁 + 交易行 / 黑市 + 公会分工”如何同时维持物品供需与银币流动，并促成玩家社交生态中的组织化分工。

本图要回答的主策问题：

- 装备与物品为什么不会无限堆积？
- 银币为什么不会只在玩家之间无损循环？
- 交易行、黑市、PvP/PvE 消耗如何把采集、生产、运输、交易和战斗组织成稳定分工？
- 这套设计中哪些机制可以被其他 MMO 或沙盒经济借鉴？

## 可信度评分

| 项目 | 内容 |
| --- | --- |
| 总分 | 87/100 |
| 结论 | 可进入正式绘图。核心机制资料充足，但实时市场价格、跨城具体品类价差、当前版本局部数值需要实测补充。 |
| 主要来源 | Albion 官方 crafting guide、官方 Black Market feature、Albion Wiki Marketplace、Albion Wiki Black Market、Albion Wiki Local Economies、Albion Wiki Margin / Trading。 |
| 盲区 | PvP 装备破坏概率、黑市买单生成速度、不同城市热门品类价差、玩家公会内部后勤数据。 |

## CEO/主策质询结论

本次不做“Albion 市场说明书”，而是把市场系统拆成一个可评估的经济稳定模型。核心判断是：Albion 不是靠系统定价维持经济，而是用装备持续消耗、局部市场差价、黑市装备 sink、交易税费、运输风险和公会战斗需求，让玩家自发形成生产与后勤分工。

通胀口径同时覆盖：

- 物品 / 装备供给不过剩：装备被 PvP、破坏、黑市与 PvE 掉落循环持续吸收。
- 银币流动不过度膨胀：交易税、订单费、制作站费用、修理和运输风险持续消耗利润空间。

分工口径以公会 / 组织结构为主，关注后勤、制作链、运输队、战斗组、市场操盘之间的协同关系。

## 系统边界

| 类型 | 内容 |
| --- | --- |
| 纳入范围 | 采集、精炼、制造、本地交易行、黑市、PvP 装备损耗、PvE 黑市需求、公会仓库、运输风险、交易税费、组织分工。 |
| 排除范围 | 单件装备战斗数值、职业技能平衡、完整命运板成长、真实实时价格抓取、所有城市品类差价明细。 |
| 版本范围 | 以当前公开资料和官方机制说明为准；实时经济参数后续需用市场数据复核。 |

## 核心循环

### 物品 / 装备循环

采集者产出资源，精炼者转化材料，制造者生产装备。装备进入本地交易行或公会仓库，被战斗组、PvE 玩家或市场买家消耗。PvP 死亡、装备破坏、黑市收购和 PvE 掉落需求共同构成装备 sink，使装备不会长期无损沉淀。

### 银币循环

玩家通过 PvE、交易、生产套利或市场活动获得银币。银币用于购买资源、装备、运输服务、公会后勤补给和市场订单。交易税、订单费、制作站费用、修理成本和运输损失持续抽走一部分银币或利润，使交易不是无损搬运。

### 公会分工循环

大规模 PvP 和领地活动制造稳定装备需求。公会通过仓库、补贴、订单、运输和制作链组织资源。战斗组提供消耗与收益场景，后勤组把资源和银币转成可持续战斗能力，市场操盘者利用本地价差和黑市需求优化资金效率。

## 节点清单

| node_id | display_name | machinations_type | design_meaning | group | x | y | initial_value | flow_rate_or_formula | trigger_condition | label | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| node_gathering | 资源采集 | Source | 采集者从开放世界产出原材料 | supply_chain | 0 | 0 | 0 | 受采集时间、地图资源、风险影响 | 玩家采集行为 | 原材料入口 | 85 |
| node_refining | 精炼 | Converter | 原材料转成可制造材料 | supply_chain | 180 | 0 | 0 | raw_resource -> refined_material | 材料进入精炼站 | 资源加工 | 85 |
| node_crafting | 装备制造 | Converter | 精炼材料转为装备与工具 | supply_chain | 360 | 0 | 0 | refined_material + crafting_fee -> equipment | 制造订单 / 公会需求 | 装备供给 | 90 |
| node_local_market | 本地交易行库存 | Pool | 城市独立市场中的玩家挂单库存 | market | 560 | 0 | 0 | buy_order / sell_order 改变库存 | 玩家挂单和成交 | 局部市场 | 95 |
| node_guild_stock | 公会仓库 | Pool | 公会集中储备装备、材料和补给 | guild | 560 | 180 | 0 | craft + purchase - battle_supply | 公会补给策略 | 组织化缓冲池 | 75 |
| node_pvp_consumption | PvP 装备损耗 | Drain | 死亡、掉落、破坏带来的装备消耗 | sinks | 760 | 120 | 0 | equipment * pvp_destroy_rate | PvP 死亡 / 大规模战斗 | 装备 sink | 70 |
| node_black_market | 黑市 | Converter | 系统生成装备买单，吸收玩家制造装备并转化为 PvE 掉落来源 | sinks | 760 | -80 | 0 | pve_demand -> black_market_buy_order | PvE 击杀 / 开箱需求 | 装备 sink + PvE 供给 | 90 |
| node_pve_demand | PvE 掉落需求 | Source | 怪物击杀和宝箱需求拉动黑市买单 | sinks | 940 | -80 | 0 | mob_kill_rate -> buy_order_pressure | PvE 活跃 | 系统需求 | 85 |
| node_silver_pool | 玩家银币池 | Pool | 玩家可用于交易、制作和后勤的银币 | silver | 360 | 320 | 0 | income - sinks - purchases | PvE / 交易 / 战斗收益 | 购买力 | 80 |
| node_market_tax | 交易税与订单费 | Drain | 成交税、买卖订单费等银币 sink | silver | 560 | 320 | 0 | sell_price * tax + order_value * setup_fee | 挂单 / 成交 | 银币 sink | 95 |
| node_transport_risk | 运输风险 | Gate | 跨城贸易的时间、死亡和货损风险 | guild | 180 | 180 | 0 | profit_margin > transport_risk_cost | 跨城搬运 | 分工门槛 | 75 |
| node_guild_division | 公会分工强度 | Register | 后勤、制作、运输、战斗、市场角色的组织化程度 | guild | 360 | 180 | 0 | demand_pressure + market_complexity + war_frequency | 公会规模化运作 | 社交分工 | 70 |

## 连接清单

| edge_id | from_node | to_node | connection_type | direction | formula_or_condition | design_meaning | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| edge_gather_to_refine | node_gathering | node_refining | Resource | forward | raw_resource_flow | 原材料进入精炼环节 | 90 |
| edge_refine_to_craft | node_refining | node_crafting | Resource | forward | refined_material_flow | 精炼材料进入制造环节 | 90 |
| edge_craft_to_market | node_crafting | node_local_market | Resource | forward | equipment_listed_for_sale | 玩家制造装备进入本地交易行 | 90 |
| edge_craft_to_guild | node_crafting | node_guild_stock | Resource | forward | guild_supply_order | 公会订单或自给生产进入仓库 | 75 |
| edge_market_to_silver | node_local_market | node_silver_pool | Resource | bidirectional | sale_price - fees | 成交让银币在买卖双方之间流转 | 85 |
| edge_market_to_tax | node_local_market | node_market_tax | Resource | forward | setup_fee + transaction_tax | 交易行抽取订单费与成交税 | 95 |
| edge_guild_to_pvp | node_guild_stock | node_pvp_consumption | Resource | forward | battle_supply_consumption | 公会战斗消耗装备储备 | 75 |
| edge_market_to_pvp | node_local_market | node_pvp_consumption | Resource | forward | player_equipment_purchase | 散人或公会从市场购买装备后参与消耗 | 80 |
| edge_pvp_to_demand | node_pvp_consumption | node_crafting | State | feedback | equipment_loss_increases_demand | 装备损耗反向提高制造需求 | 85 |
| edge_pve_to_black_market | node_pve_demand | node_black_market | Trigger | forward | mob_kills_generate_buy_orders | PvE 活跃触发黑市买单需求 | 85 |
| edge_black_market_to_craft | node_black_market | node_crafting | State | feedback | black_market_price_increases_supply | 黑市收购价拉动玩家制造供给 | 85 |
| edge_transport_to_market | node_transport_risk | node_local_market | Modifier | forward | local_price_gap_after_risk | 运输风险保留本地市场差价 | 80 |
| edge_guild_division_to_supply | node_guild_division | node_guild_stock | Modifier | forward | organization_efficiency | 分工提高补给效率和库存稳定性 | 70 |
| edge_silver_to_crafting | node_silver_pool | node_crafting | Resource | forward | material_purchase + crafting_fee | 银币支持购买材料、支付制作费用 | 85 |

## 参数假设

关键数值已同步到 `albion-market-economy-machinations-config.csv`。当前可确认的主要参数包括交易税、订单费、订单有效期和 Completed Transactions 保留期。PvP 装备破坏率、黑市需求速率、运输风险成本属于待实测参数。

## 图层布局建议

- 顶部横向放置物品供应链：资源采集 -> 精炼 -> 装备制造 -> 本地交易行 / 公会仓库。
- 右侧放置装备 sink：PvP 装备损耗、黑市、PvE 掉落需求。
- 底部放置银币流：玩家银币池、交易税与订单费。
- 中部放置组织化门槛：运输风险、公会分工强度。
- 用反馈线从 PvP 损耗和黑市需求回连到制造节点，突出“消耗制造需求”。

## 执行模式建议

建议先使用顾问模式完成 Machinations 手工建图。原因：

- 当前目标是系统理解和设计复盘，不需要立刻网页自动化。
- 图中同时存在物品流、银币流和组织分工，适合先手工调整布局。
- 等节点和连接口径确认后，再研究 Machinations 是否支持导入或复制结构。

## 待确认项

- 是否把黑市视为 `Drain` 还是 `Converter`：它既吸收装备，又把装备转化为 PvE 掉落供给。
- 是否需要进一步拆银币来源：PvE 奖励、玩家交易、活动奖励、黑市付款等。
- 是否需要把公会分工拆成多个独立节点：后勤组、制作组、运输队、战斗组、市场操盘。
- PvP 装备破坏率和黑市买单生成速率需要实测或引用更具体数据。

## 质量与趋势验收

| 检查项 | 当前结论 |
| --- | --- |
| 核心循环闭合 | 已闭合：装备供给 -> 市场 / 公会 -> 消耗 / 黑市 -> 需求回流。 |
| Source/Sink 解释资源增减 | 已覆盖：采集、PvE 需求为 Source；PvP 损耗、交易税费、黑市为 Sink / Converter。 |
| Pool/State 承载关键变量 | 已覆盖：本地市场库存、公会仓库、玩家银币池、公会分工强度。 |
| Gate/Converter 表达限制与转化 | 已覆盖：运输风险、精炼、制造、黑市。 |
| 正反馈/负反馈/瓶颈可见 | 初步可见：装备消耗提高制造需求；交易费和运输风险压缩套利；公会组织缓冲波动。 |
| 正常循环趋势 | 装备持续流转，市场有价差，公会通过后勤维持战斗消耗。 |
| 资源过剩趋势 | 若装备生产过剩，市场价格下降，黑市和 PvP 消耗吸收部分供给。 |
| 资源枯竭趋势 | 若装备供给不足，价格上升，刺激采集、制造和跨城运输。 |
| 转化瓶颈趋势 | 运输风险、制作成本、订单费、黑市买单价格可能成为瓶颈。 |
