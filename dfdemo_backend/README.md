﻿# df-demo-backend 数据上链后台

这是基于 Django 框架编写的 `df-demo-backend` 后台应用，主要用于将数据上链到 Tura 链。该系统目前提供了获取 Solana 链数据的方式和上链 API，其他数据的获取和上链方式可以根据需求自行编写和扩展。

## 系统要求

在使用该后台之前，需要确保以下环境和依赖已经配置好：

1. **Tura 链**：需要搭建 Tura 链并确保链的正常运行。该系统的功能依赖于 Tura 链进行数据上链。
2. **Solana 数据获取**：示例中使用的是 Solana 数据的获取方式，相关数据可以通过 API 接口获取并上传到 Tura 链。
3. **Django 环境**：系统基于 Django 框架开发，确保你的环境中已安装 Django。
4. **Gunicorn**：用于启动 Django 应用的 WSGI 服务器。
5. 数据库为postgres

## 启动命令

在搭建好环境后，可以通过以下方式启动 Django 后台服务。

### 使用 `python manage.py runserver` 启动

你可以通过以下命令启动 Django 内置的开发服务器：

```bash
python manage.py runserver 0.0.0.0:8000
