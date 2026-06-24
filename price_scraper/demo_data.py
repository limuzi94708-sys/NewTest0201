"""
示例数据生成器
用于初始化演示页面
"""

import json
import random
from datetime import datetime, timedelta

DEMO_DATA = {
    "keyword": "手机",
    "total_products": 24,
    "platforms": ["京东", "淘宝", "拼多多", "天猫"],
    "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "price_trend": {
        "京东": {"min": 4899, "max": 9999, "avg": 6845.30, "count": 6},
        "淘宝": {"min": 4599, "max": 8999, "avg": 6299.50, "count": 6},
        "拼多多": {"min": 4199, "max": 7999, "avg": 5599.20, "count": 6},
        "天猫": {"min": 4999, "max": 9599, "avg": 6999.00, "count": 6}
    },
    "products": [
        {
            "id": "a1b2c3d4e5f6",
            "name": "小米14 Pro 骁龙8 Gen3 旗舰手机",
            "platform": "拼多多",
            "price": 4599.00,
            "sales": 25800,
            "shop_score": 4.8,
            "url": "https://www.pinduoduo.com/product/a1b2c3d4e5f6.html",
            "category": "手机",
            "price_rank": 1,
            "sales_rank": 2,
            "value_score": 92.5,
            "recommendation": "强烈推荐",
            "price_from_avg": -18.5
        },
        {
            "id": "b2c3d4e5f6g7",
            "name": "vivo X100 Pro 蔡司镜头 拍照手机",
            "platform": "淘宝",
            "price": 4999.00,
            "sales": 18500,
            "shop_score": 4.7,
            "url": "https://www.taobao.com/product/b2c3d4e5f6g7.html",
            "category": "手机",
            "price_rank": 2,
            "sales_rank": 4,
            "value_score": 88.3,
            "recommendation": "强烈推荐",
            "price_from_avg": -12.3
        },
        {
            "id": "c3d4e5f6g7h8",
            "name": "OPPO Find X7 Ultra 哈苏影像旗舰",
            "platform": "拼多多",
            "price": 5199.00,
            "sales": 15200,
            "shop_score": 4.9,
            "url": "https://www.pinduoduo.com/product/c3d4e5f6g7h8.html",
            "category": "手机",
            "price_rank": 3,
            "sales_rank": 5,
            "value_score": 87.2,
            "recommendation": "推荐",
            "price_from_avg": -8.5
        },
        {
            "id": "d4e5f6g7h8i9",
            "name": "华为Mate 60 Pro 麒麟芯片 5G手机",
            "platform": "京东",
            "price": 6499.00,
            "sales": 42000,
            "shop_score": 4.9,
            "url": "https://www.jd.com/product/d4e5f6g7h8i9.html",
            "category": "手机",
            "price_rank": 8,
            "sales_rank": 1,
            "value_score": 85.6,
            "recommendation": "推荐",
            "price_from_avg": 8.2
        },
        {
            "id": "e5f6g7h8i9j0",
            "name": "Apple iPhone 15 Pro 256GB 5G手机",
            "platform": "天猫",
            "price": 7999.00,
            "sales": 32000,
            "shop_score": 4.8,
            "url": "https://www.tmall.com/product/e5f6g7h8i9j0.html",
            "category": "手机",
            "price_rank": 15,
            "sales_rank": 3,
            "value_score": 72.1,
            "recommendation": "推荐",
            "price_from_avg": 25.8
        },
        {
            "id": "f6g7h8i9j0k1",
            "name": "小米14 Pro 骁龙8 Gen3 旗舰手机",
            "platform": "京东",
            "price": 5299.00,
            "sales": 25800,
            "shop_score": 4.8,
            "url": "https://www.jd.com/product/f6g7h8i9j0k1.html",
            "category": "手机",
            "price_rank": 4,
            "sales_rank": 2,
            "value_score": 89.5,
            "recommendation": "强烈推荐",
            "price_from_avg": -6.2
        }
    ]
}

DEMO_CHARTS = {
    "price_comparison": {
        "type": "bar",
        "title": "商品价格对比",
        "labels": ["小米14 Pro", "vivo X100 Pro", "OPPO Find X7", "华为Mate 60", "iPhone 15 Pro"],
        "datasets": [{
            "label": "价格(元)",
            "data": [4599, 4999, 5199, 6499, 7999],
            "backgroundColor": ["#52c41a", "#52c41a", "#1890ff", "#1890ff", "#faad14"]
        }],
        "recommendations": ["强烈推荐", "强烈推荐", "推荐", "推荐", "推荐"]
    },
    "sales_ranking": {
        "type": "horizontalBar",
        "title": "销量排行榜",
        "labels": ["华为Mate 60 Pro", "iPhone 15 Pro", "小米14 Pro", "OPPO Find X7", "vivo X100"],
        "datasets": [{
            "label": "销量",
            "data": [42000, 32000, 25800, 15200, 18500],
            "backgroundColor": "#1890ff"
        }],
        "platforms": ["京东", "天猫", "拼多多/京东", "拼多多", "淘宝"]
    },
    "platform_comparison": {
        "type": "mixed",
        "title": "各平台综合对比",
        "labels": ["京东", "淘宝", "拼多多", "天猫"],
        "datasets": [
            {"label": "平均价格(元)", "data": [6845, 6299, 5599, 6999], "type": "bar", "backgroundColor": "#1890ff"},
            {"label": "平均评分", "data": [4.8, 4.7, 4.6, 4.8], "type": "line", "borderColor": "#52c41a", "yAxisID": "y1"}
        ],
        "yAxes": {
            "y": {"label": "价格(元)", "position": "left"},
            "y1": {"label": "评分", "position": "right", "min": 0, "max": 5}
        }
    },
    "value_radar": {
        "type": "radar",
        "title": "Top5商品多维度对比",
        "labels": ["价格优势", "销量表现", "评分高低", "性价比", "推荐指数"],
        "datasets": [
            {"label": "小米14 Pro", "data": [95, 85, 90, 92, 95], "backgroundColor": "rgba(24, 144, 255, 0.2)"},
            {"label": "vivo X100 Pro", "data": [88, 75, 88, 88, 90], "backgroundColor": "rgba(82, 196, 26, 0.2)"},
            {"label": "华为Mate 60", "data": [65, 98, 98, 85, 88], "backgroundColor": "rgba(250, 173, 20, 0.2)"}
        ]
    },
    "price_trend": {
        "type": "rangeBar",
        "title": "各平台价格区间",
        "labels": ["京东", "淘宝", "拼多多", "天猫"],
        "datasets": [
            {"label": "最低价", "data": [4899, 4599, 4199, 4999], "backgroundColor": "#52c41a"},
            {"label": "平均价", "data": [6845, 6299, 5599, 6999], "backgroundColor": "#1890ff"},
            {"label": "最高价", "data": [9999, 8999, 7999, 9599], "backgroundColor": "#ff4d4f"}
        ]
    }
}


if __name__ == '__main__':
    # 输出示例数据
    print(json.dumps(DEMO_DATA, ensure_ascii=False, indent=2))
