export const siteConfig = {
  name: "黄泽霖",
  title: "人工智能研究者",
  description:
    "黄泽霖的个人作品集，展示人工智能、计算机视觉、大语言模型与智能系统相关研究和项目。",
  accentColor: "#2563eb",

  social: {
    email: "zelin_huang@163.com",
    github: "https://github.com/HuangZeLinCute",
    kaggle: "https://www.kaggle.com/blueshyy",
  },

  aboutMe:
    "我是一名人工智能专业本科生，研究方向主要包括计算机视觉、大语言模型、智能体系统与深度学习。目前专注于文档图像处理、AI Agent以及机器学习系统开发，曾以第一作者身份发表计算机视觉方向论文，并在多个Kaggle竞赛中获得银牌成绩。",

  skills: [
    "Python",
    "LangGraph"
  ],

  projects: [
    {
      name: "DocRepairNet —— 文档图像阴影去除网络",
      description:
        "提出ASMG-DARN文档阴影去除框架，通过自适应阴影掩码生成模块与文档感知细化模块，实现复杂阴影环境下的文档恢复。论文发表于ICIC 2026（CCF-C类会议，Oral，一作）。",
      link:
        "https://github.com/HuangZeLinCute/DocMaskRefine",
      skills: [
        "PyTorch",
        "Computer Vision",
        "Transformer",
        "Attention",
      ],
    },

    {
      name: "AutoEdit —— 长视频智能切片Agent",
      description:
        "基于LangGraph构建的多智能体视频处理系统，实现视频理解、语音识别、内容分析、自动剪辑、字幕生成以及视频渲染。",
      link:
        "https://github.com/HuangZeLinCute/auto_edit",
      skills: [
        "LangGraph",
        "LLM Agent",
        "FastAPI",
        "Whisper",
        "FFmpeg",
      ],
    },

    {
      name: "校园舆情分析与可视化平台",
      description:
        "基于Kafka、Flink、Spring Boot和Vue构建的实时舆情分析平台，实现数据采集、流式计算、情感分析和可视化展示。",
      link:
        "https://www.bilibili.com/video/BV1Sr421g7Yc/",
      skills: [
        "Spring Boot",
        "Vue",
        "Kafka",
        "Flink",
        "NLP",
      ],
    },

    {
      name: "Kaggle竞赛项目合集",
      description:
        "参与多个Kaggle人工智能竞赛，在大语言模型推理、三维医学图像分割、低资源机器翻译和组合优化任务中取得银牌成绩。",
      link:
        "https://www.kaggle.com/blueshyy",
      skills: [
        "LLM",
        "Machine Learning",
        "Optimization",
      ],
    },
  ],


  experience: [
    {
      company: "科研经历",
      title:
        "计算机视觉研究",
      dateRange:
        "2025 - 至今",
      bullets: [
        "提出ASMG-DARN文档阴影去除网络，将阴影检测与图像恢复任务进行解耦。",
        "以第一作者身份发表论文《ASMG-DARN: Adaptive Shadow Mask Generation and Document-Aware Refinement Network for Document Shadow Removal》。",
        "在RDD和Kligler数据集上取得优于基线方法的实验结果。",
      ],
    },

    {
      company: "Kaggle竞赛",
      title:
        "机器学习竞赛参与者",
      dateRange:
        "2025 - 至今",
      bullets: [
        "获得多项Kaggle银牌成绩。",
        "AI Mathematical Olympiad - Progress Prize 1：全球排名18/1161。",
        "涉及LLM推理、3D医学图像分割、机器翻译以及组合优化等方向。",
      ],
    },

    {
      company: "个人项目",
      title:
        "人工智能系统开发",
      dateRange:
        "2024 - 至今",
      bullets: [
        "开发多个人工智能应用，包括智能视频编辑Agent、实时舆情分析系统等。",
        "熟悉PyTorch、FastAPI、LangGraph以及大模型应用开发流程。",
      ],
    },
  ],


  education: [
    {
      school:
        "广东白云学院",
      degree:
        "人工智能专业 本科",
      dateRange:
        "",
      achievements: [
        "主要学习人工智能、机器学习、深度学习以及计算机视觉相关课程。",
        "研究方向包括文档智能、大语言模型和智能体系统。",
      ],
    },
  ],
};
