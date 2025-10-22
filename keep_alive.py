#!/usr/bin/env python3
"""
简单的保活脚本 - 确保ML预测服务持续运行
Simple Keep-Alive Script for ML Prediction Service
"""

import time
import requests
import subprocess
import logging
from datetime import datetime
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/user/webapp/logs/keep_alive.log'),
        logging.StreamHandler()
    ]
)

SERVICE_URL = "http://localhost:8080"
HEALTH_ENDPOINT = f"{SERVICE_URL}/health"
CHECK_INTERVAL = 60  # 60秒检查一次

def check_service():
    """检查服务状态"""
    try:
        response = requests.get(HEALTH_ENDPOINT, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'healthy':
                return True
        return False
    except:
        return False

def restart_service():
    """重启服务"""
    try:
        logging.info("🔄 正在重启ML预测服务...")
        
        # 停止现有服务
        subprocess.run(['pkill', '-f', 'stable_app.py'], check=False)
        time.sleep(3)
        
        # 启动新服务
        subprocess.Popen(
            ['python', '/home/user/webapp/stable_app.py'],
            cwd='/home/user/webapp',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # 等待服务启动
        time.sleep(10)
        
        if check_service():
            logging.info("✅ 服务重启成功")
            return True
        else:
            logging.error("❌ 服务重启后仍无法访问")
            return False
            
    except Exception as e:
        logging.error(f"❌ 服务重启失败: {e}")
        return False

def main():
    """主监控循环"""
    logging.info("🚀 ML预测服务保活监控启动")
    logging.info(f"🌐 监控地址: {SERVICE_URL}")
    
    consecutive_failures = 0
    max_failures = 3
    
    while True:
        try:
            if check_service():
                if consecutive_failures > 0:
                    logging.info("✅ 服务恢复正常")
                    consecutive_failures = 0
                else:
                    # 每10分钟报告一次正常状态
                    current_minute = datetime.now().minute
                    if current_minute % 10 == 0:
                        logging.info("🟢 服务运行正常")
            else:
                consecutive_failures += 1
                logging.warning(f"⚠️ 服务检查失败 ({consecutive_failures}/{max_failures})")
                
                if consecutive_failures >= max_failures:
                    logging.error("🔴 达到最大失败次数，尝试重启...")
                    if restart_service():
                        consecutive_failures = 0
                    else:
                        logging.error("💥 重启失败，继续监控...")
            
            time.sleep(CHECK_INTERVAL)
            
        except KeyboardInterrupt:
            logging.info("👋 监控服务手动停止")
            break
        except Exception as e:
            logging.error(f"监控异常: {e}")
            time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()