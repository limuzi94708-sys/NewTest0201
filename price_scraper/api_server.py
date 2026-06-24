"""
Web API 服务器
提供 REST API 给前端页面调用
"""

import asyncio
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper import AsyncScraper
from cleaner import Cleaner
from deduplicator import Deduplicator
from analyzer import Analyzer
from visualizer import Visualizer
from architecture import CompareResult

app = Flask(__name__)
CORS(app)

# 存储最后一次的分析结果（用于页面展示）
latest_result = None


@app.route('/api/search', methods=['POST'])
def search():
    """搜索并分析商品"""
    global latest_result

    data = request.get_json()
    keyword = data.get('keyword', '')
    platforms = data.get('platforms', ['京东', '淘宝', '拼多多', '天猫'])
    sort_by = data.get('sort_by', 'price')

    if not keyword:
        return jsonify({'error': '关键词不能为空'}), 400

    # 执行采集和分析
    async def run_search():
        scraper = AsyncScraper(platforms)
        products = await scraper.scrape_keyword(keyword)

        # 清洗
        products = Cleaner.clean_batch(products)
        products = Cleaner.filter_valid(products)

        # 去重
        deduplicator = Deduplicator()
        products = deduplicator.deduplicate(products)

        # 分析
        result = Analyzer.build_compare_result(keyword, products)
        result.products = Analyzer.sort_results(result.products, sort_by)

        return result

    latest_result = asyncio.run(run_search())

    # 返回简化数据
    return jsonify({
        'keyword': latest_result.keyword,
        'total_products': latest_result.total_products,
        'platforms': latest_result.platforms,
        'generated_at': latest_result.generated_at,
        'price_trend': latest_result.price_trend,
        'products': [
            {
                'id': r.product.id,
                'name': r.product.name,
                'platform': r.product.platform,
                'price': r.product.price,
                'sales': r.product.sales,
                'shop_score': r.product.shop_score,
                'url': r.product.url,
                'category': r.product.category,
                'price_rank': r.price_rank,
                'sales_rank': r.sales_rank,
                'value_score': r.value_score,
                'recommendation': r.recommendation,
                'price_from_avg': r.price_from_avg
            }
            for r in latest_result.products
        ]
    })


@app.route('/api/charts', methods=['GET'])
def get_charts():
    """获取图表数据"""
    global latest_result

    if not latest_result:
        return jsonify({'error': '请先进行搜索'}), 400

    charts = Visualizer.generate_all_charts(latest_result)
    return jsonify(charts)


@app.route('/api/result', methods=['GET'])
def get_result():
    """获取完整结果"""
    global latest_result

    if not latest_result:
        return jsonify({'error': '请先进行搜索'}), 400

    return jsonify({
        'keyword': latest_result.keyword,
        'total_products': latest_result.total_products,
        'platforms': latest_result.platforms,
        'generated_at': latest_result.generated_at,
        'price_trend': latest_result.price_trend,
        'products': [
            {
                'id': r.product.id,
                'name': r.product.name,
                'platform': r.product.platform,
                'price': r.product.price,
                'sales': r.product.sales,
                'shop_score': r.product.shop_score,
                'url': r.product.url,
                'category': r.product.category,
                'price_rank': r.price_rank,
                'sales_rank': r.sales_rank,
                'value_score': r.value_score,
                'recommendation': r.recommendation,
                'price_from_avg': r.price_from_avg
            }
            for r in latest_result.products
        ]
    })


@app.route('/api/demo', methods=['GET'])
def get_demo():
    """获取演示数据"""
    global latest_result

    # 生成演示数据
    async def run_demo():
        scraper = AsyncScraper(['京东', '淘宝', '拼多多', '天猫'])
        products = await scraper.scrape_keyword('手机')

        products = Cleaner.clean_batch(products)
        products = Cleaner.filter_valid(products)

        deduplicator = Deduplicator()
        products = deduplicator.deduplicate(products)

        result = Analyzer.build_compare_result('手机', products)
        return result

    latest_result = asyncio.run(run_demo())

    # 生成图表
    charts = Visualizer.generate_all_charts(latest_result)

    return jsonify({
        'result': {
            'keyword': latest_result.keyword,
            'total_products': latest_result.total_products,
            'platforms': latest_result.platforms,
            'generated_at': latest_result.generated_at,
            'price_trend': latest_result.price_trend,
            'products': [
                {
                    'id': r.product.id,
                    'name': r.product.name,
                    'platform': r.product.platform,
                    'price': r.product.price,
                    'sales': r.product.sales,
                    'shop_score': r.product.shop_score,
                    'url': r.product.url,
                    'category': r.product.category,
                    'price_rank': r.price_rank,
                    'sales_rank': r.sales_rank,
                    'value_score': r.value_score,
                    'recommendation': r.recommendation,
                    'price_from_avg': r.price_from_avg
                }
                for r in latest_result.products
            ]
        },
        'charts': charts
    })


def run_server(host='0.0.0.0', port=5000):
    """启动服务器"""
    app.run(host=host, port=port, debug=True)


if __name__ == '__main__':
    run_server()
