import requests
import time

from openai import OpenAI

def generate(n = 6):
    client = OpenAI(api_key="sk-48553c56c2494175a4aac1f422c51c74", base_url="https://api.deepseek.com")
    prompt =  '''你是一个专业的USPTO商标生成专家。请生成{n}个符合USPTO标准的商标名称。

生成规则：
1. 独特性强：避免过于通用或描述性的词汇，禁止使用现有的商标
2. 简短易记：长度在3-12个字符之间，通常2-3个音节
3. 易于发音和拼写：避免复杂的字母组合
4. 具有商业价值：听起来专业且有品牌潜力
5. 避免已知品牌：不要使用现有知名商标
6. 现代感：适合科技、创新类企业
7. 国际化：在不同语言中都易于理解

输出要求：
- 仅输出商标名称，每个名称占一行
- 不需要解释或额外说明
- 确保9个名称都是独特的
- 名称应该具有可注册性

请生成{n}个符合以上标准的商标名称：
'''
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "user", "content": prompt},
        ],
        stream=False
    )
    s = response.choices[0].message.content
    return [x.strip() for x in s.split('\n', -1)]

def is_available(wordmark):
    url = "https://tmsearch.uspto.gov/api-v1-0-0/tmsearch"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }

    cookies = {
        "aws-waf-token": "9529a4db-84bd-40ec-80c7-9cb8758412ea:EwoAxKwz7kD0AAAA:U6OU4qKhTSXXjmqdEkV/e4NG8diVWOrGwDlbnMUzP5mmL7aX65M1oWjovysMbGn34Q//1V6M0UK0l7ItJOtRck8pn+eEJiqYUP3rXYE6aHb4tbOJRnAMEguUZz6smggYABwtzhpW2Q+sJCf2yoWo6N4b17HyeTX6ed5lxDARncqX8Tx2vADK158snpD3zpdXDmDiZfZqTkdginnBA/vJCTwd8nBBTIo/22SEuzGPch/O0qLPcExexIsBDd9F5f+uWAZPkJFCjIA7"
    }

    payload = {
        "query": {
            "bool": {
                "must": [
                    {
                        "bool": {
                            "should": [
                                {"match_phrase": {"WM": {"query": wordmark, "boost": 5}}},
                                {"match": {"WM": {"query": wordmark, "boost": 2}}},
                                {"match_phrase": {"PM": {"query": wordmark, "boost": 2}}}
                            ]
                        }
                    }
                ]
            }
        },
        "aggs": {
            "alive": {"terms": {"field": "alive"}},
            "cancelDate": {"value_count": {"field": "cancelDate"}}
        },
        "size": 100,
        "from": 0,
        "track_total_hits": True,
        "_source": [
            "abandonDate", "alive", "attorney", "cancelDate", "coordinatedClass",
            "currentBasis", "drawingCode", "filedDate", "goodsAndServices", "id",
            "internationalClass", "markDescription", "markType", "ownerFullText",
            "ownerName", "ownerType", "priorityDate", "registrationDate",
            "registrationId", "registrationType", "supplementalRegistrationDate",
            "translate", "usClass", "wordmark", "wordmarkPseudoText"
        ]
    }
    # https://a434627cf98f.edge.sdk.awswaf.com/a434627cf98f/270cb27a30c2/telemetry
    response = requests.post(url,headers=headers,cookies=cookies, json=payload)
    if response.status_code != 200:
        print(response)
        raise ValueError(response.status_code)
    hits = response.json()['hits']
    ids = [item["id"] for item in hits['hits'] if item['source']['wordmark'] == wordmark.upper() and item['source']['alive']]
    return hits['totalValue'] < 10 and len(ids) == 0

if __name__ == '__main__':
    # got      Zentrix  
    # got      Vexora  
    # got      Truvora  
    # got      Nymblex  
    # got      Quorvia 
    is_available('Quivva')
    got = set()
    while len(got) < 5:
        items = generate(10)
        print('generate', items)
        for item in items:
            if is_available(item):
                print('is_available\t', item)
                got.add(item)
            time.sleep(1)
    print(got)
