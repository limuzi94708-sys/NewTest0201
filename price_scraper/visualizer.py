"""
数据可视化模块
生成图表数据供前端展示
"""

import json
from typing import List, Dict, Any
from architecture import ProductItem, AnalysisResult, CompareResult


class Visualizer:
    """可视化数据生成器"""

    @staticmethod
    def generate_price_comparison_chart(results: List[AnalysisResult]) -> Dict[str, Any]:
        """生成价格对比图表数据"""
        labels = []
        prices = []
        colors = []
        recommendations = []

        color_map = {
            "强烈推荐": "#52c41a",
            "推荐": "#1890ff",
            "一般": "#faad14",
            "不推荐": "#ff4d4f"
        }

        for r in results[:15]:  # 最多显示15个
            labels.append(r.product.name[:20] + "..." if len(r.product.name) > 20 else r.product.name)
            prices.append(r.product.price)
            colors.append(color_map.get(r.recommendation, "#1890ff"))
            recommendations.append(r.recommendation)

        return {
            "type": "bar",
            "title": "商品价格对比",
            "labels": labels,
            "datasets": [{
                "label": "价格(元)",
                "data": prices,
                "backgroundColor": colors
            }],
            "recommendations": recommendations
        }

    @staticmethod
    def generate_sales_ranking_chart(results: List[AnalysisResult]) -> Dict[str, Any]:
        """生成销量排行图表数据"""
        sorted_by_sales = sorted(results, key=lambda x: x.product.sales, reverse=True)[:15]

        labels = [r.product.name[:15] + "..." if len(r.product.name) > 15
                  else r.product.name for r in sorted_by_sales]
        sales = [r.product.sales for r in sorted_by_sales]
        platforms = [r.product.platform for r in sorted_by_sales]

        return {
            "type": "horizontalBar",
            "title": "销量排行榜",
            "labels": labels,
            "datasets": [{
                "label": "销量",
                "data": sales,
                "backgroundColor": "#1890ff"
            }],
            "platforms": platforms
        }

    @staticmethod
    def generate_platform_comparison_chart(results: List[AnalysisResult]) -> Dict[str, Any]:
        """生成平台对比图表"""
        # 按平台聚合
        platform_data: Dict[str, Dict[str, float]] = {}
        for r in results:
            p = r.product.platform
            if p not in platform_data:
                platform_data[p] = {'total': 0, 'count': 0, 'avg_score': 0, 'total_sales': 0}

            platform_data[p]['total'] += r.product.price
            platform_data[p]['count'] += 1
            platform_data[p]['avg_score'] += r.product.shop_score
            platform_data[p]['total_sales'] += r.product.sales

        platforms = list(platform_data.keys())
        avg_prices = [round(d['total'] / d['count'], 2) if d['count'] > 0 else 0
                      for d in platform_data.values()]
        avg_scores = [round(d['avg_score'] / d['count'], 1) if d['count'] > 0 else 0
                      for d in platform_data.values()]
        total_sales = [d['total_sales'] for d in platform_data.values()]

        return {
            "type": "mixed",
            "title": "各平台综合对比",
            "labels": platforms,
            "datasets": [
                {
                    "label": "平均价格(元)",
                    "data": avg_prices,
                    "type": "bar",
                    "backgroundColor": "#1890ff"
                },
                {
                    "label": "平均评分",
                    "data": avg_scores,
                    "type": "line",
                    "borderColor": "#52c41a",
                    "yAxisID": "y1"
                }
            ],
            "yAxes": {
                "y": {"label": "价格(元)", "position": "left"},
                "y1": {"label": "评分", "position": "right", "min": 0, "max": 5}
            }
        }

    @staticmethod
    def generate_value_radar_chart(results: List[AnalysisResult]) -> Dict[str, Any]:
        """生成性价比雷达图数据"""
        # 取性价比最高的10个
        top_value = sorted(results, key=lambda x: x.value_score, reverse=True)[:10]

        labels = ["价格优势", "销量表现", "评分高低", "性价比", "推荐指数"]

        datasets = []
        colors = ["#1890ff", "#52c41a", "#faad14", "#722ed1", "#eb2f96"]

        for i, r in enumerate(top_value[:5]):
            # 计算各项归一化得分
            data = [
                100 - (r.price_rank / len(results) * 100),  # 价格排名得分
                100 - (r.sales_rank / len(results) * 100),  # 销量排名得分
                100 - (r.score_rank / len(results) * 100),   # 评分排名得分
                r.value_score,                               # 性价比得分
                r.value_score if r.recommendation in ["强烈推荐", "推荐"] else r.value_score * 0.5
            ]

            datasets.append({
                "label": r.product.name[:12] + "...",
                "data": data,
                "backgroundColor": f"rgba({', '.join([str(random.randint(0,255)) for _ in range(3)])}, 0.2)"
            })

        return {
            "type": "radar",
            "title": "Top5商品多维度对比",
            "labels": labels,
            "datasets": datasets
        }

    @staticmethod
    def generate_price_trend_chart(trend_data: Dict) -> Dict[str, Any]:
        """生成价格趋势图表"""
        platforms = list(trend_data.keys())
        mins = [trend_data[p]['min'] for p in platforms]
        maxs = [trend_data[p]['max'] for p in platforms]
        avgs = [trend_data[p]['avg'] for p in platforms]

        return {
            "type": "rangeBar",
            "title": "各平台价格区间",
            "labels": platforms,
            "datasets": [
                {"label": "最低价", "data": mins, "backgroundColor": "#52c41a"},
                {"label": "平均价", "data": avgs, "backgroundColor": "#1890ff"},
                {"label": "最高价", "data": maxs, "backgroundColor": "#ff4d4f"}
            ]
        }

    @classmethod
    def generate_all_charts(cls, compare_result: CompareResult) -> Dict[str, Any]:
        """生成所有图表数据"""
        return {
            "price_comparison": cls.generate_price_comparison_chart(compare_result.products),
            "sales_ranking": cls.generate_sales_ranking_chart(compare_result.products),
            "platform_comparison": cls.generate_platform_comparison_chart(compare_result.products),
            "value_radar": cls.generate_value_radar_chart(compare_result.products),
            "price_trend": cls.generate_price_trend_chart(compare_result.price_trend)
        }


import random
