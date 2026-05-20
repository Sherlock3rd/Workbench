# ROK_火山危机 PA 广告打点需求

| 说明 | 本文基于飞书原始设计文档《Rok PA《火山危机》需求文档》和本地最终文件 `asset/ROK_火山危机.html` 提炼。只保留 PA 广告试玩核心行为字段；广告 SDK 或投放平台可统一提供的渠道、设备、时间、session 等公共维度不在每张功能表重复设计。 |
| --- | --- |
| 负责策划 | 待策划确认 |
| 来源 | 原始设计文档：https://t6bdpf8yjg.feishu.cn/wiki/IzonwEhxwio2dvkNd3bcBFRYnOw；最终 PA 文件：`asset/ROK_火山危机.html` |

## 需求描述总览

| 功能名 | 需求描述 | 目的 |
| --- | --- | --- |
| 试玩漏斗 | 记录 PA 从加载、开始游戏、进入火山危机剧情到结局/CTA 的关键节点。 | 判断试玩是否顺利启动、玩家流失集中在哪个步骤。 |
| 分支选择 | 记录玩家在火山危机中的二元选择，例如倒水/建墙、开餐厅/堵火山、扩大规模/阻断岩浆。 | 分析不同选择对参与深度、结局和 CTA 转化的影响。 |
| 交互操作 | 记录长按倒水、画线挖水道、点击鱼群、放置闸门/餐厅、画深沟等核心交互是否成功。 | 判断 PA 的可玩交互是否被理解，以及失败/重试点是否影响体验。 |
| 结局与 CTA | 记录胜利、失败、重新开始、再玩一次和安装/下载点击。 | 评估不同结局对广告转化意愿的影响，优化结尾节奏和 CTA 展示。 |

## 公共维度

| 通用表头 | 字段类型 | 字段说明 |  | 必要性 | 字段备注 |
| --- | --- | --- | --- | --- | --- |
| session_id | string | PA 单次试玩会话 ID。 |  | 用于串联加载、选择、交互和结局。 | 由广告 SDK 或前端生成。 |
| ad_network | string | 投放渠道。 |  | 用于对比不同渠道试玩行为。 | 设计文档列出 Applovin / Unity / Moloco / IronSource / Liftoff / Google / Facebook。 |
| campaign_id | string | 投放计划或广告系列 ID。 |  | 用于按投放计划复盘。 | 若平台可提供则不需要前端重复生成。 |
| creative_id | string | 创意 ID 或素材 ID。 |  | 用于区分 PA 版本。 | 本文口径为 `ROK_火山危机`。 |
| placement_id | string | 广告位 ID。 |  | 用于分析不同广告位表现。 | 平台公共参数。 |
| device_os | string | 设备系统。 |  | 用于区分 iOS/Android/Web 试玩差异。 | 平台公共参数。 |
| event_time | string | 事件发生时间。 |  | 用于计算步骤耗时。 | SDK 公共字段。 |

## paadsession

| 表名 | paadsession |
| --- | --- |
| 功能描述 | PA 试玩会话漏斗打点，覆盖页面加载、开始游戏、剧情展示、进入核心交互、结局展示和 CTA 展示。 |

| 通用表头 | 字段类型 | 字段说明 |  | 必要性 | 字段备注 |
| --- | --- | --- | --- | --- | --- |
| action_type | string | 会话行为节点。 |  | 用于计算 PA 漏斗。 | 建议枚举：load、start_click、intro_show、game_enter、ending_show、cta_show、exit。 |
| scene_id | string | 当前场景或步骤 ID。 |  | 用于定位流失发生在哪个剧情/交互段。 | 建议枚举：menu、volcano_intro、choice1、channel_draw、gate_place、fish_collect、restaurant_place、final_choice、ending。 |
| scene_name | string | 当前场景名称。 |  | 方便策划侧阅读。 | 如火山爆发、挖掘水道、建造过滤闸门、捞鱼、餐厅经营。 |
| elapsed_time | string | 从 PA 加载到当前事件的累计耗时。 |  | 用于判断前 3 秒吸睛和整体试玩时长。 | 单位秒，字段类型仍写 string。 |
| current_danger | string | 当前毁灭进度。 |  | 用于分析危机压力与玩家行为关系。 | HTML 中有 `毁灭` 进度条。 |
| current_money | string | 当前金币数量。 |  | 用于分析经营选择和最终分支。 | HTML 中有金币显示。 |
| current_population | string | 当前人口数量。 |  | 用于衡量失败/污染等后果。 | HTML 中有人口显示。 |
| current_fish | string | 当前渔获数量。 |  | 用于分析捞鱼后进入餐厅链路。 | HTML 中有渔获显示。 |
| result | string | 当前节点结果。 |  | 用于判断节点是否成功展示或进入。 | 建议枚举：success、fail、exit。 |
| fail_reason | string | 节点失败或退出原因。 |  | 用于定位加载、运行或资源问题。 | 建议枚举：load_error、asset_error、user_exit、runtime_error、unknown。 |

## paadchoice

| 表名 | paadchoice |
| --- | --- |
| 功能描述 | PA 分支选择打点，覆盖火山危机中所有二元决策和对应后果。 |

| 通用表头 | 字段类型 | 字段说明 |  | 必要性 | 字段备注 |
| --- | --- | --- | --- | --- | --- |
| choice_id | string | 选择节点 ID。 |  | 用于区分不同分支节点。 | 建议枚举：choice_water_wall、choice_fish_use、choice_profit_use。 |
| choice_name | string | 选择节点名称。 |  | 方便策划侧复盘。 | 如初始灭火方案、鱼群利用、利润使用。 |
| option_id | string | 玩家选择的选项 ID。 |  | 用于统计每个选项选择率。 | 建议枚举：water、wall、restaurant、block_volcano、expand_business、block_lava。 |
| option_text | string | 选项文案。 |  | 用于和最终 HTML 文案核对。 | 如“往火山里倒水熄灭火山”“开设餐厅以赚取金币”。 |
| is_correct_path | string | 是否导向较优路径。 |  | 用于分析玩家是否选择了设计预期路径。 | 建议枚举：true、false、neutral。第 1 个选择设计上不影响后续，可填 neutral。 |
| next_scene_id | string | 选择后进入的下一个场景。 |  | 用于还原分支路径。 | 如 channel_draw、fish_collect、restaurant_place、victory、fail。 |
| outcome_type | string | 选择后果类型。 |  | 用于区分剧情反馈、资源变化、胜负结局。 | 建议枚举：story_feedback、resource_gain、resource_loss、win、fail。 |
| resource_change | string | 该选择带来的资源变化。 |  | 用于分析金币、人口、鱼、毁灭进度变化。 | 建议格式：money:+100;fish:+20;population:-10;danger:+15。 |

## paadinteraction

| 表名 | paadinteraction |
| --- | --- |
| 功能描述 | PA 核心可玩交互打点，覆盖长按、画线、点击、放置等操作是否被理解并完成。 |

| 通用表头 | 字段类型 | 字段说明 |  | 必要性 | 字段备注 |
| --- | --- | --- | --- | --- | --- |
| interaction_id | string | 交互节点 ID。 |  | 用于区分不同操作。 | 建议枚举：hold_water、draw_wall、draw_channel、place_gate、collect_fish、place_restaurant、draw_lava_trench。 |
| interaction_type | string | 交互类型。 |  | 用于判断哪类交互更易失败。 | 建议枚举：hold、draw、click_target、place。 |
| prompt_text | string | 交互提示文案。 |  | 用于核对最终 HTML 指引是否清晰。 | 如“长按火山口倒水”“点击地面放置建筑”。 |
| target_area | string | 目标区域或目标对象。 |  | 用于判断玩家是否理解点击/画线目标。 | 如火山、岩浆、海洋、入海口、北面缺口、南面缺口、鱼群、餐厅安全区。 |
| attempt_index | string | 当前交互第几次尝试。 |  | 用于分析重试次数。 | 首次为 1。 |
| duration | string | 本次交互耗时。 |  | 用于评估操作理解成本。 | 单位秒。 |
| path_valid | string | 画线/放置类操作是否有效。 |  | 用于分析水道、墙、深沟等空间交互是否被理解。 | 建议枚举：true、false、not_applicable。 |
| progress_value | string | 长按或计数类进度。 |  | 用于分析玩家是否半途放弃。 | 如 hold 进度、点击鱼群数量、放置数量。 |
| result | string | 交互结果。 |  | 用于统计成功率。 | 建议枚举：success、fail、cancel。 |
| fail_reason | string | 失败原因。 |  | 用于定位交互阻塞。 | 建议枚举：wrong_area、not_connected、release_early、timeout、target_missing、runtime_error。 |

## paadending

| 表名 | paadending |
| --- | --- |
| 功能描述 | PA 结局和 CTA 打点，覆盖胜利、失败、重新开始、再玩一次、安装/下载点击。 |

| 通用表头 | 字段类型 | 字段说明 |  | 必要性 | 字段备注 |
| --- | --- | --- | --- | --- | --- |
| ending_type | string | 结局类型。 |  | 用于统计不同结局占比。 | 建议枚举：win、fail、restart、replay、cta_click。 |
| ending_reason | string | 触发结局的原因。 |  | 用于判断玩家因哪个分支进入胜负。 | 建议枚举：lava_destroy_city、toxic_water、restaurant_destroyed、greedy_expand、block_lava_success、user_replay、install_click。 |
| final_scene_id | string | 到达结局前的最后场景。 |  | 用于回溯路径。 | 如 restaurant_place、final_choice、lava_trench。 |
| play_duration | string | 从 PA 加载/开始到结局的总时长。 |  | 用于分析试玩深度。 | 单位秒。 |
| choice_path | string | 本局关键选择路径。 |  | 用于分析选择组合和转化关系。 | 建议格式：water>restaurant>block_lava。 |
| interaction_summary | string | 本局核心交互完成概览。 |  | 用于汇总操作表现。 | 建议格式：draw_channel:success;place_gate:fail;collect_fish:success。 |
| cta_shown | string | 是否展示 CTA。 |  | 用于统计 CTA 曝光。 | 建议枚举：true、false。 |
| cta_click | string | 是否点击 CTA。 |  | 用于统计转化意愿。 | 建议枚举：true、false。 |

## 待确认事项

| 序号 | 问题 |
| --- | --- |
| 1 | HTML 当前可见“重新开始/再玩一次”，但未在抽取文本中确认最终安装/下载 CTA 的 DOM 或 SDK 方法名；需要前端确认 CTA 点击事件接入点。 |
| 2 | `current_money/current_population/current_fish/current_danger` 是否由 PA 内部状态统一上报，还是只在结局事件中汇总，需要与广告 SDK/数据组确认。 |
| 3 | 如果投放平台已经提供 `ad_network/campaign_id/creative_id/placement_id`，本需求只需保证本地 PA 事件带 `session_id` 并可与平台回传关联。 |

## 打点说明总结

PA 广告的核心目标不是完整复刻游戏数据，而是判断玩家是否被前 3 秒吸引、是否理解关键交互、在哪些选择和操作上流失，以及什么结局更能推动 CTA。`paadsession` 用于看整体漏斗，`paadchoice` 用于分析二元决策偏好，`paadinteraction` 用于定位画线、长按、点击、放置等试玩操作难点，`paadending` 用于关联结局与转化。后续可以基于启动率、步骤到达率、选择率、交互成功率、重试次数、结局占比和 CTA 点击率，优化开场钩子、交互提示、失败反馈、结尾节奏和安装引导。
