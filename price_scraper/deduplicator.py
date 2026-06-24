"""
数据去重模块
支持按名称、URL、价格等多维度去重
"""

import re
from typing import List, Dict, Set
from architecture import ProductItem


class Deduplicator:
    """智能去重器"""

    def __init__(self, similarity_threshold: float = 0.85):
        """
        Args:
            similarity_threshold: 名称相似度阈值 (0-1)
        """
        self.similarity_threshold = similarity_threshold

    def deduplicate(self, products: List[ProductItem]) -> List[ProductItem]:
        """执行去重"""
        # 第一步：精确去重（相同URL）
        products = self._dedupe_by_url(products)

        # 第二步：名称相似度去重
        products = self._dedupe_by_similarity(products)

        # 第三步：同平台同价格保留最低价
        products = self._dedupe_by_platform_price(products)

        return products

    def _dedupe_by_url(self, products: List[ProductItem]) -> List[ProductItem]:
        """按URL精确去重"""
        seen_urls: Set[str] = set()
        result = []

        for p in products:
            url_key = self._normalize_url(p.url)
            if url_key not in seen_urls:
                seen_urls.add(url_key)
                result.append(p)

        return result

    def _dedupe_by_similarity(self, products: List[ProductItem]) -> List[ProductItem]:
        """按名称相似度去重"""
        result = []
        seen_signatures: Set[str] = set()

        for p in products:
            signature = self._get_signature(p.name)
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                result.append(p)
            else:
                # 如果重复，保留评分更高或销量更高的
                existing = next((x for x in result if self._get_signature(x.name) == signature), None)
                if existing and self._is_better(p, existing):
                    result.remove(existing)
                    result.append(p)

        return result

    def _dedupe_by_platform_price(self, products: List[ProductItem]) -> List[ProductItem]:
        """同平台同价格商品保留最优"""
        seen: Dict[str, ProductItem] = {}
        result = []

        for p in products:
            key = f"{p.platform}:{p.name}:{int(p.price)}"
            if key not in seen:
                seen[key] = p
                result.append(p)
            else:
                # 保留更好的
                if self._is_better(p, seen[key]):
                    result.remove(seen[key])
                    result.append(p)
                    seen[key] = p

        return result

    def _normalize_url(self, url: str) -> str:
        """规范化URL"""
        if not url:
            return ""
        # 移除协议和常见参数
        url = re.sub(r'^https?://', '', url)
        url = url.split('?')[0]
        url = url.rstrip('/')
        return url.lower()

    def _get_signature(self, name: str) -> str:
        """提取名称签名用于比较"""
        # 转小写
        name = name.lower()
        # 移除非关键字符
        name = re.sub(r'[^\w\u4e00-\u9fff]', '', name)
        # 提取关键文字
        return self._normalize_chinese(name)

    @staticmethod
    def _normalize_chinese(text: str) -> str:
        """中文繁简转换和规范化"""
        # 简繁转换映射
        mapping = {
            '電': '电', '機': '机', '網': '网', '話': '话',
            '數': '数', '據': '据', '碼': '码', '號': '号',
        }
        for old, new in mapping.items():
            text = text.replace(old, new)
        return text

    def _is_better(self, new: ProductItem, existing: ProductItem) -> bool:
        """判断新商品是否更好"""
        # 综合评分：销量 * 评分 / 价格
        existing_score = existing.sales * existing.shop_score / (existing.price + 1)
        new_score = new.sales * new.shop_score / (new.price + 1)
        return new_score > existing_score

    @classmethod
    def deduplicate_simple(cls, products: List[ProductItem]) -> List[ProductItem]:
        """简单去重（保留首次出现的）"""
        seen = set()
        result = []
        for p in products:
            key = f"{p.name}|{p.platform}|{int(p.price)}"
            if key not in seen:
                seen.add(key)
                result.append(p)
        return result
