"""
数据清洗与格式化模块
"""

import re
from typing import List, Optional
from architecture import ProductItem


class Cleaner:
    """数据清洗器"""

    @staticmethod
    def clean_product(product: ProductItem) -> ProductItem:
        """清洗单个商品数据"""
        # 清理名称中的特殊字符
        product.name = Cleaner.clean_name(product.name)

        # 验证价格
        product.price = Cleaner.validate_price(product.price)

        # 验证销量
        product.sales = Cleaner.validate_sales(product.sales)

        # 验证评分
        product.shop_score = Cleaner.validate_score(product.shop_score)

        # 清理URL
        product.url = Cleaner.clean_url(product.url)

        return product

    @staticmethod
    def clean_name(name: str) -> str:
        """清理商品名称"""
        if not name:
            return "未知商品"

        # 移除多余空白
        name = re.sub(r'\s+', ' ', name)

        # 移除特殊字符（保留中文、英文、数字、常用符号）
        name = re.sub(r'[^\w\s\u4e00-\u9fff\-\(\)（）]', '', name)

        return name.strip()

    @staticmethod
    def validate_price(price: float) -> float:
        """验证并规范化价格"""
        try:
            price = float(price)
            # 价格范围检查 (0.01 - 1000000)
            if price < 0.01:
                return 0.01
            if price > 1000000:
                return 1000000
            return round(price, 2)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def validate_sales(sales: int) -> int:
        """验证销量数据"""
        try:
            sales = int(sales)
            if sales < 0:
                return 0
            return sales
        except (ValueError, TypeError):
            return 0

    @staticmethod
    def validate_score(score: float) -> float:
        """验证店铺评分"""
        try:
            score = float(score)
            if score < 0:
                return 0.0
            if score > 5.0:
                return 5.0
            return round(score, 1)
        except (ValueError, TypeError):
            return 0.0

    @staticmethod
    def clean_url(url: str) -> str:
        """清理URL"""
        if not url:
            return "#"

        # 确保URL有协议头
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url

        return url.strip()

    @classmethod
    def clean_batch(cls, products: List[ProductItem]) -> List[ProductItem]:
        """批量清洗"""
        return [cls.clean_product(p) for p in products]

    @classmethod
    def filter_valid(cls, products: List[ProductItem]) -> List[ProductItem]:
        """过滤无效数据"""
        valid = []
        for p in products:
            # 必须有名称和有效价格
            if not p.name or p.name == "未知商品":
                continue
            if p.price <= 0:
                continue
            valid.append(p)
        return valid
