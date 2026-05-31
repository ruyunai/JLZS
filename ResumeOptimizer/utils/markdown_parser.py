import re
from typing import Dict, Any, List

class MarkdownParser:
    SECTION_PATTERNS = {
        '基本信息': r'#\s*基本信息',
        '求职意向': r'#\s*求职意向',
        '工作经历': r'#\s*工作经历',
        '项目经验': r'#\s*项目经验',
        '教育背景': r'#\s*教育[背景经历]',
        '技能证书': r'#\s*技能[证书]?',
        '自我评价': r'#\s*自我评价',
    }

    @staticmethod
    def parse(markdown_text: str) -> Dict[str, Any]:
        sections = {}
        lines = markdown_text.strip().split('\n')
        current_section = None
        current_content = []

        for line in lines:
            matched = False
            for section_name, pattern in MarkdownParser.SECTION_PATTERNS.items():
                if re.match(pattern, line):
                    if current_section and current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = section_name
                    current_content = []
                    matched = True
                    break

            if not matched:
                current_content.append(line)

        if current_section and current_content:
            sections[current_section] = '\n'.join(current_content)

        return MarkdownParser._extract_fields(sections)

    @staticmethod
    def _extract_fields(sections: Dict[str, str]) -> Dict[str, Any]:
        result = {
            'personal_info': {},
            'intent': {},
            'experience': [],
            'projects': [],
            'education': [],
            'skills': {
                '专业技能': [],
                '语言能力': [],
                '证书认证': []
            },
            'summary': {
                '自我评价': '',
                '职业优势': '',
                '求职定位': ''
            }
        }

        if '基本信息' in sections:
            result['personal_info'] = MarkdownParser._parse_basic_info(sections['基本信息'])

        if '求职意向' in sections:
            result['intent'] = MarkdownParser._parse_intent(sections['求职意向'])

        if '工作经历' in sections:
            result['experience'] = MarkdownParser._parse_experience(sections['工作经历'])

        if '项目经验' in sections:
            result['projects'] = MarkdownParser._parse_projects(sections['项目经验'])

        if '教育背景' in sections:
            result['education'] = MarkdownParser._parse_education(sections['教育背景'])

        if '技能证书' in sections:
            skills_data = MarkdownParser._parse_skills(sections['技能证书'])
            if isinstance(skills_data, dict):
                result['skills'] = skills_data
            else:
                result['skills']['专业技能'] = skills_data

        if '自我评价' in sections:
            result['summary']['自我评价'] = sections['自我评价'].strip()

        return result

    @staticmethod
    def _parse_basic_info(text: str) -> Dict[str, str]:
        info = {}
        patterns = {
            '姓名': r'姓名[:：]\s*(.+)',
            '性别': r'性别[:：]\s*(.+)',
            '年龄': r'年龄[:：]\s*(.+)',
            '联系电话': r'电话[:：]\s*(.+)',
            '电子邮箱': r'邮箱[:：]\s*(.+)',
            '所在城市': r'城市[:：]\s*(.+)',
            '求职意向': r'求职意向[:：]\s*(.+)',
            '工作年限': r'工作年限[:：]\s*(.+)',
            '最高学历': r'学历[:：]\s*(.+)',
            '毕业院校': r'学校[:：]\s*(.+)',
            '专业': r'专业[:：]\s*(.+)',
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                info[key] = match.group(1).strip()
        return info

    @staticmethod
    def _parse_intent(text: str) -> Dict[str, str]:
        intent = {}
        patterns = {
            '行业': r'行业[:：]\s*(.+)',
            '岗位': r'岗位[:：]\s*(.+)',
            '薪资': r'薪资[:：]\s*(.+)',
        }
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                intent[key] = match.group(1).strip()
        return intent

    @staticmethod
    def _parse_experience(text: str) -> List[Dict[str, str]]:
        experiences = []
        blocks = re.split(r'##\s+', text)
        for block in blocks[1:]:
            lines = block.strip().split('\n')
            if lines:
                header_match = re.match(r'(.+?)\s*\|\s*(.+?)\s*\|\s*(.+)', lines[0])
                if header_match:
                    experiences.append({
                        '公司名称': header_match.group(1).strip(),
                        '职位名称': header_match.group(2).strip(),
                        '在职时间': header_match.group(3).strip(),
                        '工作描述': '\n'.join(lines[1:]).strip()
                    })
                else:
                    experiences.append({
                        '公司名称': lines[0].strip(),
                        '职位名称': '',
                        '在职时间': '',
                        '工作描述': '\n'.join(lines[1:]).strip()
                    })
        return experiences

    @staticmethod
    def _parse_projects(text: str) -> List[Dict[str, str]]:
        projects = []
        blocks = re.split(r'##\s+', text)
        for block in blocks[1:]:
            lines = block.strip().split('\n')
            if lines:
                header_match = re.match(r'(.+?)\s*\|\s*(.+)', lines[0])
                if header_match:
                    projects.append({
                        '项目名称': header_match.group(1).strip(),
                        '项目时间': header_match.group(2).strip(),
                        '项目描述': '\n'.join(lines[1:]).strip()
                    })
                else:
                    projects.append({
                        '项目名称': lines[0].strip(),
                        '项目时间': '',
                        '项目描述': '\n'.join(lines[1:]).strip()
                    })
        return projects

    @staticmethod
    def _parse_education(text: str) -> List[Dict[str, str]]:
        education = []
        blocks = re.split(r'##\s+', text)
        for block in blocks[1:]:
            lines = block.strip().split('\n')
            if lines:
                header_match = re.match(r'(.+?)\s*\|\s*(.+?)\s*\|\s*(.+)', lines[0])
                if header_match:
                    education.append({
                        '学校名称': header_match.group(1).strip(),
                        '学历学位': header_match.group(2).strip(),
                        '专业': header_match.group(3).strip(),
                        '起止时间': ''
                    })
                else:
                    education.append({
                        '学校名称': lines[0].strip(),
                        '学历学位': '',
                        '专业': '',
                        '起止时间': ''
                    })
        return education

    @staticmethod
    def _parse_skills(text: str) -> Dict[str, List]:
        skills = {
            '专业技能': [],
            '语言能力': [],
            '证书认证': []
        }

        current_category = '专业技能'
        for line in text.strip().split('\n'):
            line = line.strip()
            if '语言' in line.lower():
                current_category = '语言能力'
            elif '证书' in line:
                current_category = '证书认证'

            if line.startswith('-') or line.startswith('*'):
                skill_text = line[1:].strip()
                skills[current_category].append(skill_text)
            elif line.startswith('#'):
                continue
            elif line:
                skills[current_category].extend([s.strip() for s in line.split('、') if s.strip()])

        return skills
