"""
命令行工具入口
电商价格采集与对比工具
"""

#!/usr/bin/env python3
import argparse
import asyncio
import json
import sys
import os
from typing import List, Optional

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import AsyncScraper, scrape_sync
from cleaner import Cleaner
from deduplicator import Deduplicator
from analyzer import Analyzer
from visualizer import Visualizer
from architecture import CompareResult


class PriceComparisonCLI:
    """命令行工具"""

    def __init__(self):
        self.platforms = ["京东", "淘宝", "拼多多", "天猫"]

    def run(self, keyword: str, platforms: Optional[List[str]] = None,
            sort_by: str = 'price', top_n: int = 20,
            output: Optional[str] = None, json_only: bool = False):
        """执行采集和分析"""

        if platforms:
            self.platforms = platforms

        print(f"\n{'='*60}")
        print(f"电商价格采集与对比工具")
        print(f"{'='*60}")
        print(f"关键词: {keyword}")
        print(f"平台: {', '.join(self.platforms)}")
        print(f"排序: {sort_by}")
        print(f"{'='*60}\n")

        # 1. 采集数据
        print("[1/5] 正在采集数据...")
        scraper = AsyncScraper(self.platforms)
        products = asyncio.run(scraper.scrape_keyword(keyword))
        print(f"      采集完成，共 {len(products)} 条原始数据")

        # 2. 清洗数据
        print("[2/5] 正在清洗数据...")
        products = Cleaner.clean_batch(products)
        products = Cleaner.filter_valid(products)
        print(f"      清洗完成，有效数据 {len(products)} 条")

        # 3. 去重
        print("[3/5] 正在去重...")
        deduplicator = Deduplicator()
        products = deduplicator.deduplicate(products)
        print(f"      去重完成，剩余 {len(products)} 条")

        # 4. 分析
        print("[4/5] 正在分析...")
        compare_result = Analyzer.build_compare_result(keyword, products)
        sorted_results = Analyzer.sort_results(compare_result.products, sort_by)
        compare_result.products = sorted_results[:top_n]
        print(f"      分析完成")

        # 5. 输出
        print("[5/5] 生成结果...\n")

        if json_only:
            # 仅输出JSON
            output_data = self._to_json(compare_result)
            if output:
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                print(f"结果已保存到: {output}")
            else:
                print(json.dumps(output_data, ensure_ascii=False, indent=2))
        else:
            # 输出表格和摘要
            self._print_summary(compare_result)
            self._print_table(sorted_results[:top_n])

            if output:
                output_data = self._to_json(compare_result)
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(output_data, f, ensure_ascii=False, indent=2)
                print(f"\nJSON结果已保存到: {output}")

        return compare_result

    def _print_summary(self, result: CompareResult):
        """打印摘要"""
        print(f"\n{'='*60}")
        print(f"采集摘要")
        print(f"{'='*60}")
        print(f"关键词: {result.keyword}")
        print(f"总商品数: {result.total_products}")
        print(f"涵盖平台: {', '.join(result.platforms)}")
        print(f"生成时间: {result.generated_at}")
        print(f"\n价格趋势:")
        for platform, trend in result.price_trend.items():
            print(f"  {platform}: ¥{trend['min']:.2f} ~ ¥{trend['max']:.2f} (平均 ¥{trend['avg']:.2f})")
        print(f"{'='*60}\n")

    def _print_table(self, results: List):
        """打印商品表格"""
        if not results:
            print("没有找到商品")
            return

        # 表头
        header = f"{'排名':<4} {'商品名称':<30} {'平台':<6} {'价格':>10} {'销量':>10} {'评分':<6} {'推荐':<8}"
        print(header)
        print("-" * 90)

        for i, r in enumerate(results, 1):
            name = r.product.name[:28] + ".." if len(r.product.name) > 28 else r.product.name
            print(f"{i:<4} {name:<30} {r.product.platform:<6} ¥{r.product.price:>8.2f} "
                  f"{r.product.sales:>9} {r.product.shop_score:<6} {r.recommendation:<8}")

        print("-" * 90)

        # 打印图例
        print("\n推荐等级说明:")
        print("  强烈推荐 - 性价比极高，价格优惠，评分高")
        print("  推荐     - 性价比良好，综合表现优秀")
        print("  一般     - 性价比一般，可根据需求选择")
        print("  不推荐   - 性价比低，不建议购买")

    def _to_json(self, result: CompareResult) -> dict:
        """转换为JSON格式"""
        return {
            "keyword": result.keyword,
            "total_products": result.total_products,
            "platforms": result.platforms,
            "generated_at": result.generated_at,
            "price_trend": result.price_trend,
            "products": [
                {
                    "name": r.product.name,
                    "platform": r.product.platform,
                    "price": r.product.price,
                    "sales": r.product.sales,
                    "shop_score": r.product.shop_score,
                    "url": r.product.url,
                    "category": r.product.category,
                    "price_rank": r.price_rank,
                    "sales_rank": r.sales_rank,
                    "score_rank": r.score_rank,
                    "value_score": r.value_score,
                    "recommendation": r.recommendation,
                    "price_from_avg": r.price_from_avg
                }
                for r in result.products
            ]
        }


def main():
    parser = argparse.ArgumentParser(
        description='电商价格采集与对比工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s 手机 -t 30
  %(prog)s 笔记本 --platforms 京东 淘宝 --sort_by sales
  %(prog)s 耳机 -o result.json --json_only
        """
    )

    parser.add_argument('keyword', nargs='?', default='手机',
                        help='搜索关键词 (默认: 手机)')
    parser.add_argument('-p', '--platforms', nargs='+',
                        choices=['京东', '淘宝', '拼多多', '天猫'],
                        help='指定采集平台')
    parser.add_argument('-s', '--sort_by', default='price',
                        choices=['price', 'sales', 'score', 'value'],
                        help='排序方式 (默认: price)')
    parser.add_argument('-n', '--top_n', type=int, default=20,
                        help='显示数量 (默认: 20)')
    parser.add_argument('-o', '--output', help='输出JSON文件路径')
    parser.add_argument('-j', '--json_only', action='store_true',
                        help='仅输出JSON格式')

    args = parser.parse_args()

    cli = PriceComparisonCLI()
    cli.run(
        keyword=args.keyword,
        platforms=args.platforms,
        sort_by=args.sort_by,
        top_n=args.top_n,
        output=args.output,
        json_only=args.json_only
    )


if __name__ == '__main__':
    main()
