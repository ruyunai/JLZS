import re
from typing import List, Dict, Any

class PromptFilter:
    SUSPICIOUS_PATTERNS = [
        r'\d{4}-\d{4}(?=.*?(领导|创立|成立))',
        r'精通.{0,2}及.{0,2}等\d+种',
        r'负责.{0,5}公司.{0,5}全面.{0,5}管理',
        r'带领.{0,5}\d+人.{0,5}团队',
        r'年薪\d+万',
    ]

    FILTER_KEYWORDS = [
        '新闻', '广告', '推广', 'Sponsored', 'Advertisement',
        '点击这里', '了解更多', '立即购买', '限时优惠',
        '恭喜', '中奖', '获奖通知', '活动规则'
    ]

    @staticmethod
    def filter_user_input(text: str) -> str:
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
        text = re.sub(r'http[s]?://\S+', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def filter_search_results(text: str) -> str:
        for keyword in PromptFilter.FILTER_KEYWORDS:
            text = re.sub(rf'{re.escape(keyword)}.*?(?=\n|$)', '', text, flags=re.IGNORECASE)
        return text.strip()

    @staticmethod
    def check_suspicious_content(text: str) -> Dict[str, Any]:
        suspicious_found = []
        for pattern in PromptFilter.SUSPICIOUS_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                suspicious_found.append({
                    'pattern': pattern,
                    'matches': matches
                })

        return {
            'has_suspicious': len(suspicious_found) > 0,
            'details': suspicious_found
        }

    @staticmethod
    def validate_json_output(text: str) -> Dict[str, Any]:
        text = text.strip()
        if text.startswith('```json'):
            text = text[7:]
        if text.endswith('```'):
            text = text[:-3]
        text = text.strip()

        try:
            import json
            json_obj = json.loads(text)
            return {'valid': True, 'data': json_obj}
        except json.JSONDecodeError as e:
            return {'valid': False, 'error': str(e), 'raw_text': text}

    @staticmethod
    def sanitize_prompt(prompt: str, max_length: int = 8000) -> str:
        prompt = PromptFilter.filter_user_input(prompt)
        if len(prompt) > max_length:
            prompt = prompt[:max_length] + '...'
        return prompt
