import json
import os
from typing import Optional

from openai import OpenAI

from tools import read_resume_text, run_command


class ResumeAgent:
    def __init__(self) -> None:
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        api_key = os.getenv("OPENAI_API_KEY")
        self.client: Optional[OpenAI] = OpenAI(api_key=api_key) if api_key else None

    def ask(self, prompt: str, latest_resume: Optional[str] = None) -> str:
        if not self.client:
            return self._fallback(prompt, latest_resume)

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "read_resume",
                    "description": "Read a resume from a local file path or an s3 uri.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "Local path or s3 uri for the resume",
                            }
                        },
                        "required": ["location"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "run_command",
                    "description": "Run a local CLI command for the demo app.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "The command to run",
                            }
                        },
                        "required": ["command"],
                    },
                },
            },
        ]

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an AI agent. Read uploaded files and execute commands when needed. "
                    "Answer concisely."
                ),
            },
            {
                "role": "user",
                "content": prompt if latest_resume else f"{prompt}\nNo file has been uploaded yet.",
            },
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )

        message = response.choices[0].message
        if not message.tool_calls:
            return message.content or "No response returned."

        tool_outputs = []
        for tool_call in message.tool_calls:
            name = tool_call.function.name
            arguments = json.loads(tool_call.function.arguments)

            if name == "read_resume":
                location = arguments.get("location") or latest_resume or ""
                result = read_resume_text(location)
            elif name == "run_command":
                command = arguments.get("command", "")
                result = run_command(command)
            else:
                result = f"Unknown tool: {name}"

            tool_outputs.append({"tool": name, "result": result})

        return json.dumps(tool_outputs, indent=2, default=str)

    def _fallback(self, prompt: str, latest_resume: Optional[str] = None) -> str:
        lowered = prompt.lower()

        if "resume" in lowered or "summarize" in lowered:
            if not latest_resume:
                return "No file has been uploaded yet."
            text = read_resume_text(latest_resume)
            snippet = text[:1500]
            return f"File content:\n\n{snippet}"

        if lowered.startswith("run ") or lowered.startswith("execute "):
            command = prompt.split(" ", 1)[1]
            result = run_command(command)
            return json.dumps(result, indent=2)

        return (
            "The AI agent is ready."
        )
