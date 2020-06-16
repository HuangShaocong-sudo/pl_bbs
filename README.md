## 一个基于 Flask 开发的论坛

#### **具体实现**

技术栈：Ubuntu + Nginx + Gunicorn + Flask + Jinja2 + MySQL + Redis + Celery

- 功能
  - 邮箱验证登录，忘记密码，用户信息修改，**权限验证**，板块和用户管理功能 
  - 分主题发帖，话题回复，@提醒，发邮件，Markdown 语法渲染支持
- 数据存储 
  - 利用 MySQL 配合 Flask 的 SQLAlchemy 插件实现了 ORM
  - 利用 **Redis** 实现服务器端 session 和 csrf_token 管理
- 性能提升
  - 利用 **Nginx** 作为反向代理，实现 静态资源访问 和 SSL 证书安装
  - 利用 **Gunicorn** 和 Nginx 实现 单机**多进程负载均衡**，利用 **gevent** 实现 **协程** 来并发处理请求
  - 利用 **消息队列**(Celery) 和 Redis 实现异步发邮件，提高用户体验的同时，确保了邮件发送的可靠性
  - 利用 MySQL 的 事务 和 join 机制优化 ORM 生成的 SQL请求语句
- 安全
  - 实现对 CSRF、XSS 脚本注入 和 SQL 注入 等攻击的防御
  - 实现 HTTPS (SSL证书) 部署

#### 地址

https://www.piggiesland.com  								测试账号：user1   123