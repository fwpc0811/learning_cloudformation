import boto3
import pytest
import time
import uuid
import json
import os  

# --- 設定値 ---
ENDPOINT_URL = os.getenv("TEST_ENDPOINT_URL", "http://localhost:4566")
REGION = "us-east-1"
BUCKET_NAME = "my-learning-bucket-12345"
LOG_GROUP_NAME = "/aws/lambda/my-learning-function"

# --- 前準備 ---
@pytest.fixture(scope="module")
def s3_client():
    """S3操作用のクライアントを作成"""
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        region_name=REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

@pytest.fixture(scope="module")
def logs_client():
    """CloudWatch Logs操作用のクライアントを作成"""
    return boto3.client(
        "logs",
        endpoint_url=ENDPOINT_URL,
        region_name=REGION,
        aws_access_key_id="test",
        aws_secret_access_key="test"
    )

# --- テスト本体 ---
def test_s3_upload_triggers_lambda(s3_client, logs_client):
    """
    S3にファイルをアップロードし、Lambdaがそれを処理したことをログから確認する
    """
    # 1. テスト用にユニークなファイル名を作る (衝突防止)
    unique_key = f"auto-test-{str(uuid.uuid4())}.txt"
    file_content = "Hello from Pytest!"

    print(f"\n[Test] Uploading file: {unique_key}")

    # 2. S3にアップロード (発火)
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=unique_key,
        Body=file_content
    )

    # 3. ログをポーリングして確認 (非同期処理なので最大30秒待つ)
    found = False
    start_time = time.time()
    timeout_seconds = 30

    print("[Test] Waiting for Lambda logs...")

    while time.time() - start_time < timeout_seconds:
        # ログイベントを取得
        try:
            response = logs_client.filter_log_events(
                logGroupName=LOG_GROUP_NAME,
                startTime=int(start_time * 1000) # テスト開始以降のログを見る
            )
            
            # ログの中から「今回アップロードしたファイル名」を探す
            for event in response.get('events', []):
                message = event['message']
                # Lambdaが "Success: ... {ファイル名} ..." と出力することを利用
                if unique_key in message and "Success" in message:
                    print(f"[Test] Found log: {message}")
                    found = True
                    break
            
            if found:
                break
            
        except logs_client.exceptions.ResourceNotFoundException:
            # Lambdaがまだ一度も動いていない場合、ロググループが存在しないことがある
            pass

        # まだ見つからなければ少し待って再確認
        time.sleep(2)

    # 4. 判定
    assert found, f"Time out! Lambda did not process the file '{unique_key}' within {timeout_seconds} seconds."