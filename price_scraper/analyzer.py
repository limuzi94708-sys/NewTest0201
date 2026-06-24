"""
数据分析与性价比计算模块
"""

import math
from typing import List, Dict, Tuple
from architecture import ProductItem, AnalysisResult, CompareResult
from datetime import datetime


class Analyzer:
    """数据分析器"""

    # 性价比权重配置
    WEIGHTS = {
        'price': 0.35,       # 价格权重
        'sales': 0.30,       # 销量权重
        'score': 0.25,       # 评分权重
        'consistency': 0.10 # 价格一致性权重
    }

    @classmethod
    def analyze(cls, products: List[ProductItem]) -> List[AnalysisResult]:
        """分析商品列表并返回排名和推荐"""
        if not products:
            return []

        # 计算各项指标
        prices = [p.price for p in products]
        sales = [p.sales for p in products]
        scores = [p.shop_score for p in products]

        avg_price = sum(prices) / len(prices)
        max_price = max(prices)
        min_price = min(prices)
        max_sales = max(sales) if sales else 1
        max_score = max(scores) if scores else 5.0

        # 计算价格排名（价格越低排名越高）
        price_ranked = sorted(products, key=lambda x: x.price)
        price_ranks = {p.id: i + 1 for i, p in enumerate(price_ranked)}

        # 计算销量排名
        sales_ranked = sorted(products, key=lambda x: x.sales, reverse=True)
        sales_ranks = {p.id: i + 1 for i, p in enumerate(sales_ranked)}

        # 计算评分排名
        score_ranked = sorted(products, key=lambda x: x.shop_score, reverse=True)
        score_ranks = {p.id: i + 1 for i, p in enumerate(score_ranked)}

        results = []
        for p in products:
            # 归一化得分 (0-100)
            price_score = cls._normalize_score(p.price, min_price, max_price, lower_is_better=True)
            sales_score = cls._normalize_score(p.sales, 0, max_sales, lower_is_better=False)
            score_score = cls._normalize_score(p.shop_score, 0, max_score, lower_is_better=False)

            # 性价比综合得分
            value_score = (
                price_score * cls.WEIGHTS['price'] +
                sales_score * cls.WEIGHTS['sales'] +
                score_score * cls.WEIGHTS['score']
            )

            # 推荐等级
            recommendation = cls._get_recommendation(value_score, price_score, score_score)

            # 与平均价格偏差
            price_from_avg = ((p.price - avg_price) / avg_price) * 100 if avg_price > 0 else 0

            result = AnalysisResult(
                product=p,
                price_rank=price_ranks[p.id],
                sales_rank=sales_ranks[p.id],
                score_rank=score_ranks[p.id],
                value_score=round(value_score, 2),
                recommendation=recommendation,
                price_from_avg=round(price_from_avg, 1)
            )
            results.append(result)

        return results

    @staticmethod
    def _normalize_score(value: float, min_val: float, max_val: float,
                         lower_is_better: bool = False) -> float:
        """归一化得分到0-100"""
        if max_val == min_val:
            return 50.0

        normalized = (value - min_val) / (max_val - min_val)

        if lower_is_better:
            normalized = 1 - normalized

        return normalized * 100

    @staticmethod
    def _get_recommendation(value_score: float, price_score: float, score_score: float) -> str:
        """根据综合得分确定推荐等级"""
        if value_score >= 75 and price_score >= 60:
            return "强烈推荐"
        elif value_score >= 60:
            return "推荐"
        elif value_score >= 40:
            return "一般"
        else:
            return "不推荐"

    @classmethod
    def sort_results(cls, results: List[AnalysisResult],
                     sort_by: str = 'price') -> List[AnalysisResult]:
        """排序结果"""
        if sort_by == 'price':
            return sorted(results, key=lambda x: x.product.price)
        elif sort_by == 'sales':
            return sorted(results, key=lambda x: x.product.sales, reverse=True)
        elif sort_by == 'score':
            return sorted(results, key=lambda x: x.product.shop_score, reverse=True)
        elif sort_by == 'value':
            return sorted(results, key=lambda x: x.value_score, reverse=True)
        elif sort_by == 'price_rank':
            return sorted(results, key=lambda x: x.price_rank)
        else:
            return sorted(results, key=lambda x: x.product.price)

    @classmethod
    def generate_price_trend(cls, products: List[ProductItem]) -> Dict:
        """生成价格趋势数据"""
        # 按平台分组
        platform_prices: Dict[str, List[float]] = {}
        for p in products:
            if p.platform not in platform_prices:
                platform_prices[p.platform] = []
            platform_prices[p.platform].append(p.price)

        trend = {}
        for platform, prices in platform_prices.items():
            if prices:
                trend[platform] = {
                    'min': min(prices),
                    'max': max(prices),
                    'avg': round(sum(prices) / len(prices), 2),
                    'count': len(prices)
                }

        return trend

    @classmethod
    def build_compare_result(cls, keyword: str, products: List[ProductItem]) -> CompareResult:
        """构建完整对比结果"""
        analyzed = cls.analyze(products)
        sorted_results = cls.sort_results(analyzed, 'price')

        platforms = list(set(p.platform for p in products))

        return CompareResult(
            keyword=keyword,
            total_products=len(products),
            platforms=platforms,
            products=sorted_results,
            generated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            price_trend=cls.generate_price_trend(products)
        )
