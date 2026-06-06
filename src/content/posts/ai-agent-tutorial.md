---
title: "AI Agent 实战：构建你的第一个智能助手"
published: 2026-05-28
description: "从零开始构建一个基于 LLM 的 AI Agent，涵盖工具调用、记忆系统和规划能力的实现细节。"
image: ""
tags: [AI, Agent, LLM, 自动化]
category: 人工智能
draft: false
---

## AI Agent 是什么？

AI Agent 是能够自主感知环境、做出决策并执行动作的智能体。与传统聊天机器人不同，Agent 具备：

- **工具使用** — 调用外部 API 和工具
- **记忆能力** — 保持上下文和历史信息
- **规划推理** — 将复杂任务分解为步骤
- **自主决策** — 根据反馈调整行动策略

## 架构设计

一个完整的 AI Agent 系统包含以下核心组件：

```
┌─────────────────────────────────────────┐
│              AI Agent                   │
│                                         │
│  ┌───────────┐    ┌──────────────────┐ │
│  │   LLM     │◄──►│  Planner         │ │
│  │  (Brain)  │    │  (任务规划)       │ │
│  └─────┬─────┘    └──────────────────┘ │
│        │                                │
│  ┌─────▼─────┐    ┌──────────────────┐ │
│  │  Memory   │    │  Tool Registry   │ │
│  │  (记忆)   │    │  (工具注册)       │ │
│  └───────────┘    └────────┬─────────┘ │
│                            │            │
└────────────────────────────┼────────────┘
                             │
              ┌──────────────▼──────────────┐
              │        External Tools       │
              │  ┌─────┐ ┌─────┐ ┌──────┐ │
              │  │ Web │ │ DB  │ │ Code │ │
              │  │Search│ │Query│ │ Exec │ │
              │  └─────┘ └─────┘ └──────┘ │
              └────────────────────────────┘
```

## 核心实现

### 1. 工具调用

```python
from pydantic import BaseModel
from typing import Callable, Any
import json

class Tool(BaseModel):
    name: str
    description: str
    func: Callable
    parameters: dict

    def execute(self, **kwargs) -> Any:
        return self.func(**kwargs)

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool):
        self._tools[tool.name] = tool

    def get_tool_descriptions(self) -> str:
        descriptions = []
        for tool in self._tools.values():
            descriptions.append(
                f"- {tool.name}: {tool.description}\n"
                f"  Parameters: {json.dumps(tool.parameters)}"
            )
        return "\n".join(descriptions)

    def execute(self, tool_name: str, **kwargs) -> Any:
        tool = self._tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        return tool.execute(**kwargs)
```

### 2. 记忆系统

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Message:
    role: str  # "user" | "assistant" | "system" | "tool"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

class ConversationMemory:
    def __init__(self, max_messages: int = 50):
        self.messages: list[Message] = []
        self.max_messages = max_messages

    def add(self, role: str, content: str):
        self.messages.append(Message(role=role, content=content))
        # 保留最近的消息
        if len(self.messages) > self.max_messages:
            self.messages = self.messages[-self.max_messages:]

    def get_context(self) -> list[dict]:
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def summarize(self) -> str:
        """生成对话摘要，用于长对话场景"""
        # 可以调用 LLM 生成摘要
        return f"Conversation with {len(self.messages)} messages"
```

### 3. Agent 主循环

```python
class Agent:
    def __init__(self, llm_client, tool_registry: ToolRegistry, memory: ConversationMemory):
        self.llm = llm_client
        self.tools = tool_registry
        self.memory = memory

    async def run(self, user_input: str) -> str:
        self.memory.add("user", user_input)

        while True:
            # 构建提示词
            system_prompt = f"""你是一个智能助手，可以使用以下工具：
{self.tools.get_tool_descriptions()}

请根据用户的需求选择合适的工具，或直接回答问题。
如果需要使用工具，请输出 JSON 格式的工具调用。"""

            messages = [
                {"role": "system", "content": system_prompt},
                *self.memory.get_context()
            ]

            # 调用 LLM
            response = await self.llm.chat(messages)
            self.memory.add("assistant", response)

            # 解析是否需要工具调用
            tool_call = self._parse_tool_call(response)
            if tool_call:
                result = self.tools.execute(**tool_call)
                self.memory.add("tool", str(result))
                continue  # 继续循环，让 LLM 处理工具结果
            else:
                return response  # 无工具调用，返回最终回复
```

## 最佳实践

1. **工具设计要单一** — 每个工具做好一件事
2. **提供清晰的描述** — LLM 依赖描述选择工具
3. **添加安全检查** — 限制危险操作
4. **实现重试机制** — 处理工具调用失败
5. **记录执行日志** — 便于调试和优化

> AI Agent 是 LLM 从"对话"走向"行动"的关键一步。未来，每个开发者都会构建自己的 Agent。
