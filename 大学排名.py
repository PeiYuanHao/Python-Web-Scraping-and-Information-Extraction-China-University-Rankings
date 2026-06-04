import requests
from bs4 import BeautifulSoup
import re

def format_chinese(text, width):
    text = str(text)
    chinese_count = 0

    for ch in text:
        if '\u4e00' <= ch <= '\u9fff':
            chinese_count += 1

    return "{:<{}}".format(text, width - chinese_count)  # 少补一些空格，抵消中文 多占的宽度

# 要求 2
# 显示 2023 2024 2025 三年的中国大学排名
def get_rank(year):
    # 爬取网址
    url = f'https://www.shanghairanking.cn/rankings/bcur/{year}'

    # 用requests 库中的 get 函数向网址发送一次 HTTP GET 请求，获取网页内容。
    r = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'})  # headers 给请求添加请求头 参数伪装成浏览器访问网站，避免网站认为这是程序爬虫而拒绝访问。
    r.encoding = 'utf-8'
    html = r.text

    soup = BeautifulSoup(html, 'html.parser')  # 解析 html
    row = soup.find('table').find_all('tr')  # 找出每一行

    # 表头
    print("{}中国大学排名".format(year))
    print("{}{}{}{}".format(
        format_chinese('排名', 8),
        format_chinese('学校名称', 24),
        format_chinese('总分', 10),
        format_chinese('科学研究', 10)
    ))

    res = 0

    # 解析查找到的若干学校
    for i in row:
        t = i.find_all('td')

        if len(t) >= 6:  # 保证一定是满足要求的行
            rank = re.sub(r'\s+', '', t[0].get_text(strip=True))  # 使用正则化，去掉任意空白字符
            name = re.sub(r'\s+', '', t[1].find('span').get_text(strip=True))
            score = re.sub(r'\s+', '', t[4].get_text(strip=True))
            research = re.sub(r'\s+', '', t[5].get_text(strip=True))

            res += 1  # 计数

            print("{}{}{}{}".format(
                format_chinese(rank, 8),
                format_chinese(name, 24),
                format_chinese(score, 10),
                format_chinese(research, 10)
            ))
    return res

# 要求 3
def threeyearsrank(n):
    schools = {}

    for year in [2023, 2024, 2025]:
        # 学科水平 / 科学研究 / 人才培养 在右侧菜单里分别对应
        subject_code, research_code, talent_code = {
            2023: ('412', '416', '415'),
            2024: ('537', '541', '540'),
            2025: ('652', '656', '655')
        }[year]

        page_url = f'https://www.shanghairanking.cn/rankings/bcur/{year}'
        page = requests.get(page_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=20)
        page.encoding = 'utf-8'
        html = page.text

        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find('table').find_all('tr')

        # 抓取页面中提到的 payload.js，里面包含所有大学的各指标分数
        payload_path = re.search(r'(/_nuxt/static/[^"\']+/rankings/bcur/' + str(year) + r'/payload\.js)', html).group(1)
        payload = requests.get('https://www.shanghairanking.cn' + payload_path,
                               headers={'User-Agent': 'Mozilla/5.0', 'Referer': page_url},
                               timeout=20).text

        # 从 payload 里逐个学校提取 学科水平 / 科学研究 / 人才培养 三项
        for tr in rows:
            tds = tr.find_all('td')
            if len(tds) < 6:
                continue
            name = re.sub(r'\s+', '', tds[1].find('span').get_text(strip=True))

            # 在 payload 中查找当前学校对应的 univUp 字段
            univ_match = re.search(r'univUp:"([^"]+)",[^}]*univNameCn:"' + re.escape(name) + '"', payload)  # 存储的是从 payload 中匹配到的大学标识信息
            block = re.search(r'univUp:"' + re.escape(univ_match.group(1)) + r'".*?indData:\{([^}]*)\}', payload)  # 存储该大学的详细分数数据块
            if not block:
                continue

            # 解析分数到字典
            scores = {}
            for item in block.group(1).split(','):  # 分割成列表 ['"412":"85.1"', '"416":"91.2"', '"415":"88.5"']
                k, v = item.split(':')
                v = v.strip().strip('"')  # v.strip() 去除首尾空白, .strip('"') 去除首尾的双引号
                if v.endswith('%'):
                    v = v[:-1]  # v[:-1] 去掉最后一个字符, 实际上是去掉百分号
                if v == '' or v == '-':  # 无数据
                    v = '0'
                try:
                    scores[k.strip('"')] = float(v)  # k.strip('"') 去掉键的双引号，得到纯代码 "412" to 412
                except:
                    scores[k.strip('"')] = 0

            subject = scores.get(subject_code, 0)
            research = scores.get(research_code, 0)
            talent = scores.get(talent_code, 0)
            total = subject + research + talent

            if name not in schools:
                schools[name] = 0
            schools[name] += total

    result = sorted(schools.items(), key=lambda x: x[1], reverse=True)  # 转换为元组列表 降序

    print("2023-2025中国大学三年综合排名")
    print("{}{}{}".format(
        format_chinese('排名', 8),
        format_chinese('学校名称', 24),
        format_chinese('综合总分', 10)
    ))

    for i in range(min(n, len(result))):
        print("{}{}{}".format(
            format_chinese(i + 1, 8),
            format_chinese(result[i][0], 24),
            format_chinese("{:.1f}".format(result[i][1]), 10)
        ))
    
# 要求 4
def get_stock():
    urls = {
        '沪市': 'http://www.cgedt.com/stockcode/hushi.asp',
        '深市': 'http://www.cgedt.com/stockcode/shenshi.asp'
    }

    for name, url in urls.items():
        # 爬取网址
        r = requests.get(url, headers = {'User-Agent': 'Mozilla/5.0'}, timeout = 10)
        r.encoding = 'gb2312'
        html = r.text

        # 使用正则表达式查找 6 位股票代码
        stocks = re.findall(r'\d{6}', html)  # re.findall() 在HTML中查找所有匹配的内容, r'\d{6}' 匹配连续6个数字

        # 去重，并保持原来的顺序
        res = []  # 列表 存储去重后的结果
        used = set()  # 集合 记录已经出现过的股票代码
        for stock in stocks:
            if stock not in used:
                res.append(stock)  # 将元素添加到列表末尾
                used.add(stock)  # 将元素添加到集合中

        print("{}股票代码，共{}个".format(name, len(res)))
        for stock in res:
            print(stock)

# 要求 5
def pair_stock():
    n = int(input('请输入要匹配的大学数量：'))

    # 先从要求 4 的两个网址中爬取全部股票代码
    stock_urls = [
        'http://www.cgedt.com/stockcode/hushi.asp',
        'http://www.cgedt.com/stockcode/shenshi.asp'
    ]

    session = requests.Session()

    stocks = []
    used = set()
    for url in stock_urls:
        r = session.get(url, headers = {'User-Agent': 'Mozilla/5.0'}, timeout = 20)
        r.encoding = 'gb2312'
        html = r.text

        temp = re.findall(r'\d{6}', html)
        for stock in temp:
            if stock not in used:
                stocks.append(stock)
                used.add(stock)

    # 随机选取 n 支股票代码
    import random
    stock_result = random.sample(stocks, n)  # 随机

    # 再计算 2023、2024、2025 三年大学综合排名
    schools = {}
    ind_codes = {
        2023: ('412', '416', '415'),
        2024: ('537', '541', '540'),
        2025: ('652', '656', '655')
    }

    for year in [2023, 2024, 2025]:
        subject_code, research_code, talent_code = ind_codes[year]

        url = f'https://www.shanghairanking.cn/rankings/bcur/{year}'
        r = session.get(url, headers = {'User-Agent': 'Mozilla/5.0'}, timeout = 20)
        r.encoding = 'utf-8'
        html = r.text

        soup = BeautifulSoup(html, 'html.parser')
        rows = soup.find('table').find_all('tr')

        payload_path = re.search(r'(/_nuxt/static/[^"\']+/rankings/bcur/' + str(year) + r'/payload\.js)', html).group(1)
        payload_url = 'https://www.shanghairanking.cn' + payload_path
        r = session.get(payload_url, headers = {'User-Agent': 'Mozilla/5.0', 'Referer': url}, timeout = 20)
        payload = r.text

        for tr in rows:
            tds = tr.find_all('td')
            if len(tds) < 6:
                continue

            name = re.sub(r'\s+', '', tds[1].find('span').get_text(strip=True))

            univ_match = re.search(r'univUp:"([^"]+)",[^}]*univNameCn:"' + re.escape(name) + '"', payload)
            if not univ_match:
                continue

            block = re.search(r'univUp:"' + re.escape(univ_match.group(1)) + r'".*?indData:\{([^}]*)\}', payload)
            if not block:
                continue

            scores = {}
            for item in block.group(1).split(','):
                k, v = item.split(':')
                v = v.strip().strip('"')

                if v.endswith('%'):
                    v = v[:-1]
                if v == '' or v == '-':
                    v = '0'

                try:
                    scores[k.strip('"')] = float(v)
                except:
                    scores[k.strip('"')] = 0

            subject = scores.get(subject_code, 0)
            research = scores.get(research_code, 0)
            talent = scores.get(talent_code, 0)
            total = subject + research + talent

            if name not in schools:
                schools[name] = 0
            schools[name] += total

    result = sorted(schools.items(), key = lambda x: x[1], reverse = True)

    print("2023-2025年中国大学排名（前{}）".format(n))
    print("{}{}{}{}".format(
        format_chinese('排名', 8),
        format_chinese('学校名称', 24),
        format_chinese('总分', 10),
        format_chinese('股票代码', 10)
    ))

    for i in range(n):
        print("{}{}{}{}".format(
            format_chinese(i + 1, 8),
            format_chinese(result[i][0], 24),
            format_chinese("{:.1f}".format(result[i][1]), 10),
            format_chinese(stock_result[i], 10)  # 输出
        ))

def main():
    for year in [2023, 2024, 2025]:
        num = get_rank(year)
    threeyearsrank(num)
    get_stock()
    pair_stock()

if __name__ == "__main__":
    main()