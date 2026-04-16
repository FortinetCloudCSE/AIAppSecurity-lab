import json
import logging
import os
from typing import Optional

from openai import OpenAI

from tools import fetch_aws_account_info, get_all_resume_contents, read_resume_text, sync_resumes_from_bucket

logger = logging.getLogger(__name__)
PROMPT_COLOR = "\033[96m"
COLOR_RESET = "\033[0m"


class ResumeAgent:
    def __init__(self) -> None:
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        self.client: Optional[OpenAI] = OpenAI(api_key=api_key) if api_key else None
        self.max_iterations = 5
        self.user_request = ""
        self.previous_output = "None"
        self.latest_resume: Optional[str] = None
        self.golden_color = "\033[38;2;255;215;0m"
        self.reset_color = "\033[0m"

    def ask(self, prompt: str, latest_resume: Optional[str] = None) -> str:
        logger.info(
            "agent_ask start prompt=%s%r%s latest_resume=%s has_openai=%s",
            PROMPT_COLOR,
            prompt,
            COLOR_RESET,
            latest_resume,
            bool(self.client),
        )
        if not self.client:
            logger.info("agent_ask using_fallback prompt=%s%r%s", PROMPT_COLOR, prompt, COLOR_RESET)
            return self._fallback(prompt, latest_resume)

        self.user_request = prompt
        self.previous_output = "None"
        self.latest_resume = latest_resume
        return self.run()

    def _fallback(self, prompt: str, latest_resume: Optional[str] = None) -> str:
        lowered = prompt.lower()

        if "read all resumes" in lowered or "read the resumes" in lowered:
            resumes = get_all_resume_contents()
            if not resumes:
                return "I don't have any resumes stored currently. If you provide or upload a resume file, I can read and analyze it for you."

            contents = []
            for resume in resumes[:5]:
                contents.append(f"{resume['location']}:\n{resume['content'][:1500]}")
            return "\n\n".join(contents)

        if "resume" in lowered and any(
            phrase in lowered for phrase in {"do you have", "what resumes", "list", "available"}
        ):
            resumes = sync_resumes_from_bucket()
            if not resumes:
                return "I don't have any resumes stored currently. If you provide or upload a resume file, I can read and analyze it for you."
            return "Available resumes:\n\n" + "\n".join(f"- {resume}" for resume in resumes)

        if "resume" in lowered or "summarize" in lowered:
            if not latest_resume:
                return "No file has been uploaded yet."
            text = read_resume_text(latest_resume)
            snippet = text[:1500]
            return f"File content:\n\n{snippet}"

        if any(token in lowered for token in {"aws", "account", "iam", "ec2", "s3", "sts", "vpc"}):
            return self.agent_get_aws_data(prompt)

        return (
            "The AI agent is ready. But there is an issue!"
        )

    def call_llm(self, system_message: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
        )
        return (response.choices[0].message.content or "").strip()

    def agent_get_aws_data(self, prompt: str) -> str:
        system_message = (
            "You are an assistant that helps getting information from AWS by executing AWS commands. "
            "But respond only with a command, nothing else. example: \"aws ec2 describe-instances\""
        )
        command = self.call_llm(system_message, prompt)
        logger.info("AWS Command:%s %s %s", self.golden_color, command, self.reset_color)
        result = fetch_aws_account_info(command)
        logger.info("agent_step_result action=agent_get_aws_data command=%r result=%s", command, json.dumps(result, default=str))
        output = result.get("stdout") or result.get("stderr") or ""
        return output.strip()

    def agent_get_resumes(self, prompt: str) -> str:
        resume_files = sync_resumes_from_bucket()
        resume_contents = get_all_resume_contents()
        logger.info("agent_step_result action=agent_get_resumes file_count=%s", len(resume_files))
        formatted_resumes = []
        for resume in resume_contents:
            formatted_resumes.append(f"{resume['location']}:\n{resume['content']}")

        return "\n\n".join(formatted_resumes).strip()

    def agent_finalize_results(self, prompt: str) -> str:
        system_message = (
            f"You are a task assistant that helps answer the user request: '{self.user_request}' "
            f"based on the output from a previous step: '{self.previous_output}'"
        )
        result = self.call_llm(system_message, prompt)
        return result or self._fallback(self.user_request, self.latest_resume)

    def decide_next_step(self, thought: str) -> str:
        system_message = (
            "You need to decide the next step (task) to be taken. Based on the context"
            "Your strict options: 'agent_get_aws_data', 'agent_get_resumes', 'agent_finalize_results'. "
            "Your response should be only one of those options. Nothing else. "
            "If you think you have enough information to obtain good results respond with 'agent_finalize_results'. "
            "If it is about resumes or candidates use 'agent_get_resumes'. "
            "If it is AWS related use 'agent_get_aws_data'."
        )
        user_prompt = f"Based on the thought: '{thought}', which task should be performed next?"
        content = self.call_llm(system_message, user_prompt)
        logger.info("agent_decision_raw content=%r", content)

        if content not in {"agent_get_resumes", "agent_get_aws_data", "agent_finalize_results"}:
            logger.warning("agent_decision_invalid content=%r", content)
            return "agent_finalize_results"

        return content

    def run(self) -> str:
        prompt = ""
        for iteration in range(self.max_iterations):
            prompt = f"Thought #{iteration + 1}: {self.user_request} with previous output '{self.previous_output}'"
            next_step = self.decide_next_step(prompt)
            logger.info(
                "%sllm_decision - Next step(%s): %s%s",
                self.golden_color,
                iteration + 1,
                next_step,
                self.reset_color,
            )

            if next_step == "agent_get_aws_data":
                result = self.agent_get_aws_data(prompt)
                self.previous_output = result or "None"
            elif next_step == "agent_get_resumes":
                result = self.agent_get_resumes(prompt)
                self.previous_output = result or "None"
            elif next_step == "agent_finalize_results":
                result = self.agent_finalize_results(prompt)
                logger.info("result: %s", result[:1000])
                return result

        result = self.agent_finalize_results(prompt)
        logger.info("result: %s", result[:1000])
        return result
