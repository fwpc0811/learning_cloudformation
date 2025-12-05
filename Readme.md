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
# コンテナの停止
docker-compose down
```


