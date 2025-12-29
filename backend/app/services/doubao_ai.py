import requests
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DoubaoService:
    def __init__(self):
        # ================= 配置区域 =================
        # 1. 你的 API Key
        self.api_key = "28a77d37-c75b-46e6-a56f-c16bc6d45610"
        
        # 2. 你的 Model ID (之前验证成功的那个)
        self.model = "doubao-seed-1-6-251015"
        
        # 3. 火山引擎 API 地址
        self.api_url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        # ===========================================

    def generate_learning_path(self, student_profile: dict, weak_points: list):
        # 构造 Prompt
        prompt = f"""
        你是一位资深的教育专家系统。
        学生信息：姓名 {student_profile.get('name')}，{student_profile.get('grade')}年级。
        薄弱点：{', '.join(weak_points)}。
        
        请根据“最近发展区”理论，生成个性化学习路径。
        【重要】必须严格返回纯 JSON 格式，不要包含 Markdown 标记（如 ```json）。
        返回格式如下：
        {{
            "logic_reasoning": "简短的诊断分析（50字以内）",
            "recommended_steps": ["第一步行动", "第二步行动", "第三步行动", "第四步行动"]
        }}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 构造请求体
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "你是一个只输出 JSON 的教育专家助手。"
                },
                {
                    "role": "user", 
                    "content": prompt 
                }
            ],
            "temperature": 0.7,
            "max_tokens": 4096 
        }

        try:
            logger.info(f"正在调用豆包模型: {self.model} ...")
            
            # 发送请求
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            
            if response.status_code != 200:
                logger.error(f"API 调用失败: {response.text}")
                return self._get_fallback_data(f"API 报错: {response.status_code}")

            result = response.json()
            
            if 'choices' not in result or not result['choices']:
                return self._get_fallback_data("API 返回内容为空")

            content = result['choices'][0]['message']['content']
            logger.info(f"AI 返回原始内容: {content}")
            
            # 清洗数据
            clean_content = content.replace("```json", "").replace("```", "").strip()
            
            try:
                return json.loads(clean_content)
            except json.JSONDecodeError:
                return {
                    "logic_reasoning": content[:100] + "...",
                    "recommended_steps": ["AI 返回格式非标准，请查看诊断分析"]
                }

        except Exception as e:
            logger.error(f"系统内部错误: {str(e)}")
            return self._get_fallback_data(f"系统连接错误: {str(e)}")

    def _get_fallback_data(self, reason):
        return {
            "logic_reasoning": f"【系统提示】{reason}。显示离线建议。",
            "recommended_steps": ["检查网络连接", "确认 Model ID 正确"]
        }

# 【关键点】这里实例化了 ai_agent，这就是报错说找不到的东西
ai_agent = DoubaoService()