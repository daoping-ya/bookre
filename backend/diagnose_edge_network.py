#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Edge-TTS 网络连接诊断工具
"""
import socket
import requests
from urllib.parse import urlparse
import sys

def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60)

def test_dns(domain):
    """测试 DNS 解析"""
    print(f"\n1. 测试 DNS 解析: {domain}")
    try:
        ip = socket.gethostbyname(domain)
        print(f"   ✅ DNS 解析成功: {ip}")
        return True, ip
    except socket.gaierror as e:
        print(f"   ❌ DNS 解析失败: {e}")
        return False, None

def test_http_connection(url):
    """测试 HTTP 连接"""
    print(f"\n2. 测试 HTTP 连接: {url}")
    try:
        response = requests.get(url, timeout=10, verify=False)
        print(f"   ✅ HTTP 连接成功: {response.status_code}")
        return True
    except requests.exceptions.Timeout:
        print(f"   ❌ 连接超时")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ 连接失败: {e}")
        return False
    except Exception as e:
        print(f"   ❌ 未知错误: {e}")
        return False

def test_edge_tts_import():
    """测试 edge-tts 模块"""
    print(f"\n3. 测试 edge-tts 模块")
    try:
        import edge_tts
        print(f"   ✅ edge-tts 已安装")
        return True
    except ImportError:
        print(f"   ❌ edge-tts 未安装")
        print(f"   请运行: pip install edge-tts")
        return False

def test_edge_tts_basic():
    """测试 edge-tts 基本功能"""
    print(f"\n4. 测试 edge-tts 基本功能")
    try:
        import edge_tts
        import asyncio
        
        async def test():
            communicate = edge_tts.Communicate("test", "zh-CN-XiaoxiaoNeural")
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    return True
            return False
        
        result = asyncio.run(test())
        if result:
            print(f"   ✅ edge-tts 可以正常工作")
            return True
        else:
            print(f"   ❌ edge-tts 无法生成音频")
            return False
    except Exception as e:
        print(f"   ❌ edge-tts 测试失败: {type(e).__name__}: {str(e)[:100]}")
        return False

def check_proxy():
    """检查代理设置"""
    print(f"\n5. 检查代理设置")
    import os
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if http_proxy or https_proxy:
        print(f"   HTTP_PROXY: {http_proxy or '未设置'}")
        print(f"   HTTPS_PROXY: {https_proxy or '未设置'}")
    else:
        print(f"   ℹ️  未配置代理")
    
    return http_proxy or https_proxy

def main():
    print_header("Edge-TTS 网络连接诊断")
    
    results = {}
    
    # 测试 DNS
    results['dns'], ip = test_dns('speech.platform.bing.com')
    
    # 测试 HTTP 连接
    results['http'] = test_http_connection('https://www.bing.com')
    
    # 测试模块
    results['module'] = test_edge_tts_import()
    
    # 检查代理
    proxy = check_proxy()
    
    # 测试 edge-tts
    if results['module']:
        results['edge_tts'] = test_edge_tts_basic()
    else:
        results['edge_tts'] = False
    
    # 总结
    print_header("诊断总结")
    
    all_pass = all(results.values())
    
    if all_pass:
        print("\n✅ 所有测试通过！Edge-TTS 应该可以正常工作。")
        print("\n建议操作：")
        print("1. 重启后端服务")
        print("2. 刷新浏览器")
        print("3. 测试语音播放")
    else:
        print("\n❌ 存在问题，请根据以下建议操作：")
        
        if not results['dns']:
            print("\n【DNS 问题】")
            print("- 检查网络连接")
            print("- 尝试更换 DNS 服务器（如 8.8.8.8）")
        
        if not results['http']:
            print("\n【网络连接问题】")
            print("- 检查防火墙设置")
            print("- 尝试使用代理或 VPN")
            print("- 确保可以访问国外网站")
        
        if not results['module']:
            print("\n【模块问题】")
            print("- 运行: pip install edge-tts")
        
        if not results['edge_tts']:
            print("\n【Edge-TTS 服务问题】")
            print("- 可能需要配置代理")
            print("- 可能 IP 被限制，尝试更换网络")
            print("- 检查是否有防火墙阻止 WebSocket 连接")
    
    print("\n" + "=" * 60)
    
    return 0 if all_pass else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n已取消诊断")
        sys.exit(1)
