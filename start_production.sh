#!/bin/bash
"""
ML碳化深度预测系统 - 生产部署启动脚本
Production Deployment Startup Script for ML Carbonation Prediction System
"""

cd /home/user/webapp

echo "🚀 启动ML-RAC碳化深度预测系统生产服务器..."
echo "Starting ML-RAC Carbonation Prediction Production Server..."

# 检查并创建日志目录
mkdir -p logs

# 检查端口是否被占用
if lsof -Pi :5002 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  端口5002已被占用，正在停止现有服务..."
    pkill -f "gunicorn.*wsgi:app"
    sleep 3
fi

# 启动Gunicorn生产服务器
echo "🔧 启动Gunicorn服务器 (端口: 5002)..."
gunicorn --config gunicorn_config.py wsgi:app &

# 等待服务启动
sleep 5

# 检查服务状态
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5002/ | grep -q "200"; then
    echo "✅ 服务启动成功!"
    echo "🌐 访问地址: https://5002-io345j3ofvh5e2qc8bjvs-6532622b.e2b.dev"
    echo "📊 API端点: /predict"
    echo "🔍 健康检查: /"
    echo ""
    echo "📈 系统信息:"
    echo "   - Worker进程数: $(ps aux | grep 'gunicorn.*wsgi:app' | grep -v grep | wc -l)"
    echo "   - 配置文件: gunicorn_config.py"
    echo "   - 日志文件: logs/access.log, logs/error.log"
    echo ""
    echo "🎯 使用说明:"
    echo "   1. 在浏览器中打开上述访问地址"
    echo "   2. 输入13个RAC参数"
    echo "   3. 选择ML模型 (推荐XGBoost)"
    echo "   4. 点击'开始预测'获取结果"
    echo ""
    echo "⚡ 生产级特性:"
    echo "   - 多Worker进程提高并发性能"
    echo "   - 自动重启和错误恢复"
    echo "   - 详细访问和错误日志"
    echo "   - 优化的超时和连接设置"
else
    echo "❌ 服务启动失败，请检查日志文件"
    tail -n 10 logs/error.log 2>/dev/null || echo "无法读取错误日志"
fi