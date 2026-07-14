import argparse
import html
import json
import xml.etree.ElementTree as ET
from pathlib import Path


NODE_TAGS = {
    "mxPoolShapeCell": "Pool",
    "mxMachinationRegisterCell": "Register",
    "mxConverterShapeCell": "Converter",
    "mxGateShapeCell": "Gate",
    "mxDrainShapeCell": "Drain",
    "mxSourceShapeCell": "Source",
}

CONNECTION_TAGS = {
    "mxResourceConnectionCell": "resource",
    "mxStateConnectionCell": "state",
}

DEFAULT_PROBLEM_EDGE_IDS = {"1164", "1166", "1170", "1171"}
DEFAULT_PROBLEM_NODE_IDS = {"1646", "1604", "1627", "1641", "1178", "1637", "1645", "1614"}
REDRAW_PROBLEM_NODE_IDS = {"1148", "2701", "678"}
REDRAW_PROBLEM_EDGE_IDS = {"1159", "1164", "1170", "1171", "2702", "5485"}
REDRAW_ADDED_NODE_IDS = {
    "redraw_market_buy_demand",
    "redraw_silver_fast_travel",
    "redraw_silver_island",
    "redraw_silver_respec",
    "redraw_consumable_sink",
}
REDRAW_ADDED_EDGE_IDS = {
    "redraw_silver_to_market_buy_demand",
    "redraw_market_buy_demand_to_match",
    "redraw_silver_fast_travel",
    "redraw_silver_island",
    "redraw_silver_respec",
    "redraw_consumable_use_drain",
    "redraw_pvp_consumable_demand",
    "redraw_pve_consumable_demand",
    "redraw_gather_consumable_demand",
}
REDRAW_REMOVED_EDGE_IDS = {"1162", "1186"}


def calculate_view_box(nodes):
    xs = [node["x"] for node in nodes] + [node["x"] + node["w"] for node in nodes]
    ys = [node["y"] for node in nodes] + [node["y"] + node["h"] for node in nodes]
    return [
        round(min(xs) - 220, 2),
        round(min(ys) - 180, 2),
        round(max(xs) - min(xs) + 640, 2),
        round(max(ys) - min(ys) + 440, 2),
    ]


def redraw_node(node_id, kind, label, x, y, formula="", activation="", w=46, h=46):
    return {
        "id": node_id,
        "kind": kind,
        "label": label,
        "x": x,
        "y": y,
        "w": w,
        "h": h,
        "formula": formula,
        "activation": activation,
    }


def redraw_edge(edge_id, kind, source, target, label="", formula="", resource=""):
    return {
        "id": edge_id,
        "kind": kind,
        "from": source,
        "to": target,
        "label": label,
        "formula": formula,
        "resource": resource,
    }


def build_albion_reference_redraw_view():
    nodes = [
        redraw_node("r_raw_source", "Source", "资源采集", 0, 360, "采集时间 * 地图资源"),
        redraw_node("r_raw_split", "Gate", "资源分级", 170, 360, "T1-T4/T5-T6/T7-T8"),
        redraw_node("r_raw_t14", "Pool", "T1-T4原料库存", 340, 140),
        redraw_node("r_raw_t56", "Pool", "T5-T6原料库存", 340, 360),
        redraw_node("r_raw_t78", "Pool", "T7-T8原料库存", 340, 580),
        redraw_node("r_refine_t14", "Converter", "T1-T4精炼", 530, 140, "原料 -> 精炼材料", "automatic"),
        redraw_node("r_refine_t56", "Converter", "T5-T6精炼", 530, 360, "原料 -> 精炼材料", "automatic"),
        redraw_node("r_refine_t78", "Converter", "T7-T8精炼", 530, 580, "原料 -> 精炼材料", "automatic"),
        redraw_node("r_craft_t14", "Converter", "T1-T4制造", 720, 140, "材料 + 制作费 -> 装备", "automatic"),
        redraw_node("r_craft_t56", "Converter", "T5-T6制造", 720, 360, "材料 + 制作费 -> 装备", "automatic"),
        redraw_node("r_craft_t78", "Converter", "T7-T8制造", 720, 580, "材料 + 制作费 -> 装备", "automatic"),
        redraw_node("r_equip_t14", "Pool", "T1-T4装备库存", 910, 140),
        redraw_node("r_equip_t56", "Pool", "T5-T6装备库存", 910, 360),
        redraw_node("r_equip_t78", "Pool", "T7-T8装备库存", 910, 580),
        redraw_node("r_flow_t14", "Gate", "T1-T4装备流向", 1100, 140, "卖单 / 黑市 / 公会 / 自用"),
        redraw_node("r_flow_t56", "Gate", "T5-T6装备流向", 1100, 360, "卖单 / 黑市 / 公会 / 自用"),
        redraw_node("r_flow_t78", "Gate", "T7-T8装备流向", 1100, 580, "卖单 / 黑市 / 公会 / 自用"),
        redraw_node("r_sell_order", "Pool", "玩家卖单", 1280, 150),
        redraw_node("r_market_stock", "Pool", "本地交易行库存装备", 1660, 120),
        redraw_node("r_buy_order", "Pool", "玩家买单", 1280, 510),
        redraw_node("r_match", "Converter", "交易行成交出库", 1660, 470, "库存装备 + 买单 -> 买家持有", "automatic"),
        redraw_node("r_player_use", "Pool", "玩家装备持有/使用", 2040, 330),
        redraw_node("r_pvp", "Gate", "PvP 战斗判定", 2320, 330, "掉落 / 破坏"),
        redraw_node("r_pvp_loot", "Pool", "PvP 战利品回流", 2600, 190),
        redraw_node("r_pvp_destroy", "Drain", "PvP 装备破坏", 2600, 470, "装备 sink"),
        redraw_node("r_black_t14_trade", "Converter", "T1-T4 黑市收购", 1280, 700, "T1-T4装备 -> 系统付款", "automatic"),
        redraw_node("r_black_t56_trade", "Converter", "T5-T6 黑市收购", 1280, 860, "T5-T6装备 -> 系统付款", "automatic"),
        redraw_node("r_black_t78_trade", "Converter", "T7-T8 黑市收购", 1280, 1020, "T7-T8装备 -> 系统付款", "automatic"),
        redraw_node("r_black_t14_price", "Register", "T1-T4 黑市收购价", 1460, 650, "20"),
        redraw_node("r_black_t56_price", "Register", "T5-T6 黑市收购价", 1460, 860, "40"),
        redraw_node("r_black_t78_price", "Register", "T7-T8 黑市收购价", 1460, 1070, "100"),
        redraw_node("r_black_coin", "Pool", "黑市 NPC 银币流入统计", 1660, 790, "系统流入银币"),
        redraw_node("r_black_sink", "Drain", "黑市回收销毁", 1660, 1120, "装备 sink"),
        redraw_node("r_mob_stock", "Pool", "PvE掉落库", 2040, 860),
        redraw_node("r_pve_kill", "Gate", "PvE 击杀/开箱", 2320, 790, "触发掉落抽取"),
        redraw_node("r_pve_drop", "Gate", "PvE掉落分拣", 2600, 790, "按装备档位回流库存"),
        redraw_node("r_player_silver", "Pool", "玩家交易银币池", 1660, 1290),
        redraw_node("r_fee_sink", "Drain", "交易税/订单费/制作费", 2040, 1290, "银币 sink"),
        redraw_node("r_price_signal", "Register", "市场价格信号", 2320, 1290, "买单压力 - 卖单压力 - 库存 + 黑市价 + PvP消耗 + 跨城价差"),
        redraw_node("r_transport", "Gate", "跨城运输风险", 2600, 1290, "价差 > 风险成本"),
        redraw_node("r_guild_stock", "Pool", "公会装备仓库", 1660, 1530),
        redraw_node("r_guild_division", "Register", "公会分工强度", 2320, 1530, "战斗频率 + 后勤需求 + 市场复杂度"),
        redraw_node("r_role_gather", "Register", "采集者", 0, 760, "1"),
        redraw_node("r_role_refine", "Register", "精炼者", 530, 760, "1"),
        redraw_node("r_role_craft", "Register", "制造者", 720, 760, "1"),
        redraw_node("r_role_market", "Register", "市场商人", 1660, -80, "1"),
        redraw_node("r_role_transport", "Register", "跨城运输者", 2600, 1490, "1"),
        redraw_node("r_role_pvp", "Register", "PvP 战斗玩家", 2320, 90, "1"),
        redraw_node("r_role_pve", "Register", "PvE 刷取玩家", 2320, 620, "1"),
        redraw_node("r_role_guild", "Register", "公会后勤", 1660, 1730, "1"),
    ]
    for node in nodes:
        if node["x"] >= 1280:
            node["x"] = round(1100 + (node["x"] - 1100) * 1.6 + 230, 2)
        if node["x"] >= 1500 and node["y"] >= 650:
            node["y"] = round(650 + (node["y"] - 650) * 1.12, 2)
    edges = [
        redraw_edge("re_raw_split", "resource", "r_raw_source", "r_raw_split", "原料产出", "170"),
        redraw_edge("re_split_raw_t14", "resource", "r_raw_split", "r_raw_t14", "基础资源", "100"),
        redraw_edge("re_split_raw_t56", "resource", "r_raw_split", "r_raw_t56", "标准资源", "50"),
        redraw_edge("re_split_raw_t78", "resource", "r_raw_split", "r_raw_t78", "稀有资源", "20"),
        redraw_edge("re_raw_t14_refine", "resource", "r_raw_t14", "r_refine_t14", "T1-T4原料", "3"),
        redraw_edge("re_raw_t56_refine", "resource", "r_raw_t56", "r_refine_t56", "T5-T6原料", "3"),
        redraw_edge("re_raw_t78_refine", "resource", "r_raw_t78", "r_refine_t78", "T7-T8原料", "3"),
        redraw_edge("re_refine_t14_craft", "resource", "r_refine_t14", "r_craft_t14", "T1-T4材料", "2"),
        redraw_edge("re_refine_t56_craft", "resource", "r_refine_t56", "r_craft_t56", "T5-T6材料", "2"),
        redraw_edge("re_refine_t78_craft", "resource", "r_refine_t78", "r_craft_t78", "T7-T8材料", "2"),
        redraw_edge("re_craft_t14_stock", "resource", "r_craft_t14", "r_equip_t14", "T1-T4装备", "100"),
        redraw_edge("re_craft_t56_stock", "resource", "r_craft_t56", "r_equip_t56", "T5-T6装备", "50"),
        redraw_edge("re_craft_t78_stock", "resource", "r_craft_t78", "r_equip_t78", "T7-T8装备", "10"),
        redraw_edge("re_stock_t14_gate", "resource", "r_equip_t14", "r_flow_t14", "待分配装备", "100"),
        redraw_edge("re_stock_t56_gate", "resource", "r_equip_t56", "r_flow_t56", "待分配装备", "50"),
        redraw_edge("re_stock_t78_gate", "resource", "r_equip_t78", "r_flow_t78", "待分配装备", "10"),
        redraw_edge("re_gate_t14_sell", "resource", "r_flow_t14", "r_sell_order", "低阶玩家挂卖", "10%"),
        redraw_edge("re_gate_t56_sell", "resource", "r_flow_t56", "r_sell_order", "中阶玩家挂卖", "50%"),
        redraw_edge("re_gate_t78_sell", "resource", "r_flow_t78", "r_sell_order", "高阶玩家挂卖", "10%"),
        redraw_edge("re_sell_market", "resource", "r_sell_order", "r_market_stock", "进入本地库存", "1"),
        redraw_edge("re_buy_match", "resource", "r_buy_order", "r_match", "购买需求", "120"),
        redraw_edge("re_market_match", "resource", "r_market_stock", "r_match", "可售装备", "1"),
        redraw_edge("re_match_use", "resource", "r_match", "r_player_use", "买家获得装备", "1"),
        redraw_edge("re_use_pvp", "resource", "r_player_use", "r_pvp", "战斗携带", "1"),
        redraw_edge("re_pvp_loot", "resource", "r_pvp", "r_pvp_loot", "掉落回流", "70%"),
        redraw_edge("re_pvp_destroy", "resource", "r_pvp", "r_pvp_destroy", "碎裂破坏", "30%"),
        redraw_edge("re_loot_market", "resource", "r_pvp_loot", "r_market_stock", "二次出售", "1"),
        redraw_edge("re_gate_t14_black", "resource", "r_flow_t14", "r_black_t14_trade", "低阶黑市供给", "60%"),
        redraw_edge("re_gate_t56_black", "resource", "r_flow_t56", "r_black_t56_trade", "中阶黑市供给", "45%"),
        redraw_edge("re_gate_t78_black", "resource", "r_flow_t78", "r_black_t78_trade", "高阶黑市供给", "50%"),
        redraw_edge("re_gate_t14_pvp", "resource", "r_flow_t14", "r_player_use", "低阶自用/PvP", "5%"),
        redraw_edge("re_gate_t56_pvp", "resource", "r_flow_t56", "r_player_use", "中阶自用/PvP", "5%"),
        redraw_edge("re_gate_t78_pvp", "resource", "r_flow_t78", "r_player_use", "高阶自用/PvP", "20%"),
        redraw_edge("re_black_t14_coin", "resource", "r_black_t14_trade", "r_black_coin", "T1-T4 NPC 付款", "20"),
        redraw_edge("re_black_t56_coin", "resource", "r_black_t56_trade", "r_black_coin", "T5-T6 NPC 付款", "40"),
        redraw_edge("re_black_t78_coin", "resource", "r_black_t78_trade", "r_black_coin", "T7-T8 NPC 付款", "100"),
        redraw_edge("re_black_t14_sink", "resource", "r_black_t14_trade", "r_black_sink", "低阶/过量销毁", "20%"),
        redraw_edge("re_black_t56_sink", "resource", "r_black_t56_trade", "r_black_sink", "中阶回收销毁", "15%"),
        redraw_edge("re_black_t78_sink", "resource", "r_black_t78_trade", "r_black_sink", "高阶回收销毁", "10%"),
        redraw_edge("re_black_t14_mob", "resource", "r_black_t14_trade", "r_mob_stock", "低阶回流掉落库", "80%"),
        redraw_edge("re_black_t56_mob", "resource", "r_black_t56_trade", "r_mob_stock", "中阶回流掉落库", "85%"),
        redraw_edge("re_black_t78_mob", "resource", "r_black_t78_trade", "r_mob_stock", "高阶回流掉落库", "90%"),
        redraw_edge("re_pve_mob", "state", "r_pve_kill", "r_mob_stock", "触发掉落抽取", "1"),
        redraw_edge("re_mob_drop", "resource", "r_mob_stock", "r_pve_drop", "刷取掉落", "1"),
        redraw_edge("re_pve_sort_t14", "resource", "r_pve_drop", "r_equip_t14", "T1-T4掉落回流", "1"),
        redraw_edge("re_pve_sort_t56", "resource", "r_pve_drop", "r_equip_t56", "T5-T6掉落回流", "1"),
        redraw_edge("re_pve_sort_t78", "resource", "r_pve_drop", "r_equip_t78", "T7-T8掉落回流", "1"),
        redraw_edge("re_silver_buy", "resource", "r_player_silver", "r_buy_order", "玩家购买力", "120"),
        redraw_edge("re_match_silver", "resource", "r_match", "r_player_silver", "卖家所得", "100"),
        redraw_edge("re_fee_sink", "resource", "r_player_silver", "r_fee_sink", "订单费/税/制作费", "6.5%"),
        redraw_edge("re_gate_t78_guild", "resource", "r_flow_t78", "r_guild_stock", "高阶公会补给", "20%"),
        redraw_edge("re_guild_use", "resource", "r_guild_stock", "r_player_use", "战斗发装", "1"),
        redraw_edge("re_buy_price", "state", "r_buy_order", "r_price_signal", "买单压力", "1"),
        redraw_edge("re_sell_price", "state", "r_sell_order", "r_price_signal", "卖单压力", "-1"),
        redraw_edge("re_stock_price", "state", "r_market_stock", "r_price_signal", "库存压力", "-1"),
        redraw_edge("re_black_price", "state", "r_black_coin", "r_price_signal", "黑市价格", "1"),
        redraw_edge("re_destroy_price", "state", "r_pvp_destroy", "r_price_signal", "装备消耗", "1"),
        redraw_edge("re_price_craft_t14", "state", "r_price_signal", "r_craft_t14", "刺激低阶制造", "1"),
        redraw_edge("re_price_craft_t56", "state", "r_price_signal", "r_craft_t56", "刺激中阶制造", "1"),
        redraw_edge("re_price_craft_t78", "state", "r_price_signal", "r_craft_t78", "刺激高阶制造", "1"),
        redraw_edge("re_price_transport", "state", "r_price_signal", "r_transport", "套利动机", "1"),
        redraw_edge("re_transport_market", "state", "r_transport", "r_market_stock", "跨城补给调节", "1"),
        redraw_edge("re_guild_division", "state", "r_guild_division", "r_guild_stock", "后勤效率", "1"),
        redraw_edge("re_pvp_guild", "state", "r_pvp", "r_guild_division", "稳定消耗推动分工", "1"),
        redraw_edge("re_market_guild", "state", "r_price_signal", "r_guild_division", "市场复杂度推动分工", "1"),
        redraw_edge("re_price_t14_to_trade", "state", "r_black_t14_price", "r_black_t14_trade", "收购价", "20"),
        redraw_edge("re_price_t56_to_trade", "state", "r_black_t56_price", "r_black_t56_trade", "收购价", "40"),
        redraw_edge("re_price_t78_to_trade", "state", "r_black_t78_price", "r_black_t78_trade", "收购价", "100"),
        redraw_edge("re_role_gather", "state", "r_role_gather", "r_raw_source", "执行采集", "1"),
        redraw_edge("re_role_refine_t14", "state", "r_role_refine", "r_refine_t14", "执行精炼", "1"),
        redraw_edge("re_role_refine_t56", "state", "r_role_refine", "r_refine_t56", "执行精炼", "1"),
        redraw_edge("re_role_refine_t78", "state", "r_role_refine", "r_refine_t78", "执行精炼", "1"),
        redraw_edge("re_role_craft_t14", "state", "r_role_craft", "r_craft_t14", "执行制造", "1"),
        redraw_edge("re_role_craft_t56", "state", "r_role_craft", "r_craft_t56", "执行制造", "1"),
        redraw_edge("re_role_craft_t78", "state", "r_role_craft", "r_craft_t78", "执行制造", "1"),
        redraw_edge("re_role_market", "state", "r_role_market", "r_match", "执行挂单/套利", "1"),
        redraw_edge("re_role_transport", "state", "r_role_transport", "r_transport", "执行运输", "1"),
        redraw_edge("re_role_pvp", "state", "r_role_pvp", "r_pvp", "发起战斗", "1"),
        redraw_edge("re_role_pve", "state", "r_role_pve", "r_pve_kill", "刷怪开箱", "1"),
        redraw_edge("re_role_guild", "state", "r_role_guild", "r_guild_stock", "组织补给", "1"),
    ]
    return {
        "id": "redraw",
        "title": "讨论重绘图",
        "description": "按 Machinations 习惯重新排布，用于讨论和手工照抄；不是原坐标校验图。",
        "viewBox": calculate_view_box(nodes),
        "nodes": nodes,
        "edges": edges,
        "problemNodeIds": [],
        "problemEdgeIds": [],
        "explanations": [
            "前半段保留已确认的采集、资源分级、三档精炼、三档制造和三档装备库存，不再把装备分级合并成一个总池。",
            "玩家交易银币只表示玩家之间转移：买单消耗购买力，交易行成交出库后装备进入买家持有，银币进入卖家侧，本身不创造系统银币。",
            "黑市 NPC 银币单独标记为系统流入统计，因为这是 NPC 向玩家付款，和玩家交易市场银币不是同一种口径。",
            "黑市收购价同步新图数值：T1-T4 为 20，T5-T6 为 40，T7-T8 为 100；银币流入直接用这些数值跑通。",
            "黑市交易后的装备分成两类：一部分回流 PvE掉落库，再经 PvE掉落分拣回到三档装备库存；一部分进入黑市回收销毁，作为装备 sink。",
            "PvE 击杀/开箱是 Gate，不是 Source；它只用 State 线触发 PvE掉落库释放装备，不凭空生成装备。",
            "角色标记使用 Register 表示玩家分工：采集者、精炼者、制造者、市场商人、跨城运输者、PvP 战斗玩家、PvE 刷取玩家和公会后勤分别驱动对应环节。",
            "PvP 线只承担装备出口与回流：战斗后分成战利品回流和装备破坏，不再让交易行成交出库直接同时生成 PvP/PvE 装备。",
            "市场价格信号只用状态线接收买单、卖单、库存、黑市价格、装备消耗和跨城价差，再反馈制造、运输和公会分工。",
        ],
    }


def build_albion_redraw_view(original_nodes, original_edges):
    nodes = [dict(node) for node in original_nodes]
    edges = [dict(edge) for edge in original_edges if edge["id"] not in REDRAW_REMOVED_EDGE_IDS]
    node_map = {node["id"]: node for node in nodes}

    if "1148" in node_map:
        node_map["1148"]["label"] = "交易行成交出库"
        node_map["1148"]["kind"] = "Gate"
        node_map["1148"]["formula"] = "库存装备 + 买单 -> 买家持有"
    if "2701" in node_map:
        node_map["2701"]["label"] = "交易行成交出库"
        node_map["2701"]["kind"] = "Gate"
        node_map["2701"]["formula"] = "库存装备 -> 买家持有"
    if "678" in node_map:
        node_map["678"]["label"] = "玩家装备持有/使用"

    nodes.extend(
        [
            redraw_node("redraw_market_buy_demand", "Register", "玩家买单/购买需求", 2860, 780, "银币购买力 + 装备需求"),
            redraw_node("redraw_silver_fast_travel", "Drain", "快速旅行/传送费", 2580, 2820, "银币 sink"),
            redraw_node("redraw_silver_island", "Drain", "岛屿/建筑维护", 2780, 2820, "银币 sink"),
            redraw_node("redraw_silver_respec", "Drain", "自动专精/声望转化", 2980, 2820, "银币 sink"),
            redraw_node("redraw_consumable_sink", "Drain", "消耗品使用消耗", 2200, 2100, "食物/药水 sink"),
        ]
    )

    for edge in edges:
        if edge["id"] == "1159":
            edge["kind"] = "state"
            edge["from"] = "1146"
            edge["to"] = "1148"
            edge["label"] = "购买需求触发"
            edge["formula"] = "1"
        elif edge["id"] == "1164":
            edge["from"] = "1148"
            edge["to"] = "678"
            edge["label"] = "买家获得装备"
            edge["formula"] = "1"
        elif edge["id"] == "2702":
            edge["from"] = "2701"
            edge["to"] = "678"
            edge["label"] = "买家获得装备"
            edge["formula"] = "1"
        elif edge["id"] == "1170":
            edge["from"] = "1161"
            edge["to"] = "1149"
            edge["label"] = "订单创建费"
            if edge["formula"] in {"", "-5", "5"}:
                edge["formula"] = "5"
            edge["resource"] = "银币"
        elif edge["id"] == "1171":
            edge["from"] = "1161"
            edge["to"] = "1150"
            edge["label"] = "成交税"
            if edge["formula"] in {"", "-10", "10"}:
                edge["formula"] = "10"
            edge["resource"] = "银币"
        elif edge["id"] == "1187":
            edge["from"] = "1182"
            edge["to"] = "1154"
            edge["label"] = "执行运输"
            edge["formula"] = "1"
        elif edge["id"] == "5485":
            edge["label"] = "剩余进入市场/黑市流向"
            edge["formula"] = "20%"

    edges.extend(
        [
            redraw_edge("redraw_silver_to_market_buy_demand", "state", "1161", "redraw_market_buy_demand", "购买力形成买单", "1"),
            redraw_edge("redraw_market_buy_demand_to_match", "state", "redraw_market_buy_demand", "2701", "买单触发成交", "1"),
            redraw_edge("redraw_silver_fast_travel", "resource", "1161", "redraw_silver_fast_travel", "快速旅行/传送费", "200"),
            redraw_edge("redraw_silver_island", "resource", "1161", "redraw_silver_island", "岛屿/建筑维护", "500"),
            redraw_edge("redraw_silver_respec", "resource", "1161", "redraw_silver_respec", "自动专精/声望转化", "1000"),
            redraw_edge("redraw_consumable_use_drain", "resource", "5482", "redraw_consumable_sink", "大部分用后消耗", "80%"),
            redraw_edge("redraw_pvp_consumable_demand", "state", "884", "redraw_consumable_sink", "战斗消耗需求", "1"),
            redraw_edge("redraw_pve_consumable_demand", "state", "1906", "redraw_consumable_sink", "刷取消耗需求", "1"),
            redraw_edge("redraw_gather_consumable_demand", "state", "1542", "redraw_consumable_sink", "采集增益需求", "1"),
        ]
    )

    return {
        "id": "redraw",
        "title": "讨论重绘图",
        "description": "基于最新原图的局部修正版；未列为问题的节点和布局保持原样。",
        "viewBox": calculate_view_box(nodes),
        "nodes": nodes,
        "edges": edges,
        "problemNodeIds": sorted(REDRAW_PROBLEM_NODE_IDS | REDRAW_ADDED_NODE_IDS),
        "problemEdgeIds": sorted(REDRAW_PROBLEM_EDGE_IDS | REDRAW_ADDED_EDGE_IDS),
        "explanations": [
            "讨论重绘图只局部修改有问题的节点和连线；未列为问题的节点保持原坐标和原布局。",
            "交易行成交出库改为 Gate；买单用 State 触发出库，装备资源仍从本地交易行库存流向玩家装备持有/使用，避免 Converter 把装备档位抹平成单一资源。",
            "删除交易行成交出库到玩家银币池的卖家所得资源线；玩家间交易对总银币池净变化为 0，只保留税费 Drain 和系统银币流入。",
            "订单创建费和成交税改为玩家银币池流向 Drain，避免用负数从费用节点回流到银币池。",
            "原图已有金币充值、买金、卖金、月卡和外观链路；讨论重绘图不再额外叠加第二套金币模块，避免出现重复金币图。",
            "额外补充三个常见银币出口检查：快速旅行/传送费、岛屿/建筑维护、自动专精/声望转化；这些和现有税费、制作/精炼费、维修费一起压低银币池膨胀。",
            "新版原图已经包含消耗品原材料、精炼、制造、库存、交易行库存、交易和黑市收购；讨论重绘图不再叠加第二套消耗品模块，只把消耗品库存按 80% 使用消耗、20% 继续进入市场/黑市流向来表达主要出口。",
        ],
    }


def load_diagram_xml(capture_path):
    data = json.loads(capture_path.read_text(encoding="utf-8"))
    entries = data if isinstance(data, list) else [data]

    for entry in entries:
        url = str(entry.get("url", ""))
        body_text = entry.get("body")
        if not body_text:
            continue

        try:
            body = json.loads(body_text) if isinstance(body_text, str) else body_text
        except json.JSONDecodeError:
            continue

        content = body.get("content") if isinstance(body, dict) else None
        xml = content.get("xml") if isinstance(content, dict) else None
        if xml and ("/diagram/open/" in url or body.get("success") is True):
            return {
                "url": url,
                "filename": content.get("filename", ""),
                "xml": xml,
            }

    raise ValueError(f"No Machinations diagram XML found in {capture_path}")


def parse_graph(xml_text):
    root = ET.fromstring(xml_text)
    nodes = {}

    for element in root.iter():
        if element.tag not in NODE_TAGS:
            continue

        attrs = element.attrib
        geometry = element.find("mxGeometry")
        if geometry is None:
            continue

        node_id = attrs.get("id")
        label = html.unescape(attrs.get("value", "")).replace("\n", " ").strip() or "(unnamed)"
        nodes[node_id] = {
            "id": node_id,
            "kind": NODE_TAGS[element.tag],
            "label": label,
            "x": round(float(geometry.attrib.get("x", 0)), 2),
            "y": round(float(geometry.attrib.get("y", 0)), 2),
            "w": round(float(geometry.attrib.get("width", 46)), 2),
            "h": round(float(geometry.attrib.get("height", 46)), 2),
            "formula": attrs.get("formula") or attrs.get("formulaValue") or "",
            "activation": attrs.get("activation") or "",
        }

    connection_elements = [element for element in root.iter() if element.tag in CONNECTION_TAGS]
    connection_ids = {element.attrib.get("id") for element in connection_elements if element.attrib.get("id")}
    endpoint_ids = set(nodes) | connection_ids
    edges = []
    for element in connection_elements:
        attrs = element.attrib
        source = attrs.get("source")
        target = attrs.get("target")
        if source not in endpoint_ids or target not in endpoint_ids:
            continue

        edges.append(
            {
                "id": attrs.get("id"),
                "kind": CONNECTION_TAGS[element.tag],
                "from": source,
                "to": target,
                "label": html.unescape(attrs.get("value", "")).replace("\n", " ").strip(),
                "formula": attrs.get("formulaValue") or attrs.get("formula") or "",
                "resource": attrs.get("resource") or "",
            }
        )

    return nodes, edges


def build_payload(capture_path, diagram, nodes, edges, problem_node_ids, problem_edge_ids):
    for edge in edges:
        if edge["id"] in problem_edge_ids:
            problem_node_ids.add(edge["from"])
            problem_node_ids.add(edge["to"])

    original_nodes = list(nodes.values())
    view_box = calculate_view_box(original_nodes)
    original_view = {
        "id": "original",
        "title": "原坐标复原图",
        "description": "严格使用 Machinations XML 原始坐标，用于校验当前抓取数据。",
        "viewBox": view_box,
        "nodes": original_nodes,
        "edges": edges,
        "problemNodeIds": sorted(problem_node_ids),
        "problemEdgeIds": sorted(problem_edge_ids),
        "explanations": [
            "该视图保持原始 x/y/w/h，不做语义重排。",
            "红色高亮保留当前优先检查的节点和连线。",
        ],
    }
    redraw_view = build_albion_redraw_view(original_nodes, edges)

    return {
        "meta": {
            "source": capture_path.name,
            "diagram": diagram.get("filename", ""),
            "url": diagram.get("url", ""),
            "nodeCount": len(nodes),
            "edgeCount": len(edges),
            "xmlChars": len(diagram["xml"]),
            "viewBox": view_box,
        },
        "nodes": original_nodes,
        "edges": edges,
        "problemNodeIds": sorted(problem_node_ids),
        "problemEdgeIds": sorted(problem_edge_ids),
        "views": {
            "original": original_view,
            "redraw": redraw_view,
        },
    }


def render_html(payload):
    payload_js = json.dumps(payload, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")
    capture_snippet = Path(__file__).with_name("browser_capture_snippet.js").read_text(encoding="utf-8")
    capture_snippet_js = json.dumps(capture_snippet, ensure_ascii=True).replace("</", "<\\/")
    return HTML_TEMPLATE.replace("__PAYLOAD__", payload_js).replace("__CAPTURE_SNIPPET__", capture_snippet_js)


HTML_TEMPLATE = r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Albion Machinations &#x539f;&#x5750;&#x6807;&#x590d;&#x539f;&#x56fe;</title>
<style>
:root{--bg:#0e1117;--panel:#151922;--panel2:#1d2430;--text:#e8edf5;--muted:#9aa7b8;--line:#7a8799;--state:#9fa8ba;--accent:#9cc3ff;--bad:#ff7f7a}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:13px/1.45 system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}header{padding:14px 18px;background:#111620;border-bottom:1px solid #293241;position:sticky;top:0;z-index:10}h1{font-size:18px;margin:0 0 6px}.meta{color:var(--muted);display:flex;gap:14px;flex-wrap:wrap}.toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;padding:10px 18px;background:#0f141d;border-bottom:1px solid #293241;position:sticky;top:69px;z-index:9}button,label{border:1px solid #303b4d;background:var(--panel2);color:var(--text);border-radius:7px;padding:6px 9px}button{cursor:pointer}button.active{border-color:var(--accent);background:#23314a}.legend,.explain{margin:10px 18px;background:#111620;border:1px solid #303b4d;border-radius:10px;padding:10px 12px;color:var(--muted)}.legend b,.explain b{color:var(--text)}.explain-head{display:flex;align-items:center;justify-content:space-between;gap:10px}.explain-title{font-weight:700;color:var(--text);margin-bottom:0}.explain-toggle{white-space:nowrap}.explain-body ul{margin:8px 0 0 18px;padding:0}.explain-body li{margin:4px 0}.explain.collapsed .explain-body{display:none}.legend-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:8px 14px;align-items:center}.legend-item{display:flex;align-items:center;gap:8px;min-height:32px}.legend svg{display:inline-block;background:transparent;border:0;border-radius:0;flex:0 0 auto}.legend-note{margin-top:8px;color:var(--muted)}.stage{height:calc(100vh - 330px);min-height:420px;overflow:auto;background:#0b0e14;cursor:grab}.stage.dragging{cursor:grabbing;user-select:none}.stage.stage-fullscreen{position:fixed;inset:0;z-index:1000;height:100vh;min-height:100vh;border:0}.stage:fullscreen{height:100vh;min-height:100vh;background:#0b0e14}.stage.stage-fullscreen .canvas-wrap,.stage:fullscreen .canvas-wrap{padding:24px}.canvas-wrap{width:max-content;min-width:100%;padding:18px}svg{display:block;background:#f8fafc;border:1px solid #2b3444;border-radius:10px}.grid{stroke:#dde3ec;stroke-width:1}.edge.resource{stroke:#46566b;stroke-width:2;fill:none}.edge.state{stroke:#7a668a;stroke-width:1.6;stroke-dasharray:8 7;fill:none}.edge.problem{stroke:var(--bad);stroke-width:3}.edge-arrow{stroke:#f8fafc;stroke-width:4;stroke-linejoin:round;paint-order:stroke;opacity:.95}.edge-arrow.resource{fill:#46566b}.edge-arrow.state{fill:#7a668a}.edge-arrow.problem{fill:#ff7f7a}.edge-label{font-size:13px;fill:#2c3542;paint-order:stroke;stroke:#f8fafc;stroke-width:5px;stroke-linejoin:round}.node-shape{stroke:#1c2533;stroke-width:2;fill:white}.node.Pool .node-shape{fill:#e8f1ff}.node.Converter .node-shape{fill:#fff6dc}.node.Gate .node-shape{fill:#f0e8ff}.node.Register .node-shape{fill:#e9fff1}.node.Source .node-shape{fill:#e8fff9}.node.Drain .node-shape{fill:#ffe9e7}.node.problem .node-shape{stroke:#d7352f;stroke-width:4}.node-label-bg{fill:rgba(255,255,255,.92);stroke:#d8dee8;stroke-width:1}.node-label-main{font-size:14px;font-weight:700;fill:#172033}.node-label-sub{font-size:11px;fill:#526073}.dim .edge,.dim .edge-arrow{opacity:.16}.dim .node{opacity:.35}.dim .edge.problem,.dim .edge-arrow.problem,.dim .node.problem{opacity:1}.no-labels .node-label,.no-edge-labels .edge-label{display:none}.no-state .edge.state,.no-state .edge-arrow.state{display:none}.no-resource .edge.resource,.no-resource .edge-arrow.resource{display:none}.selected .node:not(.focus){opacity:.18}.selected .edge:not(.focus),.selected .edge-group:not(.focus) .edge-arrow{opacity:.08}.selected .focus{opacity:1}.node-hit{fill:transparent;cursor:pointer}.modal-backdrop{position:fixed;inset:0;z-index:2000;background:rgba(3,7,14,.68);display:none;align-items:center;justify-content:center;padding:24px}.modal-backdrop.open{display:flex}.modal{width:min(560px,100%);background:#111620;border:1px solid #303b4d;border-radius:14px;padding:18px 20px;box-shadow:0 18px 60px rgba(0,0,0,.45)}.modal h2{font-size:17px;margin:0 0 10px}.modal ol{margin:8px 0 14px 22px;padding:0;color:var(--muted)}.modal li{margin:6px 0}.modal-actions{display:flex;gap:10px;flex-wrap:wrap;align-items:center}.copy-status{color:var(--muted)}.info{position:fixed;left:18px;bottom:18px;z-index:20;background:rgba(17,22,32,.94);border:1px solid #303b4d;border-radius:10px;padding:10px 12px;color:var(--muted);max-width:460px}.info b{color:var(--text)}
</style>
</head>
<body>
<header><h1>Albion Machinations &#x539f;&#x5750;&#x6807;&#x590d;&#x539f;&#x56fe;</h1><div id="meta" class="meta"></div></header>
<div class="toolbar"><button id="originalViewBtn" class="active">&#x539f;&#x5750;&#x6807;&#x590d;&#x539f;&#x56fe;</button><button id="redrawViewBtn">&#x8ba8;&#x8bba;&#x91cd;&#x7ed8;&#x56fe;</button><button id="fitBtn">&#x9002;&#x914d;&#x5168;&#x56fe;</button><button id="fullscreenBtn">&#x5168;&#x5c4f;&#x67e5;&#x770b;</button><button id="captureHelpBtn">&#x6293;&#x53d6;&#x6570;&#x636e;</button><button id="issueBtn">&#x9ad8;&#x4eae;&#x95ee;&#x9898;</button><button id="labelBtn" class="active">&#x8282;&#x70b9;&#x6807;&#x7b7e;</button><button id="edgeLabelBtn" class="active">&#x8fde;&#x7ebf;&#x6807;&#x7b7e;</button><button id="stateBtn" class="active">&#x72b6;&#x6001;&#x7ebf;</button><button id="resourceBtn" class="active">&#x8d44;&#x6e90;&#x7ebf;</button><label>&#x7f29;&#x653e; <input id="scaleRange" type="range" min="35" max="130" value="70" /></label></div>
<div class="legend"><b>&#x56fe;&#x4f8b;</b><div class="legend-grid"><div class="legend-item"><svg width="34" height="24" viewBox="0 0 34 24"><ellipse cx="17" cy="12" rx="14" ry="9" fill="#e8f1ff" stroke="#1c2533" stroke-width="2"/></svg><span><b>Pool</b>&#xff1a;&#x8d44;&#x6e90;&#x6c60;&#xff0c;&#x5b58;&#x653e;&#x8d44;&#x6e90;&#x6570;&#x91cf;</span></div><div class="legend-item"><svg width="34" height="24" viewBox="0 0 34 24"><polygon points="3,4 24,4 31,12 24,20 3,20" fill="#e8fff9" stroke="#1c2533" stroke-width="2"/></svg><span><b>Source</b>&#xff1a;&#x8d44;&#x6e90;&#x6e90;&#x5934;&#xff0c;&#x751f;&#x6210;&#x8d44;&#x6e90;</span></div><div class="legend-item"><svg width="34" height="24" viewBox="0 0 34 24"><rect x="4" y="4" width="26" height="16" rx="5" fill="#fff6dc" stroke="#1c2533" stroke-width="2"/></svg><span><b>Converter</b>&#xff1a;&#x8f6c;&#x6362;&#x5668;&#xff0c;&#x6d88;&#x8017;&#x8f93;&#x5165;&#x5e76;&#x4ea7;&#x51fa;&#x7ed3;&#x679c;</span></div><div class="legend-item"><svg width="34" height="24" viewBox="0 0 34 24"><polygon points="17,3 31,12 17,21 3,12" fill="#f0e8ff" stroke="#1c2533" stroke-width="2"/></svg><span><b>Gate</b>&#xff1a;&#x95e8;&#xff0c;&#x5206;&#x6d41;&#x3001;&#x6982;&#x7387;&#x6216;&#x6761;&#x4ef6;&#x5224;&#x65ad;</span></div><div class="legend-item"><svg width="34" height="24" viewBox="0 0 34 24"><rect x="5" y="4" width="24" height="16" fill="#e9fff1" stroke="#1c2533" stroke-width="2"/></svg><span><b>Register</b>&#xff1a;&#x5bc4;&#x5b58;&#x5668;&#xff0c;&#x8ba1;&#x7b97;&#x4fe1;&#x53f7;&#x6216;&#x516c;&#x5f0f;</span></div><div class="legend-item"><svg width="34" height="24" viewBox="0 0 34 24"><polygon points="5,4 29,4 24,20 10,20" fill="#ffe9e7" stroke="#1c2533" stroke-width="2"/></svg><span><b>Drain</b>&#xff1a;&#x8d44;&#x6e90;&#x6c47;&#xff0c;&#x6c38;&#x4e45;&#x79fb;&#x9664;&#x8d44;&#x6e90;</span></div><div class="legend-item"><svg width="44" height="24" viewBox="0 0 44 24"><defs><marker id="legendArrow" markerWidth="8" markerHeight="8" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#46566b"/></marker></defs><line x1="4" y1="12" x2="36" y2="12" stroke="#46566b" stroke-width="3" marker-end="url(#legendArrow)"/></svg><span><b>&#x8d44;&#x6e90;&#x6d41;</b>&#xff1a;&#x5b9e;&#x7ebf;&#xff0c;&#x8868;&#x793a;&#x8d44;&#x6e90;&#x79fb;&#x52a8;</span></div><div class="legend-item"><svg width="44" height="24" viewBox="0 0 44 24"><line x1="4" y1="12" x2="38" y2="12" stroke="#7a668a" stroke-width="2" stroke-dasharray="6 4"/></svg><span><b>&#x72b6;&#x6001;&#x7ebf;</b>&#xff1a;&#x865a;&#x7ebf;&#xff0c;&#x8868;&#x793a;&#x5f71;&#x54cd;&#x3001;&#x4fee;&#x6b63;&#x6216;&#x89e6;&#x53d1;</span></div><div class="legend-item"><svg width="44" height="24" viewBox="0 0 44 24"><line x1="4" y1="12" x2="38" y2="12" stroke="#ff7f7a" stroke-width="4"/></svg><span><b>&#x7ea2;&#x8272;</b>&#xff1a;&#x4f18;&#x5148;&#x68c0;&#x67e5;&#x7684;&#x95ee;&#x9898;&#x8282;&#x70b9;&#x6216;&#x8fde;&#x7ebf;</span></div></div><div class="legend-note"><b>&#x5750;&#x6807;&#x89c4;&#x5219;&#xff1a;</b>&#x8282;&#x70b9;&#x4f7f;&#x7528; XML &#x539f;&#x59cb; x/y/w/h&#xff1b;&#x9875;&#x9762;&#x53ea;&#x6539;&#x53d8; SVG viewBox&#x3001;&#x663e;&#x793a;&#x7f29;&#x653e;&#x548c;&#x6eda;&#x52a8;&#x4f4d;&#x7f6e;&#x3002;<b>&#x64cd;&#x4f5c;&#xff1a;</b>&#x5728;&#x7a7a;&#x767d;&#x753b;&#x5e03;&#x6309;&#x4f4f;&#x9f20;&#x6807;&#x5de6;&#x952e;&#x62d6;&#x52a8;&#x53ef;&#x5e73;&#x79fb;&#xff1b;&#x70b9;&#x51fb;&#x8282;&#x70b9;&#x67e5;&#x770b;&#x539f;&#x59cb;&#x6570;&#x636e;&#x3002;</div></div>
<div id="explain" class="explain collapsed"></div>
<div class="stage"><div id="wrap" class="canvas-wrap"><svg id="svg" xmlns="http://www.w3.org/2000/svg"></svg></div></div>
<div id="info" class="info">&#x70b9;&#x51fb;&#x8282;&#x70b9;&#x53ef;&#x67e5;&#x770b;&#x539f;&#x59cb; ID&#x3001;&#x7c7b;&#x578b;&#x3001;&#x6807;&#x7b7e;&#x548c;&#x5750;&#x6807;&#x3002;</div>
<div id="captureModal" class="modal-backdrop" role="dialog" aria-modal="true" aria-labelledby="captureTitle"><div class="modal"><h2 id="captureTitle">&#x6293;&#x53d6; Machinations &#x6700;&#x65b0;&#x6570;&#x636e;</h2><ol><li>&#x5207;&#x6362;&#x5230; Machinations &#x56fe;&#x8868;&#x9875;&#x7b7e;&#x3002;</li><li>&#x6309; F12 &#x6253;&#x5f00;&#x5f00;&#x53d1;&#x8005;&#x5de5;&#x5177;&#xff0c;&#x5207;&#x5230; Console&#x3002;</li><li>&#x70b9;&#x51fb;&#x4e0b;&#x65b9;&#x590d;&#x5236;&#x6309;&#x94ae;&#xff0c;&#x628a;&#x5185;&#x5bb9;&#x7c98;&#x8d34;&#x5230; Console&#x3002;</li><li>&#x6309;&#x56de;&#x8f66;&#xff0c;&#x4e0b;&#x8f7d; machinations-capture.json &#x5230;&#x672c;&#x5730;&#x3002;</li></ol><div class="modal-actions"><button id="copyCaptureSnippetBtn">&#x4e00;&#x952e;&#x590d;&#x5236;&#x6293;&#x53d6;&#x811a;&#x672c;</button><button id="closeCaptureModalBtn">&#x5173;&#x95ed;</button><span id="copyCaptureStatus" class="copy-status"></span></div></div></div>
<script>
const data=__PAYLOAD__;
const captureSnippet=__CAPTURE_SNIPPET__;
let currentViewId='original';
let currentView=data.views[currentViewId];
let nodes=currentView.nodes, edges=currentView.edges;
let nodeMap=new Map(nodes.map(n=>[n.id,n]));
let edgeMap=new Map(edges.map(e=>[e.id,e]));
let problemNodes=new Set(currentView.problemNodeIds||[]), problemEdges=new Set(currentView.problemEdgeIds||[]);
const svg=document.getElementById('svg');
const stage=document.querySelector('.stage');
const wrap=document.getElementById('wrap');
let viewBox=currentView.viewBox;
let selectedNode=null;
let suppressClick=false;
let explainCollapsed=true;
let fallbackFullscreen=false;
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function updateExplain(){const panel=document.getElementById('explain');panel.classList.toggle('collapsed',explainCollapsed);const items=(currentView.explanations||[]).map(x=>`<li>${esc(x)}</li>`).join('');const label=explainCollapsed?'&#x5c55;&#x5f00;&#x8bf4;&#x660e;':'&#x6536;&#x8d77;&#x8bf4;&#x660e;';panel.innerHTML=`<div class="explain-head"><div class="explain-title">${esc(currentView.title)}：${esc(currentView.description||'')}</div><button id="toggleExplainBtn" class="explain-toggle">${label}</button></div><div class="explain-body">${items?`<ul>${items}</ul>`:''}</div>`;document.getElementById('toggleExplainBtn').addEventListener('click',()=>{explainCollapsed=!explainCollapsed;updateExplain()});}
function updateViewState(){currentView=data.views[currentViewId];nodes=currentView.nodes;edges=currentView.edges;nodeMap=new Map(nodes.map(n=>[n.id,n]));edgeMap=new Map(edges.map(e=>[e.id,e]));problemNodes=new Set(currentView.problemNodeIds||[]);problemEdges=new Set(currentView.problemEdgeIds||[]);viewBox=currentView.viewBox;document.getElementById('meta').innerHTML=`<span>&#x6765;&#x6e90;&#xff1a;${data.meta.source}</span><span>&#x56fe;&#x540d;&#xff1a;${data.meta.diagram}</span><span>&#x5f53;&#x524d;&#x89c6;&#x56fe;&#xff1a;${esc(currentView.title)}</span><span>${nodes.length} &#x4e2a;&#x8282;&#x70b9;</span><span>${edges.length} &#x6761;&#x53ef;&#x7ed8;&#x5236;&#x8fde;&#x7ebf;</span><span>ViewBox&#xff1a;${viewBox.join(', ')}</span>`;document.getElementById('originalViewBtn').classList.toggle('active',currentViewId==='original');document.getElementById('redrawViewBtn').classList.toggle('active',currentViewId==='redraw');updateExplain();}
function center(n){return{x:n.x+n.w/2,y:n.y+n.h/2}}
function edgeAnchorNode(edgeId){const e=edgeMap.get(edgeId);if(!e)return null;const a=endpointRef(e.from),b=endpointRef(e.to);if(!a||!b)return null;const ac=center(a),bc=center(b);return{id:`anchor-${edgeId}`,kind:'Anchor',label:'',x:(ac.x+bc.x)/2-1,y:(ac.y+bc.y)/2-1,w:2,h:2}}
function endpointRef(id){return nodeMap.get(id)||edgeAnchorNode(id)}
function edgeEndpoint(from,to,isTarget){const a=center(from),b=center(to);const dx=b.x-a.x,dy=b.y-a.y;const len=Math.max(1,Math.hypot(dx,dy));const ux=dx/len,uy=dy/len;const n=isTarget?to:from;const pad=isTarget?13:8;const r=Math.max(n.w,n.h)/2+pad;const c=isTarget?b:a;return{x:c.x+(isTarget?-ux:ux)*r,y:c.y+(isTarget?-uy:uy)*r}}
function edgePath(a,b,i){const ac=edgeEndpoint(a,b,false),bc=edgeEndpoint(a,b,true);const dx=bc.x-ac.x,dy=bc.y-ac.y;const len=Math.max(1,Math.hypot(dx,dy));const nx=-dy/len,ny=dx/len;const bend=((i%5)-2)*14;const cx=(ac.x+bc.x)/2+nx*bend,cy=(ac.y+bc.y)/2+ny*bend;return`M ${ac.x} ${ac.y} Q ${cx} ${cy} ${bc.x} ${bc.y}`}
function edgeLabelPos(a,b,i){const ac=center(a),bc=center(b);const dx=bc.x-ac.x,dy=bc.y-ac.y;const len=Math.max(1,Math.hypot(dx,dy));const nx=-dy/len,ny=dx/len;const bend=((i%7)-3)*22;const tx=dx/len,ty=dy/len;return{x:(ac.x+bc.x)/2+nx*bend+tx*18,y:(ac.y+bc.y)/2+ny*bend+ty*18-10}}
function edgeMidArrow(a,b,i){const ac=edgeEndpoint(a,b,false),bc=edgeEndpoint(a,b,true);const dx=bc.x-ac.x,dy=bc.y-ac.y;const len=Math.max(1,Math.hypot(dx,dy));const nx=-dy/len,ny=dx/len;const bend=((i%5)-2)*14;return{x:(ac.x+bc.x)/2+nx*bend*.52,y:(ac.y+bc.y)/2+ny*bend*.52,angle:Math.atan2(dy,dx)*180/Math.PI}}
function edgeDisplayLabel(e){return[e.label,e.formula].filter(Boolean).join(' / ')}
function shape(n){const x=n.x,y=n.y,w=n.w,h=n.h,cx=x+w/2,cy=y+h/2;if(n.kind==='Pool')return`<ellipse class="node-shape" cx="${cx}" cy="${cy}" rx="${w/2}" ry="${h/2}"/>`;if(n.kind==='Gate')return`<polygon class="node-shape" points="${cx},${y} ${x+w},${cy} ${cx},${y+h} ${x},${cy}"/>`;if(n.kind==='Drain')return`<polygon class="node-shape" points="${x+5},${y} ${x+w-5},${y} ${x+w-14},${y+h} ${x+14},${y+h}"/>`;if(n.kind==='Source')return`<polygon class="node-shape" points="${x},${y} ${x+w-11},${y} ${x+w},${cy} ${x+w-11},${y+h} ${x},${y+h}"/>`;const rx=n.kind==='Converter'?8:0;return`<rect class="node-shape" x="${x}" y="${y}" width="${w}" height="${h}" rx="${rx}"/>`}
function labelBox(n){const label=esc(n.label);const sub=esc(`${n.id} / ${n.kind}${n.activation?' / \u81ea\u52a8':''}`);const width=Math.max(92,Math.min(190,label.length*12+22));const x=n.x+n.w/2-width/2;const y=n.y+n.h+7;return`<g class="node-label"><rect class="node-label-bg" x="${x}" y="${y}" width="${width}" height="36" rx="6"/><text class="node-label-main" x="${x+width/2}" y="${y+15}" text-anchor="middle">${label.slice(0,18)}</text><text class="node-label-sub" x="${x+width/2}" y="${y+30}" text-anchor="middle">${sub}</text></g>`}
function render(){updateViewState();svg.setAttribute('viewBox',viewBox.join(' '));svg.innerHTML=`<defs><marker id="arrow-resource" markerWidth="16" markerHeight="16" refX="13" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,10 L14,5 z" fill="#46566b"/></marker><marker id="arrow-state" markerWidth="16" markerHeight="16" refX="13" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,10 L14,5 z" fill="#7a668a"/></marker><marker id="arrow-problem" markerWidth="16" markerHeight="16" refX="13" refY="5" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L0,10 L14,5 z" fill="#ff7f7a"/></marker><pattern id="grid" width="100" height="100" patternUnits="userSpaceOnUse"><path class="grid" d="M100 0H0V100" fill="none"/></pattern></defs><rect x="${viewBox[0]}" y="${viewBox[1]}" width="${viewBox[2]}" height="${viewBox[3]}" fill="url(#grid)"/>`;const edgeCounts=new Map();for(const e of edges){const a=endpointRef(e.from),b=endpointRef(e.to);if(!a||!b)continue;const key=[e.from,e.to].sort().join('-');const idx=edgeCounts.get(key)||0;edgeCounts.set(key,idx+1);const cls=`edge ${e.kind} ${problemEdges.has(e.id)?'problem':''}`;const marker=problemEdges.has(e.id)?'arrow-problem':(e.kind==='state'?'arrow-state':'arrow-resource');const arrowCls=problemEdges.has(e.id)?'problem':e.kind;const path=edgePath(a,b,idx);const label=edgeDisplayLabel(e);const pos=edgeLabelPos(a,b,idx);const p=edgeMidArrow(a,b,idx);svg.insertAdjacentHTML('beforeend',`<g class="edge-group" data-edge="${esc(e.id)}" data-from="${esc(e.from)}" data-to="${esc(e.to)}"><path class="${cls}" d="${path}" marker-end="url(#${marker})"/><polygon class="edge-arrow ${arrowCls}" points="-7,-5 8,0 -7,5" transform="translate(${p.x} ${p.y}) rotate(${p.angle})"/><text class="edge-label" x="${pos.x}" y="${pos.y}">${esc(label)}</text></g>`)}for(const n of nodes){const cls=`node ${n.kind} ${problemNodes.has(n.id)?'problem':''}`;svg.insertAdjacentHTML('beforeend',`<g class="${cls}" data-node="${esc(n.id)}">${shape(n)}${labelBox(n)}<rect class="node-hit" x="${n.x-8}" y="${n.y-8}" width="${n.w+16}" height="${n.h+58}"/></g>`)}svg.querySelectorAll('.node').forEach(g=>g.addEventListener('click',ev=>{ev.stopPropagation();if(suppressClick){suppressClick=false;return}selectNode(g.getAttribute('data-node'))}));svg.addEventListener('click',()=>{if(suppressClick){suppressClick=false;return}selectNode(null)});}
function selectNode(id){selectedNode=id;svg.classList.toggle('selected',!!id);svg.querySelectorAll('.focus').forEach(e=>e.classList.remove('focus'));if(!id){document.getElementById('info').innerHTML='&#x70b9;&#x51fb;&#x8282;&#x70b9;&#x53ef;&#x67e5;&#x770b;&#x539f;&#x59cb; ID&#x3001;&#x7c7b;&#x578b;&#x3001;&#x6807;&#x7b7e;&#x548c;&#x5750;&#x6807;&#x3002;';return}const n=nodeMap.get(id);svg.querySelectorAll(`[data-node="${CSS.escape(id)}"]`).forEach(e=>e.classList.add('focus'));svg.querySelectorAll(`[data-from="${CSS.escape(id)}"],[data-to="${CSS.escape(id)}"]`).forEach(e=>e.classList.add('focus'));document.getElementById('info').innerHTML=`<b>${esc(n.label)}</b><br/>ID&#xff1a;${esc(n.id)} / &#x7c7b;&#x578b;&#xff1a;${esc(n.kind)}${n.activation?' / \u81ea\u52a8':''}<br/>&#x539f;&#x59cb; x/y/w/h&#xff1a;${n.x}, ${n.y}, ${n.w}, ${n.h}${n.formula?`<br/>&#x516c;&#x5f0f;&#xff1a;${esc(n.formula)}`:''}`}
function setScale(v){const baseW=viewBox[2],baseH=viewBox[3];wrap.style.width=`${Math.round(baseW*v/100)+40}px`;svg.style.width=`${Math.round(baseW*v/100)}px`;svg.style.height=`${Math.round(baseH*v/100)}px`}
let dragState=null;
stage.addEventListener('pointerdown',ev=>{if(ev.button!==0)return;if(ev.target.closest('button,label,input'))return;dragState={x:ev.clientX,y:ev.clientY,left:stage.scrollLeft,top:stage.scrollTop,moved:false};stage.classList.add('dragging');stage.setPointerCapture(ev.pointerId)});
stage.addEventListener('pointermove',ev=>{if(!dragState)return;const dx=ev.clientX-dragState.x,dy=ev.clientY-dragState.y;if(Math.abs(dx)+Math.abs(dy)>3)dragState.moved=true;stage.scrollLeft=dragState.left-dx;stage.scrollTop=dragState.top-dy});
function endDrag(ev){if(!dragState)return;if(dragState.moved){suppressClick=true;setTimeout(()=>{suppressClick=false},0)}dragState=null;stage.classList.remove('dragging');try{stage.releasePointerCapture(ev.pointerId)}catch(_){}}
stage.addEventListener('pointerup',endDrag);
stage.addEventListener('pointercancel',endDrag);
document.getElementById('scaleRange').addEventListener('input',e=>setScale(Number(e.target.value)));
document.getElementById('fitBtn').addEventListener('click',()=>{document.getElementById('scaleRange').value=70;setScale(70);document.querySelector('.stage').scrollTo(0,0)});
document.getElementById('issueBtn').addEventListener('click',e=>{e.currentTarget.classList.toggle('active');svg.classList.toggle('dim')});
function isStageFullscreen(){return document.fullscreenElement===stage||fallbackFullscreen}
function syncFullscreenButton(){const on=isStageFullscreen();stage.classList.toggle('stage-fullscreen',on);const btn=document.getElementById('fullscreenBtn');btn.classList.toggle('active',on);btn.innerHTML=on?'&#x9000;&#x51fa;&#x5168;&#x5c4f;':'&#x5168;&#x5c4f;&#x67e5;&#x770b;'}
async function toggleStageFullscreen(){if(isStageFullscreen()){if(document.fullscreenElement)await document.exitFullscreen();fallbackFullscreen=false;syncFullscreenButton();return}if(stage.requestFullscreen){await stage.requestFullscreen()}else{fallbackFullscreen=true;syncFullscreenButton()}}
document.getElementById('fullscreenBtn').addEventListener('click',()=>toggleStageFullscreen().catch(()=>{fallbackFullscreen=!fallbackFullscreen;syncFullscreenButton()}));
document.addEventListener('fullscreenchange',()=>{if(document.fullscreenElement!==stage)fallbackFullscreen=false;syncFullscreenButton()});
function setCaptureModal(open){document.getElementById('captureModal').classList.toggle('open',open);document.getElementById('copyCaptureStatus').textContent=''}
function copyTextFallback(text){const el=document.createElement('textarea');el.value=text;el.setAttribute('readonly','');el.style.position='fixed';el.style.left='-9999px';document.body.appendChild(el);el.select();document.execCommand('copy');el.remove()}
async function copyCaptureSnippet(){if(navigator.clipboard&&navigator.clipboard.writeText){await navigator.clipboard.writeText(captureSnippet)}else{copyTextFallback(captureSnippet)}document.getElementById('copyCaptureStatus').textContent='\u5df2\u590d\u5236'}
document.getElementById('captureHelpBtn').addEventListener('click',()=>setCaptureModal(true));
document.getElementById('closeCaptureModalBtn').addEventListener('click',()=>setCaptureModal(false));
document.getElementById('captureModal').addEventListener('click',ev=>{if(ev.target.id==='captureModal')setCaptureModal(false)});
document.getElementById('copyCaptureSnippetBtn').addEventListener('click',()=>copyCaptureSnippet().catch(()=>{copyTextFallback(captureSnippet);document.getElementById('copyCaptureStatus').textContent='\u5df2\u590d\u5236'}));
document.getElementById('originalViewBtn').addEventListener('click',()=>switchView('original'));
document.getElementById('redrawViewBtn').addEventListener('click',()=>switchView('redraw'));
function switchView(id){if(currentViewId===id)return;currentViewId=id;if(currentViewId==='redraw')explainCollapsed=true;selectNode(null);render();setScale(Number(document.getElementById('scaleRange').value));stage.scrollTo(0,0);}
for(const [id,cls] of [['labelBtn','no-labels'],['edgeLabelBtn','no-edge-labels'],['stateBtn','no-state'],['resourceBtn','no-resource']]){document.getElementById(id).addEventListener('click',e=>{e.currentTarget.classList.toggle('active');svg.classList.toggle(cls)})}
render();setScale(70);
</script>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description="Generate a raw-coordinate Machinations HTML preview.")
    parser.add_argument("--capture", type=Path, default=Path("artifacts/machinations/machinations-capture.json"))
    parser.add_argument("--output", type=Path, default=Path("artifacts/machinations/albion-machinations-raw-coordinate.html"))
    args = parser.parse_args()

    diagram = load_diagram_xml(args.capture)
    nodes, edges = parse_graph(diagram["xml"])
    payload = build_payload(
        args.capture,
        diagram,
        nodes,
        edges,
        set(DEFAULT_PROBLEM_NODE_IDS),
        set(DEFAULT_PROBLEM_EDGE_IDS),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_html(payload), encoding="utf-8")

    print(f"Generated {args.output}")
    print(f"Nodes: {len(nodes)}")
    print(f"Drawable edges: {len(edges)}")
    print(f"Diagram: {payload['meta']['diagram']}")


if __name__ == "__main__":
    main()
