#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Model Provider Connectivity Tester - Web UI
基于 Streamlit 的模型 Provider 连通性测试工具
"""

import streamlit as st
import time
import json
from typing import Optional, Dict, Any, List
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed


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
        
        return test_methods[self.api_type]()


# Streamlit UI
def fetch_model_list(api_url: str) -> Dict[str, Any]:
    """从 API 获取模型列表"""
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {"error": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def batch_test_models(base_url: str, api_key: str, api_type: str, models: List[str], max_workers: int = 5) -> List[Dict[str, Any]]:
    """批量测试多个模型"""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_model = {
            executor.submit(
                ProviderTester(api_key, base_url, api_type, model).test
            ): model 
            for model in models
        }
        
        for future in as_completed(future_to_model):
            model = future_to_model[future]
            try:
                result = future.result()
                result['model'] = model
                results.append(result)
            except Exception as e:
                results.append({
                    'model': model,
                    'success': False,
                    'message': '❌ 测试异常',
                    'error': str(e)
                })
    
    return sorted(results, key=lambda x: x['model'])


def single_point_test():
    """单点测试界面"""
    # 主区域 - 常见配置示例
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📝 常见 Provider 配置")
        
        with st.expander("🔹 Anthropic Official"):
            st.code("""
API 类型: anthropic
地址: https://api.anthropic.com
模型: claude-3-sonnet-20240229
            """, language="text")
        
        with st.expander("🔹 OpenAI Official"):
            st.code("""
API 类型: openai
地址: https://api.openai.com
模型: gpt-4
            """, language="text")
        
        with st.expander("🔹 Google Gemini"):
            st.code("""
API 类型: google
地址: https://generativelanguage.googleapis.com
模型: gemini-pro
            """, language="text")
    
    with col2:
        st.subheader("💡 使用说明")
        st.markdown("""
        1. 在左侧选择 API 类型
        2. 输入 Provider 地址（只填基础地址）
        3. 输入你的 API Key
        4. 可选：指定模型名称
        5. 点击"开始测试"
        
        **提示：**
        - API Key 不会被保存或上传
        - 测试请求只发送最小 payload（max_tokens=10）
        - 响应时间包含网络延迟
        """)
    
    st.divider()
    
    # 获取侧边栏配置
    config = st.session_state.get('single_config', {})
    base_url = config.get('base_url', '')
    api_key = config.get('api_key', '')
    api_type = config.get('api_type', 'anthropic')
    model = config.get('model', '')
    test_button = config.get('test_button', False)
    
    # 测试结果区域
    if test_button:
        if not base_url or not api_key:
            st.error("⚠️ 请填写 Provider 地址和 API Key")
            return
        
        with st.spinner("🔍 测试中..."):
            tester = ProviderTester(
                api_key=api_key,
                base_url=base_url,
                api_type=api_type,
                model=model if model else None
            )
            
            result = tester.test()
        
        # 显示结果
        if result['success']:
            st.success(result['message'])
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("状态码", result['status_code'])
            with col2:
                st.metric("响应时间", f"{result['response_time']}s")
            with col3:
                st.metric("状态", "✅ 正常")
            
            st.info(f"**请求地址:** `{result['url']}`")
            
            if 'response_preview' in result:
                with st.expander("📄 查看响应详情"):
                    st.json(result['response_preview'])
        
        else:
            st.error(result['message'])
            
            col1, col2 = st.columns(2)
            with col1:
                if 'status_code' in result:
                    st.metric("状态码", result['status_code'])
            with col2:
                st.metric("响应时间", f"{result['response_time']}s")
            
            if 'url' in result:
                st.info(f"**请求地址:** `{result['url']}`")
            
            if 'error' in result:
                st.subheader("❌ 错误详情")
                if isinstance(result['error'], dict):
                    st.json(result['error'])
                else:
                    st.code(result['error'], language="text")


def single_point_sidebar():
    """单点测试侧边栏"""
    with st.sidebar:
        st.header("⚙️ 单点配置")
        
        api_type = st.selectbox(
            "API 类型",
            options=['anthropic', 'openai', 'google'],
            help="选择 Provider 使用的 API 格式",
            key="single_api_type"
        )
        
        base_url = st.text_input(
            "Provider 地址",
            placeholder="https://api.example.com",
            help="不要包含 /v1/messages 等路径，只填基础地址",
            key="single_base_url"
        )
        
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="sk-...",
            help="你的 API 密钥",
            key="single_api_key"
        )
        
        # 默认模型提示
        default_models = {
            'anthropic': 'claude-3-haiku-20240307',
            'openai': 'gpt-3.5-turbo',
            'google': 'gemini-pro'
        }
        
        model = st.text_input(
            "模型名称（可选）",
            placeholder=default_models.get(api_type, ''),
            help=f"留空则使用默认: {default_models.get(api_type, '')}",
            key="single_model"
        )
        
        st.divider()
        
        test_button = st.button("🚀 开始测试", type="primary", use_container_width=True, key="single_test_btn")
        
        # 保存配置到 session_state
        st.session_state['single_config'] = {
            'api_type': api_type,
            'base_url': base_url,
            'api_key': api_key,
            'model': model,
            'test_button': test_button
        }


def batch_test_sidebar():
    """批量测试侧边栏"""
    with st.sidebar:
        st.header("⚙️ 批量配置")
        
        # 手动刷新按钮
        if st.button("🔄 刷新模型列表", use_container_width=True, key="refresh_models_btn"):
            MODEL_LIST_API = "https://api.taijiaicloud.com/api/pricing"
            with st.spinner("正在刷新模型列表..."):
                data = fetch_model_list(MODEL_LIST_API)
            
            if 'error' in data:
                st.error(f"❌ 刷新失败: {data['error']}")
            else:
                st.session_state['model_data'] = data
                st.session_state['model_data_loaded'] = True
                st.success(f"✅ 成功刷新 {len(data.get('data', []))} 个模型")
        
        st.divider()
        
        base_url = st.text_input(
            "Provider 地址",
            placeholder="https://api.example.com",
            help="测试用的 Provider 基础地址",
            key="batch_base_url"
        )
        
        api_key = st.text_input(
            "API Key",
            type="password",
            placeholder="sk-...",
            help="你的 API 密钥",
            key="batch_api_key"
        )
        
        api_type = st.selectbox(
            "API 类型",
            options=['anthropic', 'openai', 'google'],
            help="选择 Provider 使用的 API 格式",
            key="batch_api_type"
        )
        
        max_workers = st.slider(
            "并发数",
            min_value=1,
            max_value=10,
            value=5,
            help="同时测试的模型数量",
            key="batch_max_workers"
        )
        
        # 保存配置到 session_state
        st.session_state['batch_config'] = {
            'base_url': base_url,
            'api_key': api_key,
            'api_type': api_type,
            'max_workers': max_workers
        }


def batch_test():
    """批量测试界面"""
    # 内置 API 地址，不暴露给用户
    MODEL_LIST_API = "https://api.taijiaicloud.com/api/pricing"
    
    # 初始化 session_state
    if 'model_data_loaded' not in st.session_state:
        st.session_state['model_data_loaded'] = False
    
    # 自动加载模型列表（仅首次）
    if not st.session_state['model_data_loaded']:
        with st.spinner("正在加载模型列表..."):
            data = fetch_model_list(MODEL_LIST_API)
        
        if 'error' not in data:
            st.session_state['model_data'] = data
            st.session_state['model_data_loaded'] = True
    
    # 主区域
    st.subheader("📋 模型选择")
    
    if 'model_data' not in st.session_state:
        st.warning("⚠️ 模型列表加载失败，请点击左侧「刷新模型列表」重试")
        return
    
    data = st.session_state['model_data']
    models_list = data.get('data', [])
    auto_groups = data.get('auto_groups', [])
    
    # 按 Provider 分组展示
    st.markdown("**选择要测试的模型：**")
    
    # 初始化选择状态 - 改用 list 存储，包含 group 信息
    if 'selected_models_list' not in st.session_state:
        st.session_state['selected_models_list'] = []
    
    # 全选/取消全选
    col1, col2 = st.columns([1, 5])
    with col1:
        select_all = st.checkbox("全选", key="select_all_checkbox")
    with col2:
        if st.button("清空选择", key="clear_selection_btn"):
            st.session_state['selected_models_list'] = []
            st.rerun()
    
    # 按 Provider 分组
    provider_groups = {}
    for model in models_list:
        for group in model.get('enable_groups', []):
            if group not in provider_groups:
                provider_groups[group] = []
            provider_groups[group].append({
                'name': model['model_name'],
                'icon': model.get('icon', ''),
                'description': model.get('description', '')
            })
    
    # 显示分组选择器
    for group in auto_groups:
        if group in provider_groups:
            with st.expander(f"📦 {group} ({len(provider_groups[group])} 个模型)"):
                models_in_group = provider_groups[group]
                
                # 每行显示 3 个
                for i in range(0, len(models_in_group), 3):
                    cols = st.columns(3)
                    for j, col in enumerate(cols):
                        if i + j < len(models_in_group):
                            model_info = models_in_group[i + j]
                            model_name = model_info['name']
                            
                            # 唯一标识：group + model_name
                            model_id = f"{group}::{model_name}"
                            
                            with col:
                                # 使用唯一的 key
                                checkbox_key = f"cb_{group}_{i}_{j}"
                                is_checked = select_all or model_id in st.session_state['selected_models_list']
                                
                                if st.checkbox(
                                    model_name,
                                    value=is_checked,
                                    key=checkbox_key
                                ):
                                    if model_id not in st.session_state['selected_models_list']:
                                        st.session_state['selected_models_list'].append(model_id)
                                else:
                                    if model_id in st.session_state['selected_models_list']:
                                        st.session_state['selected_models_list'].remove(model_id)
    
    # 获取最终选择的模型列表
    selected_models = st.session_state['selected_models_list']
    
    st.divider()
    
    # 显示已选择的模型
    if selected_models:
        st.info(f"✅ 已选择 {len(selected_models)} 个模型")
        
        # 显示选中的模型名称（可折叠）
        with st.expander("📋 查看已选择的模型", expanded=False):
            for model_id in sorted(selected_models):
                group, model_name = model_id.split("::", 1)
                st.write(f"- **{group}**: {model_name}")
        
        test_button = st.button("🚀 开始批量测试", type="primary", key="batch_test_btn")
        
        if test_button:
            # 获取配置
            config = st.session_state.get('batch_config', {})
            base_url = config.get('base_url', '')
            api_key = config.get('api_key', '')
            api_type = config.get('api_type', 'anthropic')
            max_workers = config.get('max_workers', 5)
            
            if not base_url or not api_key:
                st.error("⚠️ 请填写 Provider 地址和 API Key")
                return
            
            # 解析选择的模型（去掉 group 前缀，只保留模型名）
            model_names = [m.split("::", 1)[1] for m in selected_models]
            
            st.subheader("📊 测试进度")
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner("正在批量测试..."):
                results = batch_test_models(
                    base_url=base_url,
                    api_key=api_key,
                    api_type=api_type,
                    models=model_names,
                    max_workers=max_workers
                )
            
            progress_bar.progress(100)
            status_text.text(f"✅ 测试完成！共测试 {len(results)} 个模型")
            
            # 统计结果
            success_count = sum(1 for r in results if r['success'])
            fail_count = len(results) - success_count
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("总数", len(results))
            with col2:
                st.metric("成功", success_count, delta=None if success_count == 0 else "✅")
            with col3:
                st.metric("失败", fail_count, delta=None if fail_count == 0 else "❌")
            
            st.divider()
            st.subheader("📋 详细结果")
            
            # 结果表格 - 状态码显示在标题
            for idx, r in enumerate(results):
                status_indicator = "✅" if r['success'] else "❌"
                status_code_str = f" [{r['status_code']}]" if 'status_code' in r else ""
                title = f"{status_indicator} {r['model']}{status_code_str} - {r['message']}"
                
                with st.expander(title, expanded=False):
                    col1, col2 = st.columns([1, 3])
                    
                    with col1:
                        st.metric("状态", "成功" if r['success'] else "失败")
                        if 'response_time' in r:
                            st.metric("响应时间", f"{r['response_time']}s")
                    
                    with col2:
                        # 显示请求信息
                        st.markdown("**📤 请求信息：**")
                        request_info = {
                            "模型": r['model'],
                            "API类型": api_type,
                            "Provider": base_url,
                            "请求URL": r.get('url', 'N/A')
                        }
                        st.json(request_info)
                        
                        # 显示响应详情
                        if r['success'] and 'response_preview' in r:
                            st.markdown("**📥 响应详情：**")
                            st.json(r['response_preview'])
                        elif 'error' in r:
                            st.markdown("**❌ 错误详情：**")
                            if isinstance(r['error'], dict):
                                st.json(r['error'])
                            else:
                                st.code(r['error'], language="text")
    else:
        st.warning("⚠️ 请至少选择一个模型进行测试")


def main():
    st.set_page_config(
        page_title="Model Provider Tester",
        page_icon="🔍",
        layout="wide",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )
    
    # 隐藏 Deploy 按钮和右上角菜单
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stDeployButton {display:none;}
        </style>
        """, unsafe_allow_html=True)
    
    st.title("🔍 Model Provider 连通性测试")
    st.markdown("测试自定义模型 Provider 的连通性，支持 Anthropic、OpenAI、Google 格式")
    
    st.divider()
    
    # 根据当前模式显示对应内容
    current_mode = st.session_state.get('rendering_tab', 'single')
    
    if current_mode == 'single':
        single_point_test()
    else:
        batch_test()
    
    # 页脚
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray; font-size: 0.9em;'>
        Made with ❤️ | 支持 Anthropic / OpenAI / Google API 格式 | 批量测试功能
    </div>
    """, unsafe_allow_html=True)


def run():
    """主运行函数 - 处理侧边栏和内容的协调"""
    # 初始化默认选项卡
    if 'rendering_tab' not in st.session_state:
        st.session_state['rendering_tab'] = 'single'
    
    current_mode = st.session_state['rendering_tab']
    
    # 侧边栏切换按钮
    st.sidebar.header("🎛️ 测试模式")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button(
            "🎯 单点",
            use_container_width=True,
            key="switch_single",
            type="primary" if current_mode == 'single' else "secondary"
        ):
            st.session_state['rendering_tab'] = 'single'
            st.rerun()
    with col2:
        if st.button(
            "📊 批量",
            use_container_width=True,
            key="switch_batch",
            type="primary" if current_mode == 'batch' else "secondary"
        ):
            st.session_state['rendering_tab'] = 'batch'
            st.rerun()
    
    st.sidebar.divider()
    
    # 根据当前选项卡显示对应侧边栏
    if current_mode == 'single':
        single_point_sidebar()
    else:
        batch_test_sidebar()
    
    # 显示主内容
    main()


if __name__ == '__main__':
    run()
