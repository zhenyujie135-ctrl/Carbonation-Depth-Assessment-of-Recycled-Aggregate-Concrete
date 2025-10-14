#!/usr/bin/env python3
"""
服务监控脚本 - 确保ML预测系统持续运行
Service Monitor Script - Keep ML Prediction System Running
"""

import time
import requests
import subprocess
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/monitor.log'),
        logging.StreamHandler()
    ]
)

def check_service_health():
    """检查服务健康状态"""
    try:
        response = requests.get('http://localhost:5002/', timeout=10)
        if response.status_code == 200:
            return True
        else:
            logging.warning(f"服务响应异常: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logging.error(f"服务健康检查失败: {e}")
        return False

def restart_service():
    """重启服务"""
    try:
        logging.info("正在重启ML预测服务...")
        
        # 停止现有服务
        subprocess.run(['pkill', '-f', 'gunicorn.*wsgi:app'], check=False)
        time.sleep(5)
        
        # 启动新服务
        subprocess.Popen(
            ['gunicorn', '--config', 'gunicorn_config.py', 'wsgi:app'],
            cwd='/home/user/webapp',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # 等待服务启动
        time.sleep(10)
        
        if check_service_health():
            logging.info("✅ 服务重启成功")
            return True
        else:
            logging.error("❌ 服务重启后仍然无法访问")
            return False
            
    except Exception as e:
        logging.error(f"服务重启失败: {e}")
        return False

def get_service_stats():
    """获取服务统计信息"""
    try:
        # 检查进程数
        result = subprocess.run(
            ['ps', 'aux'], 
            capture_output=True, 
            text=True
        )
        worker_count = result.stdout.count('gunicorn.*wsgi:app')
        
        return {
            'worker_count': worker_count,
            'timestamp': datetime.now().isoformat()
        }
    except:
        return {'worker_count': 0, 'timestamp': datetime.now().isoformat()}

def monitor_loop():
    """主监控循环"""
    logging.info("🚀 ML碳化深度预测系统监控启动")
    logging.info("🌐 服务地址: https://5002-io345j3ofvh5e2qc8bjvs-6532622b.e2b.dev")
    
    consecutive_failures = 0
    max_failures = 3
    check_interval = 30  # 30秒检查一次
    
    while True:
        try:
            stats = get_service_stats()
            
            if check_service_health():
                if consecutive_failures > 0:
                    logging.info(f"✅ 服务恢复正常 (Worker: {stats['worker_count']})")
                    consecutive_failures = 0
                else:
                    # 每5分钟记录一次正常状态
                    current_minute = datetime.now().minute
                    if current_minute % 5 == 0:
                        logging.info(f"🟢 服务运行正常 (Worker: {stats['worker_count']})")
            else:
                consecutive_failures += 1
                logging.warning(f"⚠️  服务健康检查失败 ({consecutive_failures}/{max_failures})")
                
                if consecutive_failures >= max_failures:
                    logging.error("🔄 连续失败次数达到阈值，尝试重启服务...")
                    if restart_service():
                        consecutive_failures = 0
                    else:
                        logging.error("💥 服务重启失败，继续监控...")
            
            time.sleep(check_interval)
            
        except KeyboardInterrupt:
            logging.info("👋 监控服务手动停止")
            break
        except Exception as e:
            logging.error(f"监控异常: {e}")
            time.sleep(check_interval)

if __name__ == "__main__":
    monitor_loop()