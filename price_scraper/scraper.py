"""
数据采集核心模块
支持多平台异步并行采集
"""

import asyncio
import random
import hashlib
import re
from typing import List, Dict, Callable, Optional
from datetime import datetime
from architecture import ProductItem


class MockScraper:
    """模拟采集器 - 生成真实的模拟数据用于演示"""

    PLATFORMS = ["京东", "淘宝", "拼多多", "天猫"]

    # 模拟商品库
    PRODUCT_TEMPLATES = [
        {"name": "Apple iPhone 15 Pro 256GB 5G手机", "category": "手机", "base_price": 7999},
        {"name": "小米14 Pro 骁龙8 Gen3 旗舰手机", "category": "手机", "base_price": 4999},
        {"name": "华为Mate 60 Pro 麒麟芯片 5G手机", "category": "手机", "base_price": 6999},
        {"name": "vivo X100 Pro 蔡司镜头 拍照手机", "category": "手机", "base_price": 5499},
        {"name": "OPPO Find X7 Ultra 哈苏影像旗舰", "category": "手机", "base_price": 5999},
        {"name": "联想拯救者R9000P 游戏笔记本", "category": "电脑", "base_price": 8999},
        {"name": "戴尔游匣G15 酷睿i7 游戏本", "category": "电脑", "base_price": 7599},
        {"name": "华硕天选4 锐龙版 游戏笔记本", "category": "电脑", "base_price": 7299},
        {"name": "索尼WH-1000XM5 降噪耳机", "category": "数码", "base_price": 2499},
        {"name": "AirPods Pro 2 代蓝牙耳机", "category": "数码", "base_price": 1799},
        {"name": "华为FreeBuds Pro 3 降噪耳机", "category": "数码", "base_price": 1499},
        {"name": "戴森V15吸尘器 智能无绳", "category": "家电", "base_price": 5499},
        {"name": "石头G20S 扫地机器人", "category": "家电", "base_price": 4999},
        {"name": "科沃斯X2 Pro 扫拖一体机", "category": "家电", "base_price": 4599},
    ]

    @classmethod
    def generate_product_id(cls, name: str, platform: str) -> str:
        """生成唯一商品ID"""
        raw = f"{name}{platform}{datetime.now().date()}"
        return hashlib.md5(raw.encode()).hexdigest()[:12]

    @classmethod
    def match_template(cls, keyword: str) -> List[Dict]:
        """根据关键词匹配商品模板"""
        keyword_lower = keyword.lower()
        matched = []

        for template in cls.PRODUCT_TEMPLATES:
            if keyword_lower in template["name"].lower():
                matched.append(template)
            elif any(kw in template["name"].lower() for kw in keyword_lower.split()):
                matched.append(template)

        # 如果没有精确匹配，返回相关类别或全部
        if not matched:
            for template in cls.PRODUCT_TEMPLATES:
                if any(kw in template["name"].lower() for kw in keyword_lower.split()):
                    matched.append(template)

        # 仍然没有，返回全部作为泛搜索
        if not matched:
            return cls.PRODUCT_TEMPLATES[:6]

        return matched[:8]

    @classmethod
    def scrape_platform(cls, keyword: str, platform: str, callback: Optional[Callable] = None) -> List[ProductItem]:
        """模拟单个平台采集"""
        templates = cls.match_template(keyword)
        products = []

        for template in templates:
            # 模拟价格波动 (±15%)
            price波动 = random.uniform(0.85, 1.15)
            # 不同平台价格差异
            platform_multiplier = {
                "京东": 1.05,   # 京东稍贵
                "淘宝": 0.95,   # 淘宝便宜
                "拼多多": 0.88, # 拼多多最便宜
                "天猫": 1.02    # 天猫居中
            }.get(platform, 1.0)

            final_price = round(template["base_price"] * price波动 * platform_multiplier, 2)

            # 模拟销量 (100-50000)
            sales = random.randint(100, 50000)

            # 模拟评分 (3.5-5.0)
            shop_score = round(random.uniform(3.5, 5.0), 1)

            # 生成URL
            product_id = cls.generate_product_id(template["name"], platform)
            url = f"https://www.{platform}.com/product/{product_id}.html"

            product = ProductItem(
                id=product_id,
                name=template["name"],
                platform=platform,
                price=final_price,
                sales=sales,
                shop_score=shop_score,
                url=url,
                category=template["category"],
                采集时间=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            products.append(product)

        return products


class AsyncScraper:
    """异步并行采集器"""

    def __init__(self, platforms: Optional[List[str]] = None):
        self.platforms = platforms or MockScraper.PLATFORMS
        self.results: List[ProductItem] = []

    async def scrape_keyword(self, keyword: str, progress_callback: Optional[Callable] = None) -> List[ProductItem]:
        """异步采集关键词相关商品"""
        tasks = []

        for platform in self.platforms:
            task = asyncio.create_task(
                self._scrape_with_platform(keyword, platform, progress_callback)
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_products = []
        for result in results:
            if isinstance(result, list):
                all_products.extend(result)

        return all_products

    async def _scrape_with_platform(self, keyword: str, platform: str,
                                     callback: Optional[Callable] = None) -> List[ProductItem]:
        """单个平台采集（带延迟模拟）"""
        # 模拟网络延迟
        await asyncio.sleep(random.uniform(0.3, 0.8))

        products = MockScraper.scrape_platform(keyword, platform)

        if callback:
            callback(platform, len(products))

        return products


def scrape_sync(keyword: str, platforms: Optional[List[str]] = None) -> List[ProductItem]:
    """同步采集入口"""
    scraper = AsyncScraper(platforms)
    return asyncio.run(scraper.scrape_keyword(keyword))


if __name__ == "__main__":
    # 测试采集
    print("测试采集: 手机")
    results = scrape_sync("手机")
    print(f"采集到 {len(results)} 个商品:")
    for p in results[:3]:
        print(f"  {p.platform}: {p.name} - ¥{p.price}")
