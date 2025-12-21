import streamlit as st
import requests

# 设置页面标题
st.title('小Yv牌聊天机器人')

# 用户输入
user_input = st.text_input('请输入您的问题：', '')

# 如果用户输入了问题
if user_input:
    # 调用外部API获取回复
    try:
        api_endpoint = "fa7d7512945e4e27bf0a1650a7daf1b0.1HOcwRm3HIlK4ZgI"  # 替换为实际的API URL
        headers = {
            "Authorization": f"Bearer fa7d7512945e4e27bf0a1650a7daf1b0.1HOcwRm3HIlK4ZgI",  # 替换为实际的API密钥
            "Content-Type": "application/json"
        }
        data = {
            "prompt": user_input
        }
        response = requests.post(api_endpoint, headers=headers, json=data)
        
        # 检查响应状态码
        if response.status_code == 200:
            assistant_response = response.json().get('reply', '未能获取回复')
            st.write('机器人回答：', assistant_response)
        else:
            st.error('API调用失败，状态码：', response.status_code)
    except Exception as e:
        st.error('发生错误：', str(e))