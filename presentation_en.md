# AI Trends 2025-2026: The Age of Agentic AI and the Promise of n8n

> 30-Minute Presentation | IT Team Knowledge Sharing | March 2026

---

## Table of Contents

1. [The Past Year in Review](#1-the-past-year-in-review)
2. [The LLM Race: A Five-Way Battle](#2-the-llm-race-a-five-way-battle)
3. [The Rise and Limits of MCP, and the Native AI Era](#3-the-rise-and-limits-of-mcp-and-the-native-ai-era)
4. [The Return to CLI and Vibe Coding](#4-the-return-to-cli-and-vibe-coding)
5. [From Prompt Engineering to Context Engineering](#5-from-prompt-engineering-to-context-engineering)
6. [Agentic AI Deep Dive: What Is It, Really?](#6-agentic-ai-deep-dive-what-is-it-really)
7. [n8n: A Platform That Makes Agentic AI Real](#7-n8n-a-platform-that-makes-agentic-ai-real)
8. [Conclusion: What We Can Do Right Now](#8-conclusion-what-we-can-do-right-now)

---

## Key Terminology

> A quick glossary of AI/IT terms that appear frequently in this presentation.

| Term | Full Name | Description |
|------|-----------|-------------|
| **LLM** | Large Language Model | Large-scale language AI models like ChatGPT. Trained on massive text data to understand and generate natural language |
| **Agent** | Agent | An AI program that reasons and acts autonomously. Pursues goals without step-by-step human instruction |
| **MCP** | Model Context Protocol | A universal standard for AI to connect with external tools (GitHub, Slack, etc.). Often called "the USB-C of AI" |
| **CLI** | Command Line Interface | A terminal/command-line environment. Operating a computer via text commands instead of a mouse |
| **Token** | Token | The smallest unit AI uses to process text. Roughly 1 English word or 4 characters per token |
| **RAG** | Retrieval Augmented Generation | A technique where AI retrieves external documents to enrich its responses |
| **Workflow** | Workflow | An automated sequence of tasks. A pipeline that runs steps A, B, C in order |
| **Orchestration** | Orchestration | Coordinating multiple AI systems and tools, like a conductor leading an orchestra |

---

## 1. The Past Year in Review

| Date | Event | Significance |
|------|-------|--------------|
| 2024.11 | **MCP** announced (Anthropic) | A universal standard for AI-to-tool connectivity emerges |
| 2025.01 | **DeepSeek R1** released | Open-source shockwave, price war begins |
| 2025.02 | **"Vibe Coding"** coined (Karpathy) | The era of writing code "without even looking at it" |
| 2025.03 | OpenAI **Agents SDK** released | Agent framework competition heats up |
| 2025.04 | Google **A2A Protocol** / Meta **Llama 4** | Agent-to-agent communication standard + open-source leap |
| 2025.05 | **Claude Code** launched | The beginning of CLI-based AI agents |
| 2025.09 | **Notion 3.0** — AI Agents pivot | Major services start embedding their own AI agents |
| 2025.10 | **n8n Series C** $180M (Nvidia participation) | A massive bet on workflow automation + AI convergence |
| 2025.12 | MCP donated to **Linux Foundation** | The standard is established, but the industry is already moving on |
| 2026.01 | **OpenClaw** goes viral (250K stars) | The peak and controversy of vibe coding |
| 2026.02 | **Claude 4.6** / Karpathy: "Vibe coding is already behind us" | The shift to agentic engineering |

**In one line:** AI is evolving from "conversation tool" to "working agent" to "a team that runs systems."

---

## 2. The LLM Race: A Five-Way Battle

### The Big 3 + Open Source + Challengers

| Camp | Key Models | Core Strengths |
|------|-----------|----------------|
| **OpenAI** | GPT-4.1, o3, o4-mini | Reasoning-focused (o-series), 1M tokens, price competitiveness (mini) |
| **Anthropic** | Claude Sonnet/Opus 4.6 | #1 in coding, **30h+ autonomous agent tasks**, agent team capabilities |
| **Google** | Gemini 2.5 Pro | 1M tokens, Deep Think mode, top-tier math and coding |
| **Open Source** | DeepSeek R1, Llama 4 | DeepSeek: price disruption / Llama 4 Scout: **10M tokens** |
| **Challengers** | xAI Grok 3, Mistral | 200K GPU infrastructure (Grok), EU data sovereignty (Mistral) |

### How the Competitive Axis Has Shifted

```
2024: "The model with the highest benchmark scores wins"
         ↓
2025: "How long can it work autonomously?"
         ↓
2026: "How well can it orchestrate a team of agents?"
```

**Four key trends:**
- Every model now ships with a **reasoning (thinking) mode** — it is table stakes
- **Agent capability** (sustained autonomous work) is the new competitive metric
- Across-the-board **price drops** since DeepSeek R1 — the cost barrier is disappearing
- Open-source models are **rapidly closing the gap** with proprietary ones

---

## 3. The Rise and Limits of MCP, and the Native AI Era

### 3-1. What Is MCP? (Quick Summary)

**Model Context Protocol** — a universal standard for AI to connect with external tools

```
Before: AI Model A x GitHub + Slack + DB = custom code for each (M x N)
After:  AI Model A ─┐              ┌── GitHub MCP Server
        AI Model B ─┼── MCP Std ───┼── Slack MCP Server
        AI Model C ─┘              └── DB MCP Server  (M+N)
```

- 2024.11 Anthropic announces MCP → By 2025, OpenAI, Google, and Microsoft all adopt it
- 5,800+ servers, 300+ clients, SDK downloads at 97M per month
- 2025.12 Donated to Linux Foundation → **industry standard confirmed**

### 3-2. But Wait... Is MCP Already Showing Its Age?

Even as MCP solidifies as a standard, **major services are embedding their own AI agents natively**:

| Service | Native AI Integration | MCP Dependency |
|---------|----------------------|----------------|
| **Notion** | Notion 3.0 AI Agents (2025.09) → 3.3 Custom Agents (2026.02) | MCP available, but native is the focus |
| **Linear** | GitHub Copilot Coding Agent native integration (2025.10) | Direct integration without MCP |
| **GitHub** | Copilot CLI + Agent Mode | Native CLI is more efficient than MCP |
| **Slack** | Built-in AI Workflow Builder | Strengthening native automation |

### 3-3. CLI vs MCP: The Efficiency Debate

> "CLI tools are more efficient for AI agents than MCP" — Developer community, early 2026

| Metric | CLI Approach (`gh`, `kubectl`, etc.) | MCP Approach |
|--------|--------------------------------------|-------------|
| Token cost | ~200 tokens | ~55,000 tokens (GitHub MCP with 93 tools) |
| LLM familiarity | Very high (abundant in training data) | Schemas encountered at runtime for the first time |
| Efficiency | **33% advantage** (benchmark) | Excessive context consumption |

### 3-4. Where MCP Stands Today

```
The future of MCP:
├── It is not going away (already a standard)
├── But shifting from "master key" to "one of several approaches"
├── Services are running "dual strategies" — native AI + MCP servers side by side
└── The real winner: the "orchestration layer" that combines all of the above ← ⭐
```

---

## 4. The Return to CLI and Vibe Coding

### 4-1. The Evolution of AI Coding Tools

```
2023  Autocomplete    → GitHub Copilot, Tabnine    "Predict the next line"
2024  Chat-based IDE  → Cursor, Windsurf           "Edit code via conversation"
2025  CLI Agents      → Claude Code, Aider          "Manage entire projects from the terminal"
2026  Team Agents     → Claude Code Teams, n8n      "Multiple agents collaborating"
```

- Claude Code: launched May 2025 → **#1 developer preference (46%) within 8 months**
- 95% of developers use AI tools at least weekly; 75% use AI for more than half their coding

### 4-2. From Vibe Coding to Agentic Engineering

> "Forget that the code even exists, just vibe it." — Karpathy, Feb 2025

**OpenClaw** — the symbol and controversy of vibe coding
- **250K+ GitHub stars** (fastest ever), open-source AI assistant
- Creator: "Ship without reading code" → 2.74x more security vulnerabilities, 75% more config errors
- Feb 2026: Creator joins OpenAI → project transitions to a foundation

> "Vibe coding is already behind us. Now it's **agentic engineering**." — Karpathy, 2026

**Bottom line:** AI writes the code, but humans supervise and orchestrate — that is becoming the standard.

---

## 5. From Prompt Engineering to Context Engineering

> "The new essential skill in AI is not prompting — it's **context engineering**."
> — Tobi Lutke (Shopify CEO)

### What Is the Difference?

| | Prompt Engineering | Context Engineering |
|--|-------------------|---------------------|
| **Scope** | A single text string | The entire information architecture |
| **Timing** | One-shot at invocation | Continuous, across multiple turns |
| **Focus** | "What should I ask?" | "What does the AI already know?" |
| **Outcome** | Better phrasing | Better **system design** |

### The 7 Elements of Context

1. **System Prompt** — The AI's role and rules
2. **User Prompt** — The current task
3. **Conversation History** — Context so far
4. **Long-term Memory** — Persistence across sessions
5. **Retrieved Information (RAG)** — Relevant documents and data
6. **Available Tools** — APIs, MCP, functions
7. **Output Format** — Structured response definitions

**Key insight:** Context engineering is the higher-order discipline of designing *what* information to provide, *when*, in *what format*, and *how much*. MCP, RAG, and Memory are its execution mechanisms.

---

## 6. Agentic AI Deep Dive: What Is It, Really?

### 6-1. One-Sentence Definition

> **Generative AI "answers" questions. Agentic AI "achieves" goals.**

### 6-2. A Simple Analogy: The Restaurant

| | Generative AI (ChatGPT) | Agentic AI |
|--|------------------------|------------|
| **Analogy** | A chef who gives you the recipe | A chef who cooks and serves the meal |
| **Input** | "Give me a pasta recipe" | "Prepare a dinner party" |
| **Output** | Text (the recipe) | **Actions** (shop → cook → set table → serve) |
| **Tools** | None | Fridge, stove, payment system... |
| **Decisions** | Human directs the next step | Decides the next step on its own |

### 6-3. How Agentic AI Works

```
┌──────────────────────────────────────────────────────┐
│                  Agentic AI Loop                     │
│                                                      │
│   ① Receive Goal    "Create a monthly sales report"  │
│        ↓                                             │
│   ② Plan            Query DB → Analyze → Visualize   │
│        ↓             → Write Document                │
│   ③ Execute Tools   Run SQL, generate charts, write  │
│        ↓                                             │
│   ④ Evaluate        "Chart is incomplete? Let me     │
│        ↓             retry."                         │
│   ⑤ Iterate/Done   Repeat ③-④ until resolved → Done │
│                                                      │
│   Key: Steps ②-⑤ are performed autonomously,        │
│        without human intervention                    │
└──────────────────────────────────────────────────────┘
```

### 6-4. Six Core Characteristics

| Trait | Description | Example |
|-------|-------------|---------|
| **Autonomy** | Proceeds toward a goal without step-by-step instructions | "Create a report" — and it handles everything |
| **Multi-step Reasoning** | Formulates and executes complex plans | DB → analysis → visualization → document pipeline |
| **Tool Use** | Accesses APIs, databases, file systems, the web | Sends Slack messages, runs SQL queries |
| **Memory** | Maintains long-term and short-term context | Remembers yesterday's work in today's session |
| **Adaptability** | Revises plans when things fail | API error → tries an alternative path |
| **Goal Orientation** | Repeats the perceive-reason-act loop | Keeps iterating until the result is satisfactory |

### 6-5. The Evolution of AI

```
Gen 1  Rule-based Chatbots    "FAQ matching" (~2022)
  ↓
Gen 2  Generative AI          "Ask a question, get an answer" (2023, ChatGPT)
  ↓
Gen 3  Copilots               "Suggests alongside you" (2024, Copilot)
  ↓
Gen 4  Single Agents          "Works independently" (2025, Claude Code)
  ↓
Gen 5  Multi-Agent Systems    "Collaborates as a team" (2026, Agent Teams)
```

### 6-6. Single Agent vs Multi-Agent

```
[Single Agent]                     [Multi-Agent System]

   ┌──────────┐                      ┌──────────────┐
   │ Jack of  │                      │ Orchestrator │
   │ all (lim)│                      └──────┬───────┘
   └──────────┘                   ┌─────────┼─────────┐
                             ┌────┴────┐┌───┴────┐┌───┴─────┐
                             │ Coding  ││Research││ Testing  │
                             │ Agent   ││ Agent  ││ Agent    │
                             └─────────┘└────────┘└──────────┘

Real-world results (DevOps case study):
- Single: 1.7% of recommendations were actionable
- Multi:  100% of recommendations were actionable
```

- Gartner: Multi-agent system inquiries surged **1,445%** (2024 Q1 → 2025 Q2)
- Market size: $7.8B → **$52B+** (projected by 2030)

### 6-7. Major Agent Frameworks

| Framework | Approach | Best For | Difficulty |
|-----------|----------|----------|-----------|
| **LangGraph** | Code (Python), graph state machines | Complex custom agents | High |
| **CrewAI** | Code (Python), role-based teams | Multi-agent prototyping | Medium |
| **OpenAI Agents SDK** | Code (Python), minimalist | All-in on OpenAI ecosystem | Low |
| **Claude Agent SDK** | Code, MCP-native | Claude-based agents | Medium |
| **n8n** | **Visual no-code/low-code** | **Business teams + dev teams** | **Low** |

### 6-8. Agentic AI in the Automotive Industry

| Company | Agentic AI Use Case |
|---------|---------------------|
| **Mercedes-Benz** | MBUX Virtual Assistant — in-vehicle multimodal AI agent, voice + gesture vehicle control |
| **BMW** | AI agents embedded in the Neue Klasse platform, automated dealer customer support |
| **Porsche** | AI-powered vehicle configurator + personalized recommendation agent |
| **Volvo** | Predictive Maintenance AI — sensor data analysis with automatic service alerts |
| **Hyundai/Kia** | AI connected-car platform + dealer network automation workflows |

### 6-9. Adoption Reality — Opportunity and Challenge

```
Current State (Deloitte 2026):
├── Exploring: 30%
├── Piloting: 38%
├── Deployment-ready: 14%
└── In production: 11%  ← Still a small minority

Predictions (Gartner):
├── By end of 2026: 40% of enterprise apps will embed AI agents
├── However: 40%+ of projects predicted to fail due to legacy compatibility issues
└── Key bottleneck: Not AI itself, but "data engineering, governance, and legacy integration"
```

**Takeaway:** The success of agentic AI depends not on the model, but on **orchestration**.

---

## 7. n8n: A Platform That Makes Agentic AI Real

### 7-1. What Is n8n?

| Item | Details |
|------|---------|
| **What** | Fair-code workflow automation platform (since 2019) |
| **Philosophy** | "The flexibility of code + the speed of no-code" |
| **Integrations** | 500+ apps and services |
| **Deployment** | Self-hosted (free) or Cloud (from EUR 24/month) |
| **AI** | LangChain-based **70+ dedicated AI nodes** |
| **Scale** | $2.5B valuation, Nvidia investment, 3,000+ enterprise customers |

### 7-2. Why n8n and Agentic AI Are a Natural Fit

Mapping the core requirements of agentic AI to n8n's capabilities:

| Agentic AI Requirement | How n8n Delivers |
|------------------------|------------------|
| **Autonomy** | Trigger-based auto-execution (webhooks, schedules, events) |
| **Multi-step Reasoning** | AI Agent node with built-in Plan & Execute pattern |
| **Tool Use** | 500+ integrations + MCP Client/Server + HTTP node |
| **Memory** | Simple / PostgreSQL / Redis memory nodes |
| **Adaptability** | Conditional branching, error handling, retry logic |
| **Goal Orientation** | A workflow is a complete pipeline from start to goal |

### 7-3. n8n AI Architecture

```
┌──────────────────────────────────────────────────────┐
│                  n8n AI Workflow                      │
│                                                      │
│  ┌──────────┐    ┌───────────────────────────┐       │
│  │ Trigger  │───→│      AI Agent Node        │       │
│  │(Webhook, │    │  ┌──────────┐             │       │
│  │ Schedule)│    │  │   LLM    │ GPT/Claude  │       │
│  └──────────┘    │  │          │ /Gemini     │       │
│                  │  └──────────┘             │       │
│                  │  ┌──────────┐             │       │
│                  │  │ Memory   │ Conversation │       │
│                  │  └──────────┘             │       │
│                  │  ┌──────────┐             │       │
│                  │  │ Tools    │ API/DB/MCP  │       │
│                  │  └──────────┘             │       │
│                  └───────────┬───────────────┘       │
│                              ↓                       │
│                  ┌───────────────────┐               │
│                  │ Follow-up Actions │               │
│                  │ (Slack, Email, DB)│               │
│                  └───────────────────┘               │
└──────────────────────────────────────────────────────┘
```

**Supported LLMs:** OpenAI, Claude, Gemini, Azure OpenAI, Hugging Face, local models

**Agent Types:**
- **Tools Agent** — ReAct pattern, tool-calling agent
- **Conversational Agent** — Chat-based interface
- **Plan and Execute Agent** — Plan first, then execute (the core agentic AI pattern)

### 7-4. n8n's Unique Position: Why It Stands Out

```
┌──────────────────────────────────────────────────┐
│            Agentic AI Tool Spectrum               │
│                                                  │
│  For Code Experts        ←→       For Business   │
│                                                  │
│  LangGraph  CrewAI  Agent SDK    n8n    Zapier   │
│     High     Med      Med      Low ⭐    Low     │
│                                                  │
│  Maximum flexibility              Maximum access │
│  but developers only              but limited    │
│                                                  │
│         n8n = "Code flexibility + No-code speed" │
│         = Sweet Spot ⭐                           │
└──────────────────────────────────────────────────┘
```

| Comparison | n8n Strengths | n8n Weaknesses |
|-----------|---------------|----------------|
| **vs LangGraph** | Visual builder, faster to build | Less suited for complex state machine control |
| **vs CrewAI** | Self-hosted, data sovereignty | Less sophisticated role-based crew structures |
| **vs Zapier** | JS/Python code support, cost-efficient | Fewer integrations (500 vs 7,000) |
| **vs Make** | AI-native (70+ nodes), self-hostable | Less accessible for non-technical users |

### 7-5. MCP + n8n = Agentic Hub

n8n supports MCP **bidirectionally** (since April 2025):

```
[External MCP Servers]            [n8n Workflow]                [External MCP Clients]
GitHub, Slack, DB  ────→  Consumed via MCP Client node
                          Agent uses them as tools
                                   │
                          Exposed via MCP Server Trigger  ────→  Claude Desktop
                          n8n workflows served as tools          Cursor, VS Code
```

**n8n acts as both a "consumer" and "provider" of MCP simultaneously.**

### 7-6. Automotive Industry AI Trends + n8n Case Studies

| Company/Case | Application | Results |
|-------------|-------------|---------|
| **Mercedes-Benz** | MBUX AI agent — in-vehicle multimodal AI | Voice + gesture agent in production |
| **BMW** | Automated dealer customer support + Neue Klasse AI | Improved CS processing efficiency |
| **Volvo** | Predictive maintenance AI — automated sensor analysis | Increased preventive maintenance rate |
| **Delivery Hero** | n8n-based operational automation workflows | **200 hours** saved per month |
| **BeGlobal** | n8n-based AI-powered proposal generation | **10x** scaling, under 1 minute per proposal |

### 7-7. Agentic Workflow Examples with n8n (Automotive Industry)

**Example 1: Automated Customer Inquiry Agent**
```
Customer email/chat received (Trigger)
  → AI Agent: Classify inquiry (test drive / service / quote / complaint)
  → Test drive: Check available vehicles in CRM → auto-book + confirmation email
  → Service: Query vehicle history DB → estimate costs → book service center
  → Quote: Configure options → AI-generated custom quote → notify sales consultant
```

**Example 2: Market Intelligence Agent**
```
Weekly schedule trigger
  → AI Agent: Gather competitor pricing/promotions (web search tool)
  → RAG: Compare against existing market data DB
  → Generate weekly competitive landscape report
  → Save to Notion + share in Slack marketing channel
```

**Example 3: Predictive Maintenance Agent**
```
Vehicle sensor data received (Webhook / API)
  → AI Agent: Analyze anomaly patterns + assess maintenance needs
  → Tools: Query vehicle history DB, check parts inventory
  → Send proactive alert to customer (SMS/push) + suggest service booking
  → Assess severity: immediate visit recommended vs. handle at next scheduled check
```

### 7-8. n8n: Current State and Potential

**Business Growth:**
- Series C $180M (**Nvidia participation**), $2.5B valuation
- ARR $40M+, **10x** year-over-year revenue growth
- **75%** of customers are using AI tools

**An Honest Assessment:**

| Opportunities | Challenges |
|--------------|------------|
| No-code/low-code democratizes agent building | Complex agent logic favors code frameworks |
| Self-hosted ensures data sovereignty | Enterprise governance and security validation needed |
| 500+ integrations connect legacy systems | LLM token cost management required |
| Bidirectional MCP support makes it an ecosystem hub | The MCP efficiency debate continues |
| Visual builder enables rapid prototyping | Production stability requires further validation |

---

## 7-9. Internal System Integration: APIs Are the Key

> For agentic AI to actually work, internal systems must be accessible via APIs.

```
[User Request] → [n8n Agent] → [API Gateway] → [Internal Systems]
                                                 ├── DMS (Dealer Management)
                                                 ├── CRM (Customer Management)
                                                 ├── ERP (Inventory/Accounting)
                                                 └── Service Booking System
```

**Current State:**
- Many internal systems offer no API or only limited access
- Data is trapped in silos
- Manual data extraction and entry remain the norm

**Required Actions:**
- Develop and expose APIs for core systems
- Standardize the API Gateway
- Design data flows (connect via n8n)

**Key message:** The success of AI agents = the maturity of your API infrastructure.

---

## 8. Conclusion: What We Can Do Right Now

### The Big Picture

```
Models got smarter (LLM competition)
  → They can use tools now (MCP, native AI)
  → They write code themselves (CLI, vibe coding)
  → They manage their own context (context engineering)
  → They work independently (agentic AI)
  → They collaborate as teams (multi-agent systems)

  ★ The platform that visually combines and executes all of this = n8n
```

### Why n8n?

1. **Low barrier to entry:** LangGraph requires Python; n8n starts with drag and drop
2. **Data sovereignty:** Self-hosted means sensitive data never leaves your infrastructure
3. **Practical integration:** 500+ app connectors link directly to your legacy systems
4. **Bidirectional MCP:** Consume external tools while exposing your workflows as tools
5. **Incremental adoption:** Start with simple automation, then gradually expand to AI agents

### Proposal: Next Steps

| Phase | Action | Goal |
|-------|--------|------|
| **Week 1** | Install n8n self-hosted, explore basic workflows | Get familiar with the tool |
| **Week 2** | Build a simple automation with the AI Agent node | Validate the potential |
| **Week 3** | Convert one real business process into an agentic workflow | Apply to real work |
| **Week 4** | Team review, decide whether to expand | Go / No-Go |

### Closing Thoughts

```
"The success of agentic AI depends not on the model, but on orchestration."

"We don't know yet whether this will succeed or fail.
 But if we never try, we'll never know."
```

> **The age of agentic AI has already begun, and n8n opens the door at the lowest threshold.**

---

## References

### Model Competition
- [OpenAI GPT-4.1](https://openai.com/index/gpt-4-1/) | [Claude Sonnet 4.6](https://www.anthropic.com/news/claude-sonnet-4-6) | [Gemini 2.5 Pro](https://blog.google/innovation-and-ai/models-and-research/google-deepmind/google-gemini-updates-io-2025/) | [Llama 4](https://ai.meta.com/blog/llama-4-multimodal-intelligence/)

### MCP & Context Engineering
- [Introducing MCP](https://www.anthropic.com/news/model-context-protocol) | [Why MCP Won](https://thenewstack.io/why-the-model-context-protocol-won/) | [Why CLI Tools Are Beating MCP](https://jannikreinhard.com/2026/02/22/why-cli-tools-are-beating-mcp-for-ai-agents/)
- [Context Engineering — Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) | [Context Engineering — Gartner](https://www.gartner.com/en/articles/context-engineering)

### Agentic AI
- [Agentic AI — MIT Sloan](https://mitsloan.mit.edu/ideas-made-to-matter/agentic-ai-explained) | [Deloitte Tech Trends 2026](https://www.deloitte.com/us/en/insights/topics/technology-management/tech-trends/2026/agentic-ai-strategy.html)
- [Gartner: 40% of Apps Will Feature AI Agents](https://www.gartner.com/en/newsroom/press-releases/2025-08-26-gartner-predicts-40-percent-of-enterprise-apps-will-feature-task-specific-ai-agents-by-2026-up-from-less-than-5-percent-in-2025)

### n8n
- [n8n.io](https://n8n.io/) | [n8n AI Agents](https://n8n.io/ai-agents/) | [n8n Series C](https://blog.n8n.io/series-c/)
- [n8n MCP Integration](https://n8n.io/integrations/categories/ai/model-context-protocol/) | [n8n Case Studies](https://n8n.io/case-studies/)
- [CrewAI vs LangGraph vs n8n](https://www.3pillarglobal.com/insights/blog/comparison-crewai-langgraph-n8n/)

### Vibe Coding & CLI
- [Vibe Coding](https://en.wikipedia.org/wiki/Vibe_coding) | [OpenClaw](https://en.wikipedia.org/wiki/OpenClaw) | [Claude Code vs Cursor](https://www.builder.io/blog/cursor-vs-claude-code)

### Automotive Industry AI Trends
- Mercedes-Benz MBUX AI: https://www.mercedes-benz.com/en/innovation/mbux/
- BMW AI & Digital: https://www.bmwgroup.com/en/innovation/digitalization.html
- Volvo Cars Tech: https://www.volvocars.com/intl/v/connectivity/
- Automotive AI Market Report — McKinsey: https://www.mckinsey.com/industries/automotive-and-assembly/our-insights
- Gartner Automotive AI Predictions: https://www.gartner.com/en/industries/automotive

---

## Slide Plan (30 minutes, ~30 slides)

| Slides | Topic | Time |
|--------|-------|------|
| 1-2 | Title + Opening question | 1 min |
| 3 | Key terminology (LLM, Agent, MCP, etc.) | 1 min |
| 4 | Timeline | 1 min |
| 5-6 | LLM 5-way race (model competition + shifting competitive axis) | 2 min |
| 7-9 | MCP rise → limits → CLI vs MCP efficiency | 3 min |
| 10 | Return to CLI & vibe coding → agentic engineering | 2 min |
| 11-12 | Prompt → context engineering + 7 elements | 2 min |
| 13 | **Bridge: "What happens when all of this comes together? → Agentic AI"** | 0.5 min |
| 14-18 | **Agentic AI deep dive** (analogy, loop, traits, evolution, multi-agent) | 5 min |
| 19 | Major agent framework comparison | 1 min |
| 20 | Adoption reality | 1 min |
| 21-26 | **n8n introduction + automotive cases + honest assessment** | 5 min |
| 27-28 | Big picture summary + proposed next steps | 2 min |
| 29-30 | Closing + Q&A | 2 min |
