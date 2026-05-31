import json
from typing import Dict, Any
from api.client_factory import APIClientFactory
from utils.config_manager import ConfigManager
from utils.prompt_filter import PromptFilter
import logging

logger = logging.getLogger(__name__)

class Agent2Optimize:
    def __init__(self):
        self.config = ConfigManager()
        self.agent_config = self.config.get_agent_config('agent2_optimize')

    def process(self, resume_data: Dict[str, Any], user_intent: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Agent2: 开始优化简历")
        result = self._optimize_with_api(resume_data, user_intent)
        logger.info("Agent2: 优化完成")
        return result

    def _optimize_with_api(self, resume_data: Dict, user_intent: Dict) -> Dict[str, Any]:
        system_prompt = """你是资深简历优化专家和温暖的职业导师。请完成以下所有任务，输出一个完整JSON：

{
  "personal_info": {"姓名": "", "性别": "", "年龄": "", "联系电话": "", "电子邮箱": "", "所在城市": "", "求职意向": "", "工作年限": "", "最高学历": "", "毕业院校": "", "专业": ""},
  "career_summary": "2-3句职业概述",
  "education": [{"学校名称": "", "学历学位": "", "专业": "", "起止时间": ""}],
  "experience": [{"公司名称": "", "职位名称": "", "在职时间": "", "工作描述": ["描述1"], "关键成果": ""}],
  "projects": [{"项目名称": "", "项目时间": "", "项目描述": "", "个人职责": "", "技术栈": "", "项目成果": ""}],
  "skills": {"专业技能": [{"技能名称": "", "熟练度": ""}], "语言能力": [{"语言": "", "水平": ""}], "证书认证": []},
  "industry_analysis": "对该行业当前形势和未来趋势的简要分析（2-3句）",
  "competitiveness": {"overall_score": 70, "analysis": "竞争力分析：你的优势在哪、不足在哪"},
  "career_suggestions": {"就业方向": ["方向1"], "补充技能": ["技能1"], "短期行动": ["行动1"]},
  "humanized_message": "给求职者的温暖鼓励寄语（80-150字），要真诚有感染力，肯定TA的努力，鼓励TA继续前进"
}

必须遵守：
1. 所有标签和内容使用中文
2. 禁止编造不存在的经历
3. 量化成果（如提升效率40%）
4. industry_analysis必须分析行业形势
5. competitiveness必须给出分数和分析
6. career_suggestions必须给出具体建议
7. humanized_message必须温暖真诚，不能敷衍"""

        user_content = f"原始简历：\n{json.dumps(resume_data, ensure_ascii=False)}\n\n求职意向：\n{json.dumps(user_intent, ensure_ascii=False)}"

        try:
            client = self._create_client()
            response = client.chat([
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ])
            filtered = PromptFilter.validate_json_output(response)
            if filtered.get('valid'):
                return filtered['data']
        except Exception as e:
            logger.error(f"Agent2 优化失败: {e}")

        return self._default_result()

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
            "career_summary": "",
            "education": [], "experience": [], "projects": [],
            "skills": {"专业技能": [], "语言能力": [], "证书认证": []},
            "industry_analysis": "",
            "competitiveness": {"overall_score": 0, "analysis": ""},
            "career_suggestions": {"就业方向": [], "补充技能": [], "短期行动": []},
            "humanized_message": ""
        }
