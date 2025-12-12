import json
import sys
# ここでインポートに失敗する（LocalStackがLayerを展開できていないため）
try:
    from my_shared_lib import hello_from_layer
except ImportError:
    hello_from_layer = None

def lambda_handler(event, context):
    # デバッグ用にパスを出力しておく
    print("sys.path:", sys.path)
    
    if hello_from_layer:
        message = hello_from_layer()
    else:
        # Layer読み込み失敗時のメッセージ
        message = "FAILED to import layer. LocalStack could not mount /opt correctly."

    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": message,
            "python_path": sys.path
        })
    }