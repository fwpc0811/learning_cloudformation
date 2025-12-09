import json

def handler(event, context):
    # バッチサイズの確認
    count = len(event['Records'])
    print(f"Lambda started! Batch size: {count}")
    
    for record in event['Records']:
        payload = record['body']
        
        # エラー実験
        if "error" in payload:
            print("!!! ERROR DETECTED !!! Crashing...")
            raise Exception("Planned Failure")
        
        print(f"Success: {payload}")
    
    return {"statusCode": 200}