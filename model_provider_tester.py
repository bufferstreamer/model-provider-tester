#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Provider Connectivity Tester
测试自定义模型 provider 的连通性
"""

import argparse
import sys
import time
import json
from typing import Optional, Dict, Any
import requests

# 修复 Windows 控制台编码问题
if sys.platform == 'win32':
    import os
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')


class ProviderTester:
    """Provider 连通性测试器"""
    
    def __init__(self, api_key: str, base_url: str, api_type: str, model: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.api_type = api_type.lower()
        self.model = model or self._get_default_model()
        
    def _get_default_model(self) -> str:
        """获取默认测试模型"""
        defaults = {
            'anthropic': 'claude-3-haiku-20240307',
            'openai': 'gpt-3.5-turbo',
            'google': 'gemini-pro'
        }
        return defaults.get(self.api_type, 'default-model')
    
    def test_anthropic(self) -> Dict[str, Any]:
        """测试 Anthropic Messages API"""
        url = f"{self.base_url}/v1/messages"
        headers = {
            'x-api-key': self.api_key,
            'anthropic-version': '2023-06-01',
            'content-type': 'application/json'
        }
        payload = {
            'model': self.model,
            'max_tokens': 10,
            'messages': [
                {'role': 'user', 'content': 'Hi'}
            ]
        }
        
        return self._send_request(url, headers, payload)
    
    def test_openai(self) -> Dict[str, Any]:
        """测试 OpenAI Chat Completions API"""
        url = f"{self.base_url}/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        payload = {
            'model': self.model,
            'max_tokens': 10,
            'messages': [
                {'role': 'user', 'content': 'Hi'}
            ]
        }
        
        return self._send_request(url, headers, payload)
    
    def test_google(self) -> Dict[str, Any]:
        """测试 Google Gemini API"""
        url = f"{self.base_url}/v1/models/{self.model}:generateContent"
        headers = {
            'Content-Type': 'application/json'
        }
        # Google 使用 query parameter 传 API key
        url = f"{url}?key={self.api_key}"
        payload = {
            'contents': [
                {
                    'parts': [
                        {'text': 'Hi'}
                    ]
                }
            ],
            'generationConfig': {
                'maxOutputTokens': 10
            }
        }
        
        return self._send_request(url, headers, payload)
    
    def _send_request(self, url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
        """发送测试请求"""
        start_time = time.time()
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=30
            )
            elapsed = time.time() - start_time
            
            result = {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'response_time': round(elapsed, 3),
                'url': url
            }
            
            if response.status_code == 200:
                result['message'] = '✅ 连通成功！'
                try:
                    result['response_preview'] = response.json()
                except:
                    result['response_preview'] = response.text[:200]
            else:
                result['message'] = f'❌ 连接失败'
                try:
                    result['error'] = response.json()
                except:
                    result['error'] = response.text[:500]
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'message': '❌ 请求超时',
                'error': '连接超时（30秒）',
                'response_time': 30.0,
                'url': url
            }
        except requests.exceptions.ConnectionError as e:
            return {
                'success': False,
                'message': '❌ 连接错误',
                'error': str(e),
                'response_time': time.time() - start_time,
                'url': url
            }
        except Exception as e:
            return {
                'success': False,
                'message': '❌ 未知错误',
                'error': str(e),
                'response_time': time.time() - start_time,
                'url': url
            }
    
    def test(self) -> Dict[str, Any]:
        """执行测试"""
        test_methods = {
            'anthropic': self.test_anthropic,
            'openai': self.test_openai,
            'google': self.test_google
        }
        
        if self.api_type not in test_methods:
            return {
                'success': False,
                'message': f'❌ 不支持的 API 类型: {self.api_type}',
                'error': f'支持的类型: {", ".join(test_methods.keys())}'
            }
        
        print(f"🔍 测试中...")
        print(f"  类型: {self.api_type}")
        print(f"  地址: {self.base_url}")
        print(f"  模型: {self.model}")
        print()
        
        return test_methods[self.api_type]()


def print_result(result: Dict[str, Any]):
    """打印测试结果"""
    print("=" * 60)
    print(result['message'])
    print("=" * 60)
    
    if 'status_code' in result:
        print(f"状态码: {result['status_code']}")
    
    print(f"响应时间: {result['response_time']}s")
    
    if 'url' in result:
        print(f"请求地址: {result['url']}")
    
    if result['success']:
        print("\n✅ Provider 配置正确，可以正常使用！")
        if 'response_preview' in result:
            print("\n响应预览:")
            print(json.dumps(result['response_preview'], indent=2, ensure_ascii=False)[:500])
    else:
        print("\n❌ 连接失败，请检查配置")
        if 'error' in result:
            print("\n错误信息:")
            if isinstance(result['error'], dict):
                print(json.dumps(result['error'], indent=2, ensure_ascii=False))
            else:
                print(result['error'])


def main():
    parser = argparse.ArgumentParser(
        description='测试模型 Provider 连通性',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 测试 Anthropic 格式
  python model_provider_tester.py -k YOUR_API_KEY -u https://api.anthropic.com -t anthropic

  # 测试 OpenAI 格式
  python model_provider_tester.py -k YOUR_API_KEY -u https://api.openai.com -t openai -m gpt-4

  # 测试 Google Gemini
  python model_provider_tester.py -k YOUR_API_KEY -u https://generativelanguage.googleapis.com -t google

支持的 API 类型: anthropic, openai, google
        '''
    )
    
    parser.add_argument('-k', '--api-key', required=True, help='API Key')
    parser.add_argument('-u', '--url', required=True, help='Provider 地址 (base URL)')
    parser.add_argument('-t', '--type', required=True, choices=['anthropic', 'openai', 'google'], 
                        help='API 类型')
    parser.add_argument('-m', '--model', help='模型名称（可选，使用默认测试模型）')
    parser.add_argument('--json', action='store_true', help='以 JSON 格式输出结果')
    
    args = parser.parse_args()
    
    tester = ProviderTester(
        api_key=args.api_key,
        base_url=args.url,
        api_type=args.type,
        model=args.model
    )
    
    result = tester.test()
    
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print_result(result)
    
    sys.exit(0 if result['success'] else 1)


if __name__ == '__main__':
    main()
