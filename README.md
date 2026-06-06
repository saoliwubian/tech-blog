# TechPulse

> 探索科技前沿 · 洞察数字未来

TechPulse 是一个专注于前沿科技的深度博客，基于 [Fuwari](https://github.com/saicaca/fuwari) 模板构建。

## 特性

- 基于 [Astro](https://astro.build) + [Tailwind CSS](https://tailwindcss.com) 构建
- 流畅的页面切换动画
- 亮色/暗色模式切换
- 响应式设计
- Pagefind 全文搜索
- Giscus 评论系统
- 社交分享按钮
- 文章分类与标签
- RSS 订阅
- 目录导航

## 文章内容

| 文章 | 分类 | 标签 |
|------|------|------|
| 大语言模型的崛起：从 GPT 到多模态 AI | 人工智能 | AI, LLM, 深度学习, GPT |
| 2026 前端开发指南 | Web 开发 | 前端, React, Vue, Astro |
| 云原生架构实战 | 云计算 | 云原生, Docker, Kubernetes |
| 开源项目贡献指南 | 开源技术 | 开源, GitHub, 协作 |
| Rust 系统编程 | 编程语言 | Rust, 系统编程, 内存安全 |
| AI Agent 实战 | 人工智能 | AI, Agent, LLM, 自动化 |
| WebAssembly：突破浏览器性能边界 | Web 开发 | WebAssembly, Wasm, 性能 |

## 本地开发

```bash
# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建
pnpm build

# 预览
pnpm preview
```

## 部署

本项目使用 GitHub Pages 部署，通过 GitHub Actions 自动构建和部署。

1. Fork 或克隆本仓库
2. 在仓库 Settings → Pages 中选择 GitHub Actions 作为源
3. 推送到 main 分支即可自动部署

## 配置 Giscus 评论

1. 在 [giscus.app](https://giscus.app/) 配置你的 GitHub 仓库
2. 将生成的 `repo-id` 和 `category-id` 填入 `src/components/misc/Giscus.astro`

## License

基于 [MIT License](./LICENSE) 开源，博客模板来自 [Fuwari](https://github.com/saicaca/fuwari)。
