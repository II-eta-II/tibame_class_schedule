import requests
import json
import base64
from env import API_JSON, CLASS_START, CLASS_END

PASSWORD_FILE = "password.json"

def get_schedule(from_file=False):

    # 測試用，不必每次都爬網頁
    if from_file:
        data = None
        with open(API_JSON, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data
        if data is None:
            print("檔案讀取失敗，重新下載課表")
        
    # API網址
    url = "https://api-c2c.tibame.com/v1/c2c/schedule/student/schedule-list"
    
    # 讀取 password.json 並產生 token
    try:
        with open(PASSWORD_FILE, "r", encoding="utf-8") as file:
            password_data = json.load(file)
        token = base64.b64encode(json.dumps(password_data).encode()).decode()
    except FileNotFoundError:
        print(f"無法讀取 {PASSWORD_FILE}，請檢查檔案是否存在。")
        print("查閱 README 取得正確設置方式。")
        return None

    # 參數設定，設定擷取時間範圍
    params = {
        "fromDate": CLASS_START,
        "toDate": CLASS_END
    }

    # 標頭，只需要帶入token即可
    headers = {
        "accept":"*/*",
        "accept-encoding":"gzip, deflate, br, zstd",
        "accept-language":"zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7",
        "class-token":token,
        "connection":"keep-alive",
        "content-type":"application/json",
        "host":"api-c2c.tibame.com",
        "origin":"https://www.tibame.com",
        "referer":"https://www.tibame.com/curriculum/class",
        "sec-ch-ua":'"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        "sec-ch-ua-mobile":"?0",
        "sec-ch-ua-platform":"Windows",
        "sec-fetch-dest":"empty",
        "sec-fetch-mode":"cors",
        "sec-fetch-site":"same-site",
        "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    }

    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        print("成功取得課表資訊")
        with open(API_JSON, "w", encoding="utf-8") as file:
            json.dump(response.json(), file, indent=2, ensure_ascii=False)
        return response.json()
    else:
        print(response.status_code)
        print("取得課表資訊失敗")
        return None

if __name__ == "__main__":
    print(f"單獨測試 get_schedule")
    get_schedule()
