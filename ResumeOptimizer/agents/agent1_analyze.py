import json
import requests
from typing import Dict, Any
from api.client_factory import APIClientFactory
from utils.config_manager import ConfigManager
from utils.prompt_filter import PromptFilter
from utils.file_parser import FileParser
import logging

logger = logging.getLogger(__name__)

class Agent1Analyze:
    def __init__(self):
        self.config = ConfigManager()
        self.agent_config = self.config.get_agent_config('agent1_analyze')

    def process(self, resume_data: Dict[str, Any], user_intent: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Agent1: 开始分析简历和搜索行业信息")

        parsed_resume = self._parse_resume(resume_data)

        industry_info = self._search_industry(user_intent)

        combined = self._analyze_with_api(parsed_resume, user_intent, industry_info)

        logger.info("Agent1: 分析完成")
        return combined

    def _parse_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        if 'file_path' in resume_data:
            try:
                parsed = FileParser.parse_resume(resume_data['file_path'])
                return {"raw_text": parsed.get('text', ''), "tables": parsed.get('tables', [])}
            except Exception as e:
                logger.warning(f"文件解析失败: {e}")
                return {"raw_text": "", "tables": []}
        elif 'markdown_text' in resume_data:
            from utils.markdown_parser import MarkdownParser
            return MarkdownParser.parse(resume_data['markdown_text'])
        return resume_data

    def _search_industry(self, user_intent: Dict[str, Any]) -> Dict[str, Any]:
        industry = user_intent.get('industry', '')
        position = user_intent.get('position', '')
        if not industry and not position:
            return {"industry_trends": [], "resume_keywords": []}

        try:
            query = f"{industry} {position} 招聘 要求 薪资"
            url = "https://api.duckduckgo.com/"
            params = {'q': query, 'format': 'json', 'no_redirect': 1}
            resp = requests.get(url, params=params, timeout=10)
            data = resp.json()
            results = []
            for topic in data.get('RelatedTopics', [])[:5]:
                if 'Text' in topic:
                    results.append(topic['Text'])
            search_text = '\n'.join(results) if results else ""
        except Exception:
            search_text = ""

        return {"search_results": search_text, "industry": industry, "position": position}

    def _analyze_with_api(self, parsed_resume: Dict, user_intent: Dict, industry_info: Dict) -> Dict[str, Any]:
        resume_text = parsed_resume.get('raw_text', '') if isinstance(parsed_resume, dict) else str(parsed_resume)
        search_text = industry_info.get('search_results', '')

        system_prompt = """你是简历分析专家。请分析简历并搜索行业信息，输出JSON：
{
  "personal_info": {"姓名": "", "性别": "", "年龄": "", "联系电话": "", "电子邮箱": "", "所在城市": "", "求职意向": "", "工作年限": "", "最高学历": "", "毕业院校": "", "专业": ""},
  "education": [{"学校名称": "", "学历学位": "", "专业": "", "起止时间": ""}],
  "experience": [{"公司名称": "", "职位名称": "", "在职时间": "", "工作描述": "", "关键成就": ""}],
  "projects": [{"项目名称": "", "项目时间": "", "项目描述": "", "个人职责": "", "技术栈": ""}],
  "skills": {"专业技能": [], "语言能力": [], "证书认证": []},
  "industry_trends": ["趋势1"],
  "resume_keywords": ["关键词1"],
  "basic_score": 75,
  "strengths": [],
  "weaknesses": []
}
要求：1.中文标签 2.禁止编造 3.保留原文措辞"""

        user_content = f"简历内容：\n{resume_text}\n\n求职意向：{json.dumps(user_intent, ensure_ascii=False)}"
        if search_text:
            user_content += f"\n\n行业搜索结果：\n{search_text}"

        try:
            client = self._create_client()
            response = client.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ])
            filtered = PromptFilter.validate_json_output(response)
            if filtered.get('valid'):
                result = filtered['data']
            else:
                result = self._default_result()
        except Exception as e:
            logger.error(f"Agent1 API调用失败: {e}")
            result = self._default_result()
            result['error'] = str(e)

        if isinstance(parsed_resume, dict) and 'raw_text' in parsed_resume:
            result['raw_text'] = parsed_resume['raw_text']
        return result

    def _create_client(self):
        return APIClientFactory.create_client(
            provider=self.agent_config.get('provider', 'siliconflow'),
            api_key=self.agent_config.get('api_key', ''),
            api_base=self.agent_config.get('api_base'),
            model=self.agent_config.get('model')
        )

    def _default_result(self) -> Dict[str, Any]:
        return {
            "personal_info": {"姓名": "未知"},
            "education": [], "experience": [], "projects": [],
            "skills": {"专业技能": [], "语言能力": [], "证书认证": []},
            "industry_trends": [], "resume_keywords": [],
            "basic_score": 0, "strengths": [], "weaknesses": []
        }
