from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class ResumeWorkflow:
    def __init__(self, agent1, agent2):
        self.agent1 = agent1
        self.agent2 = agent2

    def run(self, resume_data: dict, user_intent: dict) -> dict:
        logger.info("Workflow: 开始执行")

        analyzed = self.agent1.process(resume_data, user_intent)

        optimized = self.agent2.process(analyzed, user_intent)

        logger.info("Workflow: 执行完成")
        return optimized
