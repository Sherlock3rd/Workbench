import unittest
import sys
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import update_machinations_preview as preview


class MachinationsPreviewPayloadTest(unittest.TestCase):
    def test_payload_contains_original_and_albion_redraw_views(self):
        capture_path = Path("artifacts/machinations/machinations-capture.json")
        diagram = preview.load_diagram_xml(capture_path)
        nodes, edges = preview.parse_graph(diagram["xml"])

        payload = preview.build_payload(
            capture_path,
            diagram,
            nodes,
            edges,
            set(preview.DEFAULT_PROBLEM_NODE_IDS),
            set(preview.DEFAULT_PROBLEM_EDGE_IDS),
        )

        self.assertIn("views", payload)
        self.assertEqual("original", payload["views"]["original"]["id"])
        self.assertEqual("redraw", payload["views"]["redraw"]["id"])

        original_nodes = payload["views"]["original"]["nodes"]
        redraw_nodes = payload["views"]["redraw"]["nodes"]
        original_by_id = {node["id"]: node for node in original_nodes}
        redraw_by_id = {node["id"]: node for node in redraw_nodes}
        redraw_by_label = {node["label"]: node for node in redraw_nodes}
        redraw_labels = set(redraw_by_label)
        self.assertIn("交易行成交出库", redraw_labels)
        self.assertIn("玩家装备持有/使用", redraw_labels)
        self.assertIn("装备交易行库存", redraw_labels)
        self.assertIn("公会仓库", redraw_labels)
        self.assertIn("公会管理者", redraw_labels)
        self.assertIn("低价倒卖库存", redraw_labels)
        self.assertIn("玩家买单/购买需求", redraw_labels)
        self.assertIn("玩家市场银币池", redraw_labels)
        self.assertIn("快速旅行/传送费", redraw_labels)
        self.assertIn("岛屿/建筑维护", redraw_labels)
        self.assertIn("自动专精/声望转化", redraw_labels)
        self.assertIn("消耗品库存", redraw_labels)
        self.assertIn("消耗品流向", redraw_labels)
        self.assertIn("消耗品交易行库存", redraw_labels)
        self.assertIn("消耗品交易", redraw_labels)
        self.assertIn("消耗品使用消耗", redraw_labels)
        self.assertNotIn("交易行成交", redraw_labels)
        self.assertNotIn("装备持有/使用", redraw_labels)
        self.assertNotIn("商人套利", redraw_labels)
        self.assertNotIn("金币交易所", redraw_labels)
        self.assertNotIn("金币换银币统计", redraw_labels)
        self.assertEqual("Gate", redraw_by_label["交易行成交出库"]["kind"])
        self.assertEqual("Register", redraw_by_label["玩家买单/购买需求"]["kind"])
        self.assertEqual("Drain", redraw_by_label["消耗品使用消耗"]["kind"])
        self.assertFalse(any(node["id"].startswith("redraw_gold_") for node in redraw_nodes))

        self.assertEqual(len(original_nodes) + len(preview.REDRAW_ADDED_NODE_IDS), len(redraw_nodes))
        self.assertEqual(set(original_by_id) | preview.REDRAW_ADDED_NODE_IDS, set(redraw_by_id))
        for node_id, original_node in original_by_id.items():
            redraw_node = redraw_by_id[node_id]
            self.assertEqual((original_node["x"], original_node["y"], original_node["w"], original_node["h"]), (redraw_node["x"], redraw_node["y"], redraw_node["w"], redraw_node["h"]))
            if node_id not in preview.REDRAW_PROBLEM_NODE_IDS:
                self.assertEqual(original_node["label"], redraw_node["label"])
                self.assertEqual(original_node["kind"], redraw_node["kind"])

        explanation = "\n".join(payload["views"]["redraw"]["explanations"])
        self.assertIn("只局部修改", explanation)
        self.assertIn("未列为问题的节点保持原坐标和原布局", explanation)

        redraw_ids = {node["id"] for node in payload["views"]["redraw"]["nodes"]}
        redraw_edge_ids = {edge["id"] for edge in payload["views"]["redraw"]["edges"]}
        for edge in payload["views"]["redraw"]["edges"]:
            self.assertIn(edge["from"], redraw_ids | redraw_edge_ids)
            self.assertIn(edge["to"], redraw_ids | redraw_edge_ids)

        redraw_edges = {edge["id"]: edge for edge in payload["views"]["redraw"]["edges"]}
        self.assertEqual(redraw_by_label["装备交易行库存"]["id"], redraw_edges["1160"]["from"])
        self.assertEqual(redraw_by_label["交易行成交出库"]["id"], redraw_edges["1160"]["to"])
        self.assertEqual(redraw_by_label["交易行成交出库"]["id"], redraw_edges["2702"]["from"])
        self.assertEqual(redraw_by_label["玩家装备持有/使用"]["id"], redraw_edges["2702"]["to"])
        self.assertEqual(redraw_edges["2702"]["label"], "买家获得装备")
        self.assertNotIn("1162", redraw_edges)
        self.assertNotIn("1186", redraw_edges)
        forbidden_silver_edges = [
            edge
            for edge in redraw_edges.values()
            if edge["from"] == redraw_by_label["交易行成交出库"]["id"] and edge["to"] == redraw_by_label["玩家市场银币池"]["id"]
        ]
        self.assertEqual([], forbidden_silver_edges)
        forbidden_arbitrage_silver_edges = [
            edge
            for edge in redraw_edges.values()
            if edge["from"] == redraw_by_label["低价倒卖库存"]["id"] and edge["to"] == redraw_by_label["玩家市场银币池"]["id"]
        ]
        self.assertEqual([], forbidden_arbitrage_silver_edges)
        original_edges = {edge["id"]: edge for edge in payload["views"]["original"]["edges"]}
        for edge_id, original_edge in original_edges.items():
            if edge_id not in preview.REDRAW_PROBLEM_EDGE_IDS and edge_id not in preview.REDRAW_REMOVED_EDGE_IDS:
                self.assertEqual(original_edge, redraw_edges[edge_id])
        self.assertTrue(preview.REDRAW_ADDED_EDGE_IDS.issubset(set(redraw_edges)))

        self.assertEqual(redraw_edges["1170"]["from"], redraw_by_label["玩家市场银币池"]["id"])
        self.assertEqual(redraw_edges["1170"]["to"], redraw_by_label["T4订单创建费+成交税"]["id"])
        self.assertEqual(redraw_edges["1170"]["formula"], "300")
        self.assertEqual(redraw_edges["1171"]["from"], redraw_by_label["玩家市场银币池"]["id"])
        self.assertEqual(redraw_edges["1171"]["to"], redraw_by_label["T6订单创建费+成交税"]["id"])
        self.assertEqual(redraw_edges["1171"]["formula"], "500")
        self.assertFalse(any(edge["id"].startswith("redraw_gold_") for edge in redraw_edges.values()))
        self.assertEqual(redraw_edges["redraw_market_buy_demand_to_match"]["from"], redraw_by_label["玩家买单/购买需求"]["id"])
        self.assertEqual(redraw_edges["redraw_market_buy_demand_to_match"]["to"], redraw_by_label["交易行成交出库"]["id"])
        self.assertEqual(redraw_edges["redraw_market_buy_demand_to_match"]["kind"], "state")
        self.assertEqual(redraw_edges["redraw_silver_to_market_buy_demand"]["from"], redraw_by_label["玩家市场银币池"]["id"])
        self.assertEqual(redraw_edges["redraw_silver_to_market_buy_demand"]["to"], redraw_by_label["玩家买单/购买需求"]["id"])
        self.assertEqual(redraw_edges["redraw_silver_to_market_buy_demand"]["kind"], "state")
        self.assertEqual(redraw_edges["redraw_silver_fast_travel"]["to"], redraw_by_label["快速旅行/传送费"]["id"])
        self.assertEqual(redraw_edges["redraw_silver_island"]["to"], redraw_by_label["岛屿/建筑维护"]["id"])
        self.assertEqual(redraw_edges["redraw_silver_respec"]["to"], redraw_by_label["自动专精/声望转化"]["id"])
        self.assertEqual(redraw_edges["5485"]["from"], redraw_by_label["消耗品库存"]["id"])
        self.assertEqual(redraw_edges["5485"]["to"], redraw_by_label["消耗品流向"]["id"])
        self.assertEqual(redraw_edges["5485"]["formula"], "20%")
        self.assertEqual(redraw_edges["redraw_consumable_use_drain"]["from"], redraw_by_label["消耗品库存"]["id"])
        self.assertEqual(redraw_edges["redraw_consumable_use_drain"]["to"], redraw_by_label["消耗品使用消耗"]["id"])
        self.assertEqual(redraw_edges["redraw_consumable_use_drain"]["formula"], "80%")
        self.assertEqual(redraw_edges["redraw_pvp_consumable_demand"]["from"], redraw_by_label["PvP 战斗使用"]["id"])
        self.assertEqual(redraw_edges["redraw_pve_consumable_demand"]["from"], redraw_by_label["PvE 刷取玩家"]["id"])
        self.assertEqual(redraw_edges["redraw_gather_consumable_demand"]["from"], redraw_by_label["采集者"]["id"])
        self.assertEqual(redraw_edges["redraw_pvp_consumable_demand"]["to"], redraw_by_label["消耗品使用消耗"]["id"])
        self.assertEqual(redraw_edges["redraw_pve_consumable_demand"]["to"], redraw_by_label["消耗品使用消耗"]["id"])
        self.assertEqual(redraw_edges["redraw_gather_consumable_demand"]["to"], redraw_by_label["消耗品使用消耗"]["id"])
        self.assertEqual(original_edges["1184"], redraw_edges["1184"])
        self.assertIn("2719", redraw_edges)
        self.assertEqual(redraw_edges["2719"]["from"], "2718")
        self.assertEqual(redraw_edges["2719"]["to"], "1160")
        self.assertEqual(redraw_edges["2719"]["kind"], "state")

    def test_redraw_explanation_is_collapsible_and_collapsed_by_default(self):
        payload = {
            "meta": {"source": "test.json", "diagram": "Test", "nodeCount": 0, "edgeCount": 0, "xmlChars": 0},
            "views": {
                "original": {
                    "id": "original",
                    "title": "原坐标复原图",
                    "description": "原图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
                "redraw": {
                    "id": "redraw",
                    "title": "讨论重绘图",
                    "description": "讨论图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": ["解释"],
                },
            },
        }

        html = preview.render_html(payload)

        self.assertIn('id="explain"', html)
        self.assertIn("class=\"explain collapsed\"", html)
        self.assertIn("toggleExplainBtn", html)
        self.assertIn("currentViewId==='redraw'", html)

    def test_edges_use_visible_direction_arrows(self):
        payload = {
            "meta": {"source": "test.json", "diagram": "Test", "nodeCount": 0, "edgeCount": 0, "xmlChars": 0},
            "views": {
                "original": {
                    "id": "original",
                    "title": "原坐标复原图",
                    "description": "原图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
                "redraw": {
                    "id": "redraw",
                    "title": "讨论重绘图",
                    "description": "讨论图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
            },
        }

        html = preview.render_html(payload)

        self.assertIn('id="arrow-resource"', html)
        self.assertIn('id="arrow-state"', html)
        self.assertIn("const marker=", html)
        self.assertIn("e.kind==='state'?'arrow-state':'arrow-resource'", html)
        self.assertIn("marker-end=\"url(#${marker})\"", html)
        self.assertIn("edgeEndpoint", html)
        self.assertIn("edgeMidArrow", html)
        self.assertIn("endpointRef", html)
        self.assertIn("edgeAnchorNode", html)
        self.assertIn("class=\"edge-arrow ${arrowCls}\"", html)
        self.assertIn("transform=\"translate(${p.x} ${p.y}) rotate(${p.angle})\"", html)
        self.assertNotIn('fill="currentColor"', html)

    def test_edge_labels_do_not_render_resource_color_identifiers(self):
        payload = {
            "meta": {"source": "test.json", "diagram": "Test", "nodeCount": 2, "edgeCount": 1, "xmlChars": 0},
            "views": {
                "original": {
                    "id": "original",
                    "title": "原坐标复原图",
                    "description": "原图",
                    "viewBox": [0, 0, 200, 100],
                    "nodes": [
                        {"id": "a", "kind": "Pool", "label": "A", "x": 10, "y": 10, "w": 40, "h": 40, "formula": "", "activation": ""},
                        {"id": "b", "kind": "Pool", "label": "B", "x": 120, "y": 10, "w": 40, "h": 40, "formula": "", "activation": ""},
                    ],
                    "edges": [
                        {
                            "id": "e",
                            "kind": "resource",
                            "from": "a",
                            "to": "b",
                            "label": "流向",
                            "formula": "1",
                            "resource": "85fb4169-4608-4137-a8ef-e32bf0027196",
                        }
                    ],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
                "redraw": {
                    "id": "redraw",
                    "title": "讨论重绘图",
                    "description": "讨论图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
            },
        }

        html = preview.render_html(payload)

        self.assertIn("function edgeDisplayLabel(e)", html)
        self.assertIn("[e.label,e.formula].filter(Boolean).join(' / ')", html)
        self.assertNotIn("[e.label,e.formula,e.resource]", html)
        self.assertIn('"resource":"85fb4169-4608-4137-a8ef-e32bf0027196"', html)

    def test_canvas_stage_supports_fullscreen_mode(self):
        payload = {
            "meta": {"source": "test.json", "diagram": "Test", "nodeCount": 0, "edgeCount": 0, "xmlChars": 0},
            "views": {
                "original": {
                    "id": "original",
                    "title": "原坐标复原图",
                    "description": "原图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
                "redraw": {
                    "id": "redraw",
                    "title": "讨论重绘图",
                    "description": "讨论图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
            },
        }

        html = preview.render_html(payload)

        self.assertIn('id="fullscreenBtn"', html)
        self.assertIn("requestFullscreen", html)
        self.assertIn("exitFullscreen", html)
        self.assertIn("fullscreenchange", html)
        self.assertIn("stage-fullscreen", html)
        self.assertIn("isStageFullscreen", html)

    def test_capture_help_modal_copies_browser_snippet_without_displaying_source(self):
        payload = {
            "meta": {"source": "test.json", "diagram": "Test", "nodeCount": 0, "edgeCount": 0, "xmlChars": 0},
            "views": {
                "original": {
                    "id": "original",
                    "title": "原坐标复原图",
                    "description": "原图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
                "redraw": {
                    "id": "redraw",
                    "title": "讨论重绘图",
                    "description": "讨论图",
                    "viewBox": [0, 0, 100, 100],
                    "nodes": [],
                    "edges": [],
                    "problemNodeIds": [],
                    "problemEdgeIds": [],
                    "explanations": [],
                },
            },
        }

        html = preview.render_html(payload)

        self.assertIn('id="captureHelpBtn"', html)
        self.assertIn('id="captureModal"', html)
        self.assertIn('id="copyCaptureSnippetBtn"', html)
        self.assertIn("captureSnippet", html)
        self.assertIn("navigator.clipboard.writeText", html)
        self.assertIn("copyTextFallback", html)
        self.assertIn("machinations-capture.json", html)
        self.assertIn("Capture failed: diagram XML was not found", html)
        self.assertNotIn("<pre", html)
        self.assertNotIn("<textarea", html)

    def test_redraw_uses_numeric_values_not_placeholder_formulas(self):
        capture_path = Path("artifacts/machinations/machinations-capture.json")
        diagram = preview.load_diagram_xml(capture_path)
        nodes, edges = preview.parse_graph(diagram["xml"])
        view = preview.build_albion_redraw_view(list(nodes.values()), edges)
        forbidden_fragments = [
            "black_price",
            "black_qty",
            "trash_share",
            "destroy_rate",
            "crafting_fee",
            "掉落率",
            "收购均价",
        ]

        for edge in view["edges"]:
            for forbidden in forbidden_fragments:
                self.assertNotIn(forbidden, edge.get("formula", ""))


if __name__ == "__main__":
    unittest.main()
