import json
from env import CLASS_NAME_MAPPING, API_JSON

def class_name_reshape(class_names):
    print("更換課程名稱排版")
    try:
        with open(CLASS_NAME_MAPPING, "r", encoding="utf-8") as file:
            print("偵測到已存在的mapping檔")
            class_data = json.load(file)
    except:
        class_data = generate_mapping_file(class_names)
    
    # 把課程名稱的行數一致化
    for k, v in class_data.items():
        v = str(v)
        while v.count("\n") < 2:
            v += "\n"
        class_data[k] = v
    
    return class_data
    

# 提取課程名稱，手動換行
def generate_mapping_file(class_names):
    # 取得 scheduleList
    schedule_list = class_names.get("data", {}).get("scheduleList", [])

    # 收集所有 name，去重複
    unique_names = {item.get("name", "") for item in schedule_list if item.get("name")}

    # 建立 key=value 的字典
    output_data = {name: name for name in unique_names}

    # 寫入新的 JSON 檔
    with open(CLASS_NAME_MAPPING, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"已產生 {CLASS_NAME_MAPPING}")
    print("請手動更改換行位置再重新執行一次")
    return output_data

if __name__ == "__main__":
    with open(API_JSON, "r", encoding="utf-8") as f:
        class_names = json.load(f)
    class_name_reshape(class_names)