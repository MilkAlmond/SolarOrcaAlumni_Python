#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""配置文件模块"""

import json
import os

DEFAULT_CONFIG = {
    'data_file': 'data/alumni_data.csv',
    'output_dir': 'output',
    'chart_dpi': 150,
    'max_preview_rows': 10,
    'log_dir': 'logs'
}


def load_config():
    """加载配置文件，如果不存在则创建默认配置"""
    config_path = 'config.json'
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                # 合并默认配置，确保所有字段都存在
                config = DEFAULT_CONFIG.copy()
                config.update(user_config)
                return config
        except Exception:
            print("⚠️ 配置文件损坏，使用默认配置")
            return DEFAULT_CONFIG.copy()
    else:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2)
        print("📝 已创建默认配置文件: config.json")
        return DEFAULT_CONFIG.copy()