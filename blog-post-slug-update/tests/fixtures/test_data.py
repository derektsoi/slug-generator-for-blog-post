#!/usr/bin/env python3
"""
Test data fixtures for slug generator tests
Contains real BuyandShip URLs and expected content for testing
"""

# Real BuyandShip test cases with expected outputs
BUYANDSHIP_TEST_CASES = [
    {
        'name': 'jojo_maman_bebe',
        'url': 'https://www.buyandship.today/blog/2025/08/18/jojo-maman-bebe%e8%8b%b1%e5%9c%8b%e5%ae%98%e7%b6%b2%e6%8a%98%e6%89%a3%e5%8f%8a%e8%b3%bc%e8%b2%b7%e6%95%99%e5%ad%b8/',
        'title': '英國必買童裝 JoJo Maman Bébé官網 3 折起入手網購教學',
        'content_summary': 'A comprehensive guide to purchasing children\'s clothing and baby products from the British brand JoJo Maman Bébé, focusing on how Hong Kong customers can buy items through Buy&Ship\'s shipping and proxy shopping services.',
        'expected_slug': 'jojo-maman-bebe-uk-childrens-clothing-guide',
        'expected_alternatives': [
            'jojo-maman-bebe-shopping-guide',
            'uk-childrens-clothing-buying-guide',
            'jojo-maman-bebe-discount-guide'
        ],
        'keywords': ['jojo-maman-bebe', 'uk', 'childrens', 'clothing', 'shopping', 'guide', 'discount']
    },
    {
        'name': 'doll_clothing',
        'url': 'https://www.buyandship.today/blog/2025/08/13/%e5%a8%83%e8%a1%a3%e5%93%aa%e8%a3%a1%e8%b2%b7/',
        'title': '公仔衫、娃衣配件哪裡買？日本3COINS、Sanrio及手工製平台必買推介',
        'content_summary': 'A comprehensive guide to buying doll clothing from various Japanese online platforms, focusing on unique and high-quality doll outfits and accessories.',
        'expected_slug': 'japanese-doll-clothing-shopping-guide',
        'expected_alternatives': [
            'doll-clothes-buying-guide',
            'japanese-doll-accessories-guide',
            'doll-clothing-platforms-guide'
        ],
        'keywords': ['japanese', 'doll', 'clothing', 'shopping', 'guide', 'accessories']
    },
    {
        'name': 'kindle_guide',
        'url': 'https://www.buyandship.today/blog/2025/08/13/kindle%e7%b6%b2%e8%b3%bc%e6%94%bb%e7%95%a5/',
        'title': 'Kindle電子書閱讀器最強攻略：Paper White、Colorsoft等型號分別、價格比較及網購集運教學',
        'content_summary': 'A comprehensive guide to Amazon Kindle e-readers, comparing different models like Kindle Scribe, Colorsoft, Paperwhite, and basic Kindle, with pricing details and tips on purchasing from the US.',
        'expected_slug': 'kindle-ereader-buying-guide-comparison',
        'expected_alternatives': [
            'kindle-models-price-comparison',
            'amazon-kindle-buying-guide',
            'kindle-paperwhite-colorsoft-comparison'
        ],
        'keywords': ['kindle', 'ereader', 'buying', 'guide', 'comparison', 'paperwhite', 'colorsoft']
    },
    {
        'name': 'verish_price_comparison',
        'url': 'https://www.buyandship.today/blog/2025/08/18/verish%e9%9f%93%e5%83%b9%e5%b7%ae%e5%a4%a7%e6%af%94%e6%8b%bc/',
        'title': 'Verish韓價差大比拼',  # Inferred from URL
        'content_summary': 'Price comparison analysis for Verish brand products between Korea and other regions.',
        'expected_slug': 'verish-korea-price-comparison',
        'expected_alternatives': [
            'verish-brand-price-comparison',
            'korea-vs-local-pricing-verish',
            'verish-price-difference-analysis'
        ],
        'keywords': ['verish', 'korea', 'price', 'comparison', 'brand']
    },
    {
        'name': 'japanese_jewelry',
        'url': 'https://www.buyandship.today/blog/2025/08/18/%e6%97%a5%e6%9c%ac%e8%bc%95%e7%8f%a0%e5%af%b6%e5%93%81%e7%89%8c%e5%90%88%e9%9b%86/',
        'title': '8大日牌輕珠寶品牌一次睇！Agete、nojess及Star Jewelry等日劇女主御用明星珠寶',
        'content_summary': 'A comprehensive guide to popular Japanese lightweight jewelry brands, highlighting 8 different brands including Agete, nojess, Ahkah, K. Uno, Vendome Aoyama, Star Jewelry, Festaria Tokyo, and Canal 4°C.',
        'expected_slug': 'japanese-lightweight-jewelry-brands-guide',
        'expected_alternatives': [
            'japanese-jewelry-brands-collection',
            'agete-nojess-jewelry-brands-guide',
            'japanese-drama-jewelry-brands'
        ],
        'keywords': ['japanese', 'lightweight', 'jewelry', 'brands', 'guide', 'agete', 'nojess']
    }
]

# Generic test cases for edge conditions
GENERIC_TEST_CASES = [
    {
        'name': 'how_to_tutorial',
        'title': 'How to Deploy React Apps to AWS S3 in 2024',
        'expected_slug': 'deploy-react-apps-aws-s3',
        'keywords': ['deploy', 'react', 'apps', 'aws', 's3']
    },
    {
        'name': 'listicle',
        'title': '10 Best JavaScript Libraries for Data Visualization',
        'expected_slug': 'best-javascript-libraries-data-visualization',
        'keywords': ['best', 'javascript', 'libraries', 'data', 'visualization']
    },
    {
        'name': 'long_title_truncation',
        'title': 'The Complete Comprehensive Ultimate Beginner\'s Guide to Machine Learning with Python TensorFlow and Keras for Data Science Applications',
        'expected_slug': 'complete-guide-machine-learning-python',
        'keywords': ['complete', 'guide', 'machine', 'learning', 'python']
    },
    {
        'name': 'special_characters',
        'title': 'React 18.2.0: What\'s New & Breaking Changes (2024 Update)',
        'expected_slug': 'react-18-whats-new-breaking-changes',
        'keywords': ['react', '18', 'whats', 'new', 'breaking', 'changes']
    }
]

# Error test cases
ERROR_TEST_CASES = [
    {
        'name': 'invalid_url',
        'url': 'not-a-valid-url',
        'expected_error': 'ValueError',
        'error_message': 'Invalid URL format'
    },
    {
        'name': 'missing_protocol',
        'url': 'example.com/blog/post',
        'expected_error': 'ValueError',
        'error_message': 'Invalid URL format'
    },
    {
        'name': 'unreachable_url',
        'url': 'https://example.com/non-existent-page-12345',
        'expected_error': 'Exception',
        'error_message': 'HTTP error occurred'
    }
]

# Slug validation test cases
SLUG_VALIDATION_CASES = [
    # Valid slugs
    {
        'slug': 'react-hooks-tutorial',
        'is_valid': True,
        'reason': 'Perfect length and format'
    },
    {
        'slug': 'javascript-best-practices-guide',
        'is_valid': True,
        'reason': 'Good length, descriptive'
    },
    {
        'slug': 'machine-learning-python-beginners',
        'is_valid': True,
        'reason': 'Within length limits'
    },
    
    # Invalid slugs
    {
        'slug': 'a-b',
        'is_valid': False,
        'reason': 'Too short'
    },
    {
        'slug': 'the-complete-comprehensive-ultimate-beginner-guide-to-advanced-machine-learning-with-tensorflow',
        'is_valid': False,
        'reason': 'Too long'
    },
    {
        'slug': 'react hooks guide',
        'is_valid': False,
        'reason': 'Contains spaces'
    },
    {
        'slug': 'API_Design_Guide',
        'is_valid': False,
        'reason': 'Contains uppercase and underscores'
    },
    {
        'slug': 'react-&-vue-comparison',
        'is_valid': False,
        'reason': 'Contains special characters'
    }
]

# OpenAI API mock responses
MOCK_OPENAI_RESPONSES = {
    'jojo_maman_bebe': 'jojo-maman-bebe-uk-childrens-clothing-guide',
    'doll_clothing': 'japanese-doll-clothing-shopping-guide',
    'kindle_guide': 'kindle-ereader-buying-guide-comparison',
    'generic_tutorial': 'deploy-react-apps-aws-s3',
    'rate_limit_error': 'Rate limit exceeded',
    'api_error': 'API request failed'
}