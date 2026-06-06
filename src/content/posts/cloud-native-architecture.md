---
title: "云原生架构实战：从容器化到微服务"
published: 2026-03-10
description: "深入云原生技术栈，从 Docker 容器化到 Kubernetes 编排，再到微服务治理，构建弹性可扩展的现代应用架构。"
image: ""
tags: [云原生, Docker, Kubernetes, 微服务]
category: 云计算
draft: false
---

## 什么是云原生？

云原生（Cloud Native）不是某一种技术，而是一套构建和运行应用的方法论，其核心技术栈包括：

- **容器化** — Docker、containerd
- **服务编排** — Kubernetes
- **微服务** — 服务拆分与治理
- **DevOps** — CI/CD 自动化
- **声明式 API** — 基础设施即代码

## 容器化实践

### 多阶段构建

```dockerfile
# 构建阶段
FROM node:22-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 运行阶段
FROM node:22-alpine AS runner
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/server.js"]
```

### Docker Compose 本地开发

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DB_HOST=postgres
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: myapp
      POSTGRES_PASSWORD: secret
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  pgdata:
```

## Kubernetes 核心概念

K8s 是云原生的基石，理解以下核心概念至关重要：

| 资源 | 说明 | 示例用途 |
|------|------|---------|
| Pod | 最小调度单元 | 运行应用容器 |
| Deployment | 声明式更新 | 管理无状态应用 |
| Service | 服务发现 | 暴露应用端点 |
| Ingress | 入口路由 | HTTP 路由规则 |
| ConfigMap | 配置管理 | 环境变量注入 |
| Secret | 敏感数据 | 数据库密码等 |

### 部署清单示例

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tech-blog-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tech-blog-api
  template:
    metadata:
      labels:
        app: tech-blog-api
    spec:
      containers:
      - name: api
        image: tech-blog-api:1.0.0
        ports:
        - containerPort: 3000
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
```

## 微服务治理

### 服务间通信

- **同步通信**：gRPC、REST API
- **异步通信**：消息队列（Kafka、RabbitMQ）
- **服务网格**：Istio、Linkerd

### 可观测性三大支柱

1. **日志（Logging）** — ELK Stack / Loki
2. **指标（Metrics）** — Prometheus + Grafana
3. **追踪（Tracing）** — Jaeger / Zipkin

> 云原生的本质是让应用具备弹性、可观测和可演进的能力，而不是简单地"搬到云上"。
