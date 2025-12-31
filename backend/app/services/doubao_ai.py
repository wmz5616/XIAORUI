import requests
import json
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoubaoService:
    def __init__(self):
        self.api_key = "28a77d37-c75b-46e6-a56f-c16bc6d45610"
        self.model = "doubao-seed-1-6-251015"
        self.api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"

    def _call_ai(self, system_prompt, user_prompt, expect_json=True, retry_count=2):
        """
        通用 AI 调用方法，增强了错误处理和重试机制
        :param expect_json: 是否强制解析返回值为 JSON
        :param retry_count: 失败重试次数
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 4096 
        }

        for attempt in range(retry_count + 1):
            try:
                response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
                
                if response.status_code != 200:
                    logger.error(f"API Error (Attempt {attempt+1}): {response.text}")
                    continue
                
                content = response.json()['choices'][0]['message']['content']

                if not expect_json:
                    return content
                
                clean_content = content.replace("```json", "").replace("```", "").strip()
                try:
                    return json.loads(clean_content)
                except json.JSONDecodeError as je:
                    logger.error(f"JSON Parse Failed: {je}. Content: {clean_content}")
                    if attempt == retry_count:
                        return None
                    
            except Exception as e:
                logger.error(f"AI Call Failed (Attempt {attempt+1}): {e}")
                if attempt == retry_count:
                    return None
                time.sleep(1)

        return None

    def generate_learning_path(self, student_profile: dict, weak_points: list):
        system_prompt = "你是一位资深教育专家。请根据学生情况和薄弱点，生成学习路径。必须返回纯 JSON，格式：{'logic_reasoning': '...', 'recommended_steps': ['...']}"
        user_prompt = f"学生：{student_profile}。薄弱点：{weak_points}。"

        fallback_data = {
            "logic_reasoning": "AI 服务暂时繁忙，为您推荐通用学习路径。",
            "recommended_steps": ["复习基础概念", "完成课后习题", "整理错题本"]
        }

        res = self._call_ai(system_prompt, user_prompt, expect_json=True)

        if res and isinstance(res, dict):
            return res
        return fallback_data

    def generate_diagnostic_quiz(self, grade: int, subject: str = "数学"):
        system_prompt = """
        你是一名命题专家。请生成 5 道单选题，用于评估学生的知识水平。
        必须返回纯 JSON 格式，结构如下：
        [
            {"id": 1, "content": "题目", "options": ["A", "B", "C", "D"], "correct_index": 0, "knowledge_point": "考点"}
        ]
        """
        user_prompt = f"请为 {grade} 年级 {subject} 生成一套诊断测试题。"
        
        fallback_data = [
            {"id": 1, "content": "系统繁忙，无法生成题目，请稍后再试。", "options": ["A", "B", "C", "D"], "correct_index": 0, "knowledge_point": "无"}
        ]

        res = self._call_ai(system_prompt, user_prompt, expect_json=True)
        
        if res and isinstance(res, list):
            return res
        return fallback_data

    def analyze_weakness(self, wrong_records: list):
        if not wrong_records: return []
        
        system_prompt = "你是一名学习顾问。请根据错题总结 1-3 个薄弱知识点。必须返回纯 JSON 字符串列表，如 ['函数', '几何']"
        user_prompt = f"错题记录：{json.dumps(wrong_records, ensure_ascii=False)}"
        
        fallback_data = ["综合复习"]

        res = self._call_ai(system_prompt, user_prompt, expect_json=True)
        
        if res and isinstance(res, list):
            return res
        return fallback_data

    def generate_class_report(self, class_data: dict):
        """
        生成班级报告（Markdown 格式），不需要解析 JSON
        """
        system_prompt = """
        你是一位高级教学主管。请根据班级学情数据，生成一份简短的教学分析报告。
        请包含以下三个部分：
        1. 【整体学情】：分析班级整体掌握情况。
        2. 【共性问题】：针对共性薄弱点进行分析。
        3. 【教学建议】：给老师接下来的备课提供 3 条具体建议。
        
        请直接返回格式化的 Markdown 文本。
        """
        user_prompt = f"班级数据如下：{json.dumps(class_data, ensure_ascii=False)}"
    
        res = self._call_ai(system_prompt, user_prompt, expect_json=False)
        
        if res:
            return res
        return "AI分析服务暂时不可用，请稍后重试。"

ai_agent = DoubaoService()