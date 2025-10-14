#!/usr/bin/env python3
"""
WSGI配置文件 - 用于生产部署
WSGI configuration for production deployment
"""

from web_carbonation_app_ml import app

if __name__ == "__main__":
    app.run()