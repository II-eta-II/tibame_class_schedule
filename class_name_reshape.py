import json
from env import CLASS_NAME_MAPPING, API_JSON

def class_name_reshape(class_names):
    # class_name 是 rawdata
    # print("更換課程名稱排版")
    try:
        with open(CLASS_NAME_MAPPING, "r", encoding="utf-8") as file:
            print( f"偵測到已存在的mapping檔 {CLASS_NAME_MAPPING}")
            class_data = json.load(file)
        
        # 當 mapping 已經存在又新增課程名稱時
        # 把課程名稱提取出來並作為相同就格式(與下方重複，待整理)
        schedule_list = class_names.get("data", {}).get("scheduleList", [])
        unique_names = {item.get("name", "") for item in schedule_list if item.get("name")}
        output_data = {name: name for name in unique_names}

        # 找出新增的課程名稱
        diff_class = {k: output_data[k] for k in output_data if k not in class_data}

        if diff_class:
            print("偵測到新增課程:")
            for k,v in diff_class.items():
                print(f"- {k}")
            print("請修改排版再重新執行。")
            for key in diff_class.keys():
                class_data[key] = diff_class[key]
            with open(CLASS_NAME_MAPPING, "w", encoding="utf-8") as file:
                json.dump(class_data, file, ensure_ascii=False, indent=2)
    except:
        print("課程名稱排版檔案不存在。")
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
    # class_name 是 rawdata

    # 取得 scheduleList
    schedule_list = class_names.get("data", {}).get("scheduleList", [])

    # 收集所有 name，去重複
    unique_names = {item.get("name", "") for item in schedule_list if item.get("name")}

    # 建立 key=value 的字典
    output_data = {name: name for name in unique_names}

    # 寫入新的 JSON 檔
    with open(CLASS_NAME_MAPPING, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"已建立 {CLASS_NAME_MAPPING} 對照表，")
    print("請手動更改換行位置再重新執行一次。")
    return output_data

if __name__ == "__main__":
    with open(API_JSON, "r", encoding="utf-8") as f:
        class_names = json.load(f)
    class_name_reshape(class_names)