from __future__ import annotations
from typing import Optional
from nexura.models.schemas import ScanPlan, ToolCommand, ToolType
from nexura.ai_engine import AIEngine, SYSTEM_PROMPT


class ToolSelector:
    def __init__(self, engine: AIEngine):
        self.engine = engine

    def create_plan(self, prompt: str, target: Optional[str] = None) -> ScanPlan:
        user_prompt = f"User request: {prompt}"
        if target:
            user_prompt += f"\nTarget (forced by user): {target}"

        try:
            data = self.engine.ask_structured(SYSTEM_PROMPT, user_prompt)
        except (RuntimeError, ValueError) as e:
            return self._fallback_plan(prompt, target, str(e))

        scan_target = data.get("target", target or "unknown")
        intent = data.get("intent", prompt)
        reasoning = data.get("reasoning", "")
        tools_raw = data.get("tools", [])

        tools = []
        for t in tools_raw:
            tool_name = t.get("tool", "").lower()
            try:
                tool_type = ToolType(tool_name)
            except ValueError:
                continue
            args = [a.replace("<target>", scan_target) for a in t.get("args", [])]
            tools.append(ToolCommand(
                tool=tool_type,
                args=args,
                description=t.get("description", ""),
            ))

        return ScanPlan(
            target=scan_target,
            intent=intent,
            tools=tools,
            reasoning=reasoning,
        )

    def _fallback_plan(self, prompt: str, target: str | None, reason: str) -> ScanPlan:
        tgt = target or "unknown"
        return ScanPlan(
            target=tgt,
            intent=prompt,
            tools=[
                ToolCommand(
                    tool=ToolType.NMAP,
                    args=["-sV", "-sC", "-p", "22,80,443,8080", tgt],
                    description="Umumiy port va service skanerlash",
                ),
                ToolCommand(
                    tool=ToolType.NUCLEI,
                    args=["-severity", "critical,high,medium", tgt],
                    description="Zaifliklarni aniqlash",
                ),
            ],
            reasoning=f"AI mavjud emas ({reason}). Standart skaner rejimi.",
        )
