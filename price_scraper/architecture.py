"""
电商价格采集与对比系统
整体架构设计

## 系统架构

┌─────────────────────────────────────────────────────────────┐
│                    电商价格采集与对比系统                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────┐         ┌──────────────────────────┐  │
│  │    命令行工具     │         │       演示网页           │  │
│  │   price_cli.py   │         │    web/index.html        │  │
│  └────────┬─────────┘         └───────────┬──────────────┘  │
│           │                              │                  │
│           └──────────────┬────────────────┘                  │
│                          ▼                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   API 服务层                           │   │
│  │              api_server.py (Flask)                    │   │
│  └──────────────────────────┬───────────────────────────┘   │
│                             │                               │
│  ┌──────────────────────────▼───────────────────────────┐   │
│  │                   核心处理层                           │   │
│  │  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐  │   │
│  │  │Scraper  │→ │Cleaner  │→ │Deduplica│→ │Analyzer │  │   │
│  │  │ 采集器   │  │ 清洗器   │  │ 去重器   │  │ 分析器   │  │   │
│  │  └─────────┘  └─────────┘  └─────────┘  └─────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                             │                               │
│  ┌──────────────────────────▼───────────────────────────┐   │
│  │                   平台适配层                           │   │
│  │  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐       │   │
│  │  │ JD     │  │ TAOBAO │  │ PINDD  │  │ TIANMAO│       │   │
│  │  │ 京东   │  │ 淘宝   │  │ 拼多多  │  │ 天猫   │       │   │
│  │  └────────┘  └────────┘  └────────┘  └────────┘       │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘

## 数据流程

1. 用户输入关键词 → 采集器并行抓取多平台
2. 原始数据 → 清洗器（格式化、验证）
3. 清洗后数据 → 去重器（按商品名称/链接去重）
4. 去重后数据 → 分析器（计算性价比、趋势）
5. 分析结果 → 排序（价格/销量/评分）
6. 最终结果 → 输出（CLI表格/JSON/网页图表）

## 数据模型

ProductItem:
  - id: str              # 商品唯一标识
  - name: str            # 商品名称
  - platform: str        # 平台名称
  - price: float         # 价格
  - sales: int           # 销量
  - shop_score: float    # 店铺评分 (0-5)
  - url: str             # 商品链接
  - category: str        # 商品类目
  -采集时间: str          # 采集时间戳

## 核心模块

1. scraper.py      - 多线程异步采集器
2. cleaner.py      - 数据清洗与格式化
3. deduplicator.py - 智能去重算法
4. analyzer.py     - 数据分析与性价比计算
5. visualizer.py   - 图表生成器
6. api_server.py   - Web API服务
7. price_cli.py     - 命令行入口

## 可视化方案

1. 价格对比柱状图 - 各平台同商品价格对比
2. 销量排行条形图 - 按销量排序的商品排行
3. 性价比雷达图 - 多维度评估商品性价比
4. 价格趋势折线图 - 商品历史价格走势
"""

import dataclasses
from typing import List, Optional
from datetime import datetime

@dataclasses.dataclass
class ProductItem:
    """商品数据模型"""
    id: str
    name: str
    platform: str
    price: float
    sales: int
    shop_score: float
    url: str
    category: str
    采集时间: str = dataclasses.field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self):
        return dataclasses.asdict(self)

@dataclasses.dataclass
class AnalysisResult:
    """分析结果模型"""
    product: ProductItem
    price_rank: int          # 价格排名
    sales_rank: int           # 销量排名
    score_rank: int           # 评分排名
    value_score: float        # 性价比得分 (0-100)
    recommendation: str       # 推荐等级: "强烈推荐" / "推荐" / "一般" / "不推荐"
    price_from_avg: float     # 与平均价格偏差百分比

@dataclasses.dataclass
class CompareResult:
    """对比结果模型"""
    keyword: str
    total_products: int
    platforms: List[str]
    products: List[AnalysisResult]
    generated_at: str
    price_trend: dict         # 价格趋势数据
