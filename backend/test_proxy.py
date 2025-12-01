#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试 Python 是否能通过代理访问外网
"""
import requests
import os

def test_proxy():
    print("=" * 60)
    print("测试 Python 代理配置")
    print("=" * 60)
    
    # 检查环境变量
    print("\n1. 检查代理环境变量:")
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    print(f"   HTTP_PROXY: {http_proxy or '未设置'}")
    print(f"   HTTPS_PROXY: {https_proxy or '未设置'}")
    
    # 测试直连
    print("\n2. 测试直连 (不使用代理):")
    try:
        response = requests.get('https://www.google.com', timeout=5)
        print(f"   ✅ 直连成功: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 直连失败: {type(e).__name__}")
    
    # 测试系统代理
    print("\n3. 测试系统代理:")
    try:
        # requests 会自动使用系统代理
        response = requests.get('https://www.google.com', timeout=5)
        print(f"   ✅ 系统代理成功: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 系统代理失败: {type(e).__name__}")
    
    # 测试手动配置代理
    print("\n4. 测试手动配置代理:")
    proxies = {
        'http': 'http://127.0.0.1:10808',  # V2Ray 默认端口
        'https': 'http://127.0.0.1:10808'
    }
    
    try:
        response = requests.get('https://www.google.com', proxies=proxies, timeout=5)
        print(f"   ✅ 手动代理成功: {response.status_code}")
        print(f"   建议使用端口: 10808")
        return True
    except Exception as e:
        print(f"   ❌ 端口 10808 失败: {type(e).__name__}")
        
        # 尝试其他常见端口
        for port in [1080, 7890, 10809]:
            try:
                proxies = {
                    'http': f'http://127.0.0.1:{port}',
                    'https': f'http://127.0.0.1:{port}'
                }
                response = requests.get('https://www.google.com', proxies=proxies, timeout=3)
                print(f"   ✅ 端口 {port} 成功!")
                print(f"   建议使用端口: {port}")
                return True
            except:
                continue
        
        print(f"   ❌ 所有常见端口都失败")
        return False
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_proxy()
