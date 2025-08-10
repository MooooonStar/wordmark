from playwright.sync_api import sync_playwright
import requests

if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # 无头浏览器
        context = browser.new_context()
        page = context.new_page()
        
        # 访问 USPTO 主站，触发 telemetry & cookie 设置
        page.goto("https://tmsearch.uspto.gov")
        page.wait_for_timeout(3000)  # 等 3 秒让 JS 脚本跑完
        
        # 提取 cookie
        cookies = context.cookies()
        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in cookies])
        print("[*] 获取的 Cookie:", cookie_str)

        # 用 Python requests 带 Cookie 请求 tmsearch API
        headers = {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "origin": "https://tmsearch.uspto.gov",
            "referer": "https://tmsearch.uspto.gov/search/search-results",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }

        payload = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "bool": {
                                "should": [
                                    {"query_string": {"query": "Yondra*", "default_operator": "AND", "fields": [
                                        "goodsAndServices","markDescription","ownerName","translate","wordmark","wordmarkPseudoText"
                                    ]}}
                                ]
                            }
                        }
                    ]
                }
            },
            "size": 1
        }

        resp = requests.post(
            "https://tmsearch.uspto.gov/api-v1-0-0/tmsearch",
            headers=headers,
            cookies={c["name"]: c["value"] for c in cookies},
            json=payload
        )

        print(resp.status_code, resp.text[:500])
        browser.close()
