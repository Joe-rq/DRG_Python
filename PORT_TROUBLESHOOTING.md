# 端口冲突问题解决指南

## 🚨 问题描述

如果在启动Web应用时遇到以下错误：
```
Address already in use
Port 5000 is in use by another program.
```

这说明端口被其他程序占用了。

## 🔧 解决方案

### 方案1：使用不同端口（推荐）

我们已经将默认端口从5000改为8080，直接使用启动脚本即可：

```bash
# Linux/Mac
./start_web.sh

# Windows
start_web.cmd
```

访问地址：**http://localhost:8080**

### 方案2：自定义端口

如果8080端口也被占用，可以设置环境变量使用其他端口：

```bash
# Linux/Mac
export PORT=9000
./start_web.sh

# Windows
set PORT=9000
start_web.cmd
```

### 方案3：释放5000端口（macOS）

在macOS上，端口5000通常被AirPlay Receiver占用：

1. 打开 **系统偏好设置** → **通用** → **AirDrop与接力**
2. 关闭 **AirPlay接收器** 选项
3. 重新启动应用

### 方案4：查找并终止占用端口的程序

```bash
# 查看占用5000端口的程序
lsof -i :5000

# 终止占用端口的程序（替换PID为实际进程ID）
kill -9 <PID>
```

## 🔍 端口检查命令

检查端口是否被占用：
```bash
# 检查8080端口
lsof -i :8080

# 检查所有监听端口
netstat -an | grep LISTEN
```

## 📝 常见占用5000端口的程序

- **macOS AirPlay Receiver**：系统服务
- **Flask开发服务器**：其他Flask应用
- **Node.js应用**：某些开发服务器
- **其他Web服务**：各种本地开发工具

## 🎯 推荐配置

为避免端口冲突，建议使用以下端口：
- **8080**：Web应用默认端口
- **8000**：备用端口
- **3000**：前端开发服务器常用端口
- **9000**：备用端口

## ⚡ 快速测试

启动应用后，使用以下命令测试：
```bash
curl http://localhost:8080
```

如果返回HTML内容，说明应用启动成功。
