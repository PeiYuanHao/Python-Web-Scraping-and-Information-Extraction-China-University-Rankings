import requests
import re
import os

def download_payload_files():
    """下载2023-2025年的payload.js文件（绕过反爬）"""
    
    os.makedirs('payload_files', exist_ok=True)
    
    # 更完整的请求头，模拟真实浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    for year in [2023, 2024, 2025]:
        print(f"\n处理 {year} 年...")
        
        try:
            # 先用 session 保持连接
            session = requests.Session()
            session.headers.update(headers)
            
            # 先访问首页获取 cookies
            print(f"  访问首页获取cookie...")
            session.get('https://www.shanghairanking.cn', timeout=20)
            
            # 访问排名页面
            page_url = f'https://www.shanghairanking.cn/rankings/bcur/{year}'
            print(f"  访问: {page_url}")
            
            page = session.get(page_url, timeout=20)
            page.encoding = 'utf-8'
            html = page.text
            
            # 检查是否被拦截
            if '403' in html or 'denied' in html:
                print(f"  被拦截，尝试备用方案...")
                # 方案2：直接访问 payload.js 的常见路径模式
                # 从已知的 payload 路径模式尝试
                possible_paths = [
                    f'/_nuxt/static/rankings/bcur/{year}/payload.js',
                ]
                
                payload_content = None
                for path in possible_paths:
                    test_url = 'https://www.shanghairanking.cn' + path
                    print(f"  尝试: {test_url}")
                    resp = session.get(test_url, timeout=20)
                    if resp.status_code == 200 and 'univNameCn' in resp.text:
                        payload_content = resp.text
                        print(f"  ✓ 成功！")
                        break
                
                if not payload_content:
                    # 方案3：使用更真实的浏览器指纹
                    print(f"  使用增强版请求头...")
                    session.headers.update({
                        'Referer': page_url,
                        'Origin': 'https://www.shanghairanking.cn',
                        'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'same-origin',
                    })
                    page = session.get(page_url, timeout=20)
                    html = page.text
                    
                    # 重新提取路径
                    pattern = r'(/_nuxt/static/[^"\']+/rankings/bcur/' + str(year) + r'/payload\.js)'
                    match = re.search(pattern, html)
                    if match:
                        payload_url = 'https://www.shanghairanking.cn' + match.group(1)
                        print(f"  payload URL: {payload_url}")
                        payload_resp = session.get(payload_url, timeout=20)
                        payload_content = payload_resp.text
                    else:
                        print(f"  ✗ 未找到payload路径")
                        continue
                
                if payload_content:
                    filename = f'payload_files/payload_{year}.js'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(payload_content)
                    print(f"  ✓ 保存成功: {filename} ({len(payload_content)/1024:.1f} KB)")
                else:
                    print(f"  ✗ 下载失败")
                    
            else:
                # 正常提取路径
                pattern = r'(/_nuxt/static/[^"\']+/rankings/bcur/' + str(year) + r'/payload\.js)'
                match = re.search(pattern, html)
                if match:
                    payload_url = 'https://www.shanghairanking.cn' + match.group(1)
                    print(f"  payload URL: {payload_url}")
                    payload_resp = session.get(payload_url, timeout=20)
                    
                    filename = f'payload_files/payload_{year}.js'
                    with open(filename, 'w', encoding='utf-8') as f:
                        f.write(payload_resp.text)
                    print(f"  ✓ 保存成功: {filename} ({len(payload_resp.text)/1024:.1f} KB)")
                else:
                    print(f"  ✗ 未找到payload路径")
                    
        except Exception as e:
            print(f"  ✗ 错误: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("软科排名 Payload.js 下载工具（绕过反爬）")
    print("=" * 60)
    download_payload_files()
    print("\n完成！")