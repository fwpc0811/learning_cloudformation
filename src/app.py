import json
import os
import sys

def handler(event, context):
    print("--- DEBUG START ---")
    
    # 1. どこから読み込もうとしているか確認
    print(f"sys.path: {sys.path}")
    
    # 2. 実際に /opt フォルダに何があるか全表示
    print("Listing files in /opt:")
    for root, dirs, files in os.walk("/opt"):
        for file in files:
            print(os.path.join(root, file))
            
    print("--- DEBUG END ---")

    # 3. ここでインポートを試す (エラーになってもログは残る)
    try:
        import my_utils
        msg = my_utils.hello_from_layer()
        print(f"★SUCCESS: {msg}")
        return {"statusCode": 200, "body": msg}
        
    except ImportError as e:
        print(f"★FAILED: {e}")
        # 失敗してもログが見たいので、あえて正常終了(200)として返す
        return {"statusCode": 200, "body": f"ImportError: {str(e)}"}
    except Exception as e:
        print(f"★ERROR: {e}")
        return {"statusCode": 200, "body": str(e)}