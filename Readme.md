````markdown
# AWS CloudFormation Learning Environment (LocalStack)

AWS CloudFormation を使用して、**IaC (Infrastructure as Code)** を学習するための環境です。
LocalStack を使用しているため、AWS利用料をかけずにローカルPC上でインフラ構築の練習ができます。

## アーキテクチャ

以下の **イベント駆動アーキテクチャ** を CloudFormation で自動構築します。

**S3 (ファイル配置) → EventBridge (検知) → SQS (キューイング) → Lambda (処理)**

1. **S3**: ファイルがアップロードされる (`Object Created`)
2. **EventBridge**: S3のイベントを検知し、SQSへルーティング
3. **SQS**: メッセージを一時的に保持し、Lambdaへ渡す
4. **Lambda**: Python 3.9 で起動し、受け取ったメッセージ内容をログに出力

## 前提条件

* Docker Desktop がインストールされ、起動していること
* AWS CLI がインストールされていること

## 環境構築 & 実行手順

### 1. LocalStack の起動
プロジェクトのルートディレクトリで以下のコマンドを実行し、仮想AWS環境を立ち上げます。
(初回はイメージのダウンロードに時間がかかります)

```powershell
docker-compose up -d
````

### 2\. AWS CLI の設定 (初回のみ)

LocalStack用のダミー認証情報を設定します。

```powershell
aws configure --profile localstack
```

  * **AWS Access Key ID**: `test`
  * **AWS Secret Access Key**: `test`
  * **Default region name**: `us-east-1`
  * **Default output format**: `json`

### 3\. インフラのデプロイ

用意されたスクリプトを実行して、CloudFormationスタックを作成します。
このスクリプトは「既存スタックの削除 → 新規作成 → S3バケット確認」を自動で行います。

```powershell
.\deploy.ps1
```

> **Note**
> スクリプト実行時に「セキュリティエラー」が出る場合は、一時的に実行を許可してください。
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`

## 動作テスト

インフラが正しく動いているか確認します。

**1. テスト用ファイルの作成**

```powershell
echo "Test Message" > test_file.txt
```

**2. S3へアップロード (発火)**

```powershell
aws s3 cp test_file.txt s3://my-learning-bucket-12345/test_file.txt --endpoint-url=http://localhost:4566 --profile localstack
```

**3. Lambdaログの確認 (結果確認)**
Lambdaが起動し、処理が行われたかを確認します。

```powershell
aws logs tail "/aws/lambda/my-learning-function" --endpoint-url=http://localhost:4566 --profile localstack
```

ログに `Lambda started!` や `Received message:` が表示されていれば成功です。

## ディレクトリ構成

```text
.
├── docker-compose.yml   # LocalStackの設定 (S3, Lambda, CloudFormationなどを有効化)
├── deploy.ps1           # デプロイ自動化スクリプト (PowerShell)
├── templates/           # CloudFormationテンプレート置き場
│   └── s3_eventbridge.yaml  # 今回作成した設計図
└── volume/              # LocalStackのデータ保存場所 (Git管理外)
```

## 環境を停止・削除

以下のコマンドで環境を停止・削除します。

```powershell

# スタックの削除
aws cloudformation delete-stack --stack-name my-stack --endpoint-url=http://localhost:4566 --profile localstack

# コンテナの停止
docker-compose down
```



# バッチサイズ実験
```
echo "Batch 1" > b1.txt
echo "Batch 2" > b2.txt
echo "Batch 3" > b3.txt
echo "Batch 4" > b4.txt
echo "Batch 5" > b5.txt
```

# 5連続アップロード (& はコマンド連結)
```
aws s3 cp b1.txt s3://my-learning-bucket-12345/b1.txt --endpoint-url=http://localhost:4566 --profile localstack ; aws s3 cp b2.txt s3://my-learning-bucket-12345/b2.txt --endpoint-url=http://localhost:4566 --profile localstack ; aws s3 cp b3.txt s3://my-learning-bucket-12345/b3.txt --endpoint-url=http://localhost:4566 --profile localstack ; aws s3 cp b4.txt s3://my-learning-bucket-12345/b4.txt --endpoint-url=http://localhost:4566 --profile localstack ; aws s3 cp b5.txt s3://my-learning-bucket-12345/b5.txt --endpoint-url=http://localhost:4566 --profile localstack
```

# バッチサイズが2以上（Batch size: 2）であれば、並列で動いている
```
2025-12-08T07:01:34.323000+00:00 2025/12/08/[$LATEST]0e761b7bb3298c7d88a37c85e243a7a6 Lambda started! Batch size: 2
2025-12-08T07:01:34.323000+00:00 2025/12/08/[$LATEST]0e761b7bb3298c7d88a37c85e243a7a6 [1/2] Processing message: {"version": "0", "id": "708b8288-3573-475e-81b2-8eba2ea535e2", "detail-type": "Object Created", "source": "aws.s3", "account": "000000000000", "time": "2025-12-08T07:01:30Z", "region": "us-east-1", "resources": ["arn:aws:s3:::my-learning-bucket-12345"], "detail": {"version": "0", "bucket": {"name": "my-learning-bucket-12345"}, "object": {"key": "b1.txt", "size": 20, "etag": "32e803191d6866779d58fa80a6a33404", "sequencer": "0062E99A88DC407460"}, "request-id": "6d2fc328-8dc0-46e7-b395-cb8c734eabfa", "requester": "074255357339", "source-ip-address": "127.0.0.1", "reason": "PutObject"}}
2025-12-08T07:01:34.323000+00:00 2025/12/08/[$LATEST]0e761b7bb3298c7d88a37c85e243a7a6 [2/2] Processing message: {"version": "0", "id": "2b9571f4-7034-468d-ac64-b689f9db15a8", "detail-type": "Object Created", "source": "aws.s3", "account": "000000000000", "time": "2025-12-08T07:01:31Z", "region": "us-east-1", "resources": ["arn:aws:s3:::my-learning-bucket-12345"], "detail": {"version": "0", "bucket": {"name": "my-learning-bucket-12345"}, "object": {"key": "b2.txt", "size": 20, "etag": "71172c661688f3a692617e3cc500bb8f", "sequencer": "0062E99A88DC407460"}, "request-id": "764fc971-edbb-4af6-afd4-a82569b2f8da", "requester": "074255357339", "source-ip-address": "127.0.0.1", "reason": "PutObject"}}
```

# エラー実験
ファイル名に"error"が含まれるファイルをアップロードすると、エラーが出力されるようにする
エラーが出力されて約1分後に再度lambdaが走る

# エラー結果
```
2025-12-08T07:28:10.568000+00:00 2025/12/08/[$LATEST]c35d5ccaf204d313ed62e5ee95cec127 !!! ERROR DETECTED !!! Crashing intentionally...      
    raise Exception("Planned Failure")in handlerTEST]c35d5ccaf204d313ed62e5ee95cec127 [ERROR] Exception: Planned Failure
2025-12-08T07:28:10.568000+00:00 2025/12/08/[$LATEST]c35d5ccaf204d313ed62e5ee95cec127 END RequestId: 3691357f-4be2-4ab1-8f98-22657252e2e0   
2025-12-08T07:28:10.568000+00:00 2025/12/08/[$LATEST]c35d5ccaf204d313ed62e5ee95cec127 REPORT RequestId: 3691357f-4be2-4ab1-8f98-22657252e2e0Duration: 2.03 ms       Billed Duration: 3 ms   Memory Size: 128 MB     Max Memory Used: 128 MB
2025-12-08T07:29:13.393000+00:00 2025/12/08/[$LATEST]c35d5ccaf204d313ed62e5ee95cec127 START RequestId: 81715e34-b635-4572-95b2-8edb9a3ab7ab Version: $LATEST
2025-12-08T07:29:13.393000+00:00 2025/12/08/[$LATEST]c35d5ccaf204d313ed62e5ee95cec127 Lambda started! Batch size: 1
```

# 3回エラーでDLQに行く
```
PS C:\learning_cloudformation> aws sqs get-queue-attributes --queue-url http://localhost:4566/000000000000/my-learning-dlq --attribute-names
 ApproximateNumberOfMessages --endpoint-url=http://localhost:4566 --profile localstack
{
    "Attributes": {
        "ApproximateNumberOfMessages": "1"
    }
}
```
