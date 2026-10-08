export const siteConfig = {
  name: "黄泽霖",
  title: "Kaggle Expert",
  description:
    "黄泽霖的个人作品集，展示人工智能、计算机视觉、大语言模型与智能系统相关研究和项目。",
  accentColor: "#2563eb",

  social: {
    email: "zelin_huang@163.com",
    github: "https://github.com/HuangZeLinCute",
    kaggle: "https://www.kaggle.com/blueshyy",
  },

  aboutMe:
    "我是一名 AI 工程师/研究者，关注如何让模型真正读懂文档、让 Agent 可靠地完成任务。研究与实践覆盖计算机视觉、大语言模型和智能体系统，既做算法研究（第一作者论文），也做系统开发与竞赛实战。",
    skills: [
          ],

  projects: [
    {
      name: "AX & AX Crew —— Rust 分布式 AI 智能体运行时与控制平面",
      description:
        "AX 是一个基于 Rust 编写、可运行于任意机器的极速 AI 终端智能体，本地优先、即开即用，支持 MCP、Agent Skills 与按需加载；AX Crew 是与其配套开发的控制平面，用于跨机器的连接、编排与管理，支持任务 DAG 调度、跨设备委派与自动化例行任务。两者共同构成一套自研的分布式多智能体基础设施。",
      link:
        "https://github.com/Axium-Labs",
      skills: [
        "Rust",
        "LLM Agent",
        "MCP",
        "Multi-Agent Orchestration",
        "Distributed Systems",
      ],
    },

    {
      name: "CourtMind —— 羽毛球比赛视频智能分析平台",
      description:
        "基于React与FastAPI构建的羽毛球比赛视频分析平台。通过球场标定、人体姿态估计与羽毛球轨迹追踪，实现Rally自动切分、击球统计与比赛报告生成，并支持基于比赛结构化数据的AI对局问答，可在回答中直接回看对应视频片段。",
      link:
        "https://github.com/HuangZeLinCute/CourtMind",
      skills: [
        "PyTorch",
        "FastAPI",
        "React",
        "Computer Vision",
        "LLM",
      ],
    },
  ],

  publications: [
    {
      title:
        "ASMG-DARN: Adaptive Shadow Mask Generation and Document-Aware Refinement Network for Document Shadow Removal",
      venue: "ICIC 2026（CCF-C 类会议，Oral）",
      authors: "黄泽霖（第一作者）",
      year: "2026",
      description:
        "提出自适应阴影掩码生成（ASMG）与文档感知细化（DARN）两阶段框架，将阴影检测与图像恢复任务解耦，在 RDD 与 Kligler 数据集上取得优于基线方法的结果。",
      link:
        "https://github.com/HuangZeLinCute/DocMaskRefine",
    },
  ],


  experience: [
    {
      company: "Kaggle · Featured Code Competition",
      title: "AI Mathematical Olympiad - Progress Prize 1",
      dateRange: "2025",
      bullets: [
        "全球排名 18 / 1161 支队伍",
        "利用人工智能模型求解国家级数学奥林匹克挑战题",
      ],
    },

    {
      company: "Kaggle · Featured Code Competition",
      title: "Santa 2025 - Christmas Tree Packing Challenge",
      dateRange: "2026",
      bullets: [
        "全球排名 23 / 3357 支队伍",
        "圣诞树装箱组合优化问题求解",
      ],
    },

    {
      company: "Kaggle · Featured Code Competition",
      title: "Deep Past Challenge - Translate Akkadian to English",
      dateRange: "2026",
      bullets: [
        "全球排名 57 / 2674 支队伍",
        "古亚述语楔形文字到英文的机器翻译",
      ],
    },

    {
      company: "Kaggle · Research Code Competition",
      title: "Vesuvius Challenge - Surface Detection",
      dateRange: "2026",
      bullets: [
        "全球排名 57 / 1391 支队伍",
        "构建模型实现古卷轴的虚拟展开",
      ],
    },
  ],
};
