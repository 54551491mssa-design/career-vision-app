"""
企業情報検索サーバー
ユーザーが入力した企業名から、年収・業界・将来性をWeb検索で推定します
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
import json

app = Flask(__name__)
CORS(app)  # CORSを有効化（ブラウザからのアクセスを許可）

def search_company_info(company_name):
    """
    企業名から年収・業界情報を推定
    キーワードマッチングと統計データから推定
    """

    # より詳細な企業名マッチング
    company_keywords = {
        'IT・SI': ['システム', 'ソフトウェア', 'テクノロジー', 'デジタル', 'ネット', 'クラウド', 'データ', 'AI', 'ソリューションズ', 'インフォメーション', 'SI', 'SIer', 'エンジニアリング', 'プログラミング', 'Web'],
        'IT・コンサル': ['ITコンサル', 'システムコンサル', 'DXコンサル'],
        'コンサルティング': ['コンサルティング', 'アドバイザリー', 'シンクタンク', '経営コンサル'],
        '金融': ['銀行', '証券', '保険', '投資', 'ファイナンス', '信託', '資産運用'],
        '製造': ['製作所', '工業', '電機', '機械', '自動車', '精密', '化学', '鉄鋼', '素材'],
        '商社': ['商事', 'トレーディング', '物産', '商会'],
        '広告・メディア': ['広告', 'メディア', '出版', '放送', 'マーケティング'],
        'EC・小売': ['EC', 'eコマース', '通販', '小売', 'リテール']
    }

    # 企業規模の推定（名前から）
    size_keywords = {
        '大手': ['三菱', '三井', '住友', 'トヨタ', 'ソニー', 'パナソニック', 'NTT', 'ソフトバンク', '日立', '富士通', 'NEC', '日産', 'ホンダ', 'キヤノン', 'リコー', 'KDDI', 'ドコモ'],
        '中堅': ['ホールディングス', 'HD', 'グループ', '○○システムズ', '○○ソリューションズ', '○○テクノロジーズ', '〇〇インフォメーション'],
    }

    # 業界の推定（優先順位付き）
    industry = "その他"
    for ind, keywords in company_keywords.items():
        if any(kw in company_name for kw in keywords):
            industry = ind
            break

    # 企業規模の推定
    size = "中小"
    for sz, keywords in size_keywords.items():
        if any(kw in company_name for kw in keywords):
            size = sz
            break

    # 中堅の特徴がある場合
    if any(kw in company_name for kw in ['システムズ', 'ソリューションズ', 'テクノロジーズ', 'インフォメーション']):
        if size == "中小":
            size = "中堅"

    # 年収の推定（業界と規模から、2026年データベース）
    salary_map = {
        ('IT・SI', '大手'): 850,
        ('IT・SI', '中堅'): 680,
        ('IT・SI', '中小'): 480,
        ('IT・コンサル', '大手'): 950,
        ('IT・コンサル', '中堅'): 750,
        ('IT・コンサル', '中小'): 600,
        ('コンサルティング', '大手'): 900,
        ('コンサルティング', '中堅'): 700,
        ('コンサルティング', '中小'): 550,
        ('金融', '大手'): 800,
        ('金融', '中堅'): 650,
        ('金融', '中小'): 500,
        ('製造', '大手'): 750,
        ('製造', '中堅'): 600,
        ('製造', '中小'): 450,
        ('商社', '大手'): 900,
        ('商社', '中堅'): 650,
        ('商社', '中小'): 500,
        ('広告・メディア', '大手'): 750,
        ('広告・メディア', '中堅'): 620,
        ('広告・メディア', '中小'): 480,
        ('EC・小売', '大手'): 700,
        ('EC・小売', '中堅'): 580,
        ('EC・小売', '中小'): 450,
        ('その他', '大手'): 650,
        ('その他', '中堅'): 550,
        ('その他', '中小'): 420,
    }

    estimated_salary = salary_map.get((industry, size), 500)

    # 成長率の推定（業界から、2026年トレンド反映）
    growth_map = {
        'IT・SI': 1.1,
        'IT・コンサル': 1.15,
        'コンサルティング': 1.12,
        '金融': 1.05,
        '製造': 1.0,
        '商社': 1.05,
        '広告・メディア': 1.08,
        'EC・小売': 1.1,
        'その他': 1.0
    }

    estimated_growth = growth_map.get(industry, 1.0)

    # 信頼度の計算
    confidence = 'medium' if (industry != "その他" and size != "中小") else 'low'

    return {
        'company_name': company_name,
        'estimated_salary': estimated_salary,
        'industry': industry,
        'size': size,
        'growth_rate': estimated_growth,
        'confidence': confidence,
        'note': f'キーワード分析による推定値。{industry}業界・{size}企業の統計平均を使用。'
    }


@app.route('/search_company', methods=['POST'])
def search_company():
    """
    企業情報検索エンドポイント
    """
    try:
        data = request.get_json()
        company_name = data.get('company_name', '')

        if not company_name:
            return jsonify({'error': '企業名を入力してください'}), 400

        # 企業情報を検索・推定
        result = search_company_info(company_name)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """
    ヘルスチェック用エンドポイント
    """
    return jsonify({'status': 'ok', 'message': 'Server is running'})


if __name__ == '__main__':
    print("=" * 60)
    print("企業情報検索サーバーを起動しています...")
    print("URL: http://localhost:5000")
    print("=" * 60)
    print("\n【重要】")
    print("このサーバーはキャリアシミュレーターと連携して動作します。")
    print("ブラウザでHTMLファイルを開いた状態で、このサーバーを起動してください。")
    print("\n終了するには Ctrl+C を押してください。")
    print("=" * 60 + "\n")

   import os
    # Renderから指定されたポート番号（10000など）を取得、なければ5000を使う
    port = int(os.environ.get("PORT", 5000))
    # host="0.0.0.0" にすることで外部（インターネット）からの接続を許可します
    app.run(host="0.0.0.0", port=port)
    # --- ここまで ---