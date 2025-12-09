# 設定
$Endpoint = "http://localhost:4566"
$AwsProfile = "localstack"
$InfraStackName = "infra-stack"
$AppStackName = "app-stack"
# Lambdaのコードを一時的に置くS3バケット（infra.yamlで作ったバケットを利用）
$CodeBucket = "my-learning-bucket-12345"

# --------------------------------------------------
# Phase 1: インフラ (CloudFormation) のデプロイ
# --------------------------------------------------
Write-Host "1. インフラ(SQS, S3など)をデプロイしています..." -ForegroundColor Cyan

# インフラStackの作成/更新
aws cloudformation deploy `
    --stack-name $InfraStackName `
    --template-file infra.yaml `
    --endpoint-url $Endpoint `
    --profile $AwsProfile

# --------------------------------------------------
# Phase 2: アプリ (SAM/Lambda) のビルド
# --------------------------------------------------
Write-Host "2. Lambdaをビルドしています (Docker使用)..." -ForegroundColor Cyan

# --use-container を追加: Dockerの中でビルドするのでPCにPythonがなくてもOK
sam build --use-container

# --------------------------------------------------
# Phase 3: アプリ (SAM/Lambda) のパッケージ化とデプロイ
# --------------------------------------------------
Write-Host "3. LambdaコードをS3にアップロードしています..." -ForegroundColor Cyan

# ビルドされたコードをZIPにしてS3に上げ、packaged.yaml を作る
aws cloudformation package `
    --template-file .aws-sam/build/template.yaml `
    --s3-bucket $CodeBucket `
    --output-template-file packaged.yaml `
    --endpoint-url $Endpoint `
    --profile $AwsProfile

Write-Host "4. Lambdaをデプロイしています..." -ForegroundColor Cyan

# packaged.yaml を使ってデプロイ（SAMではなくAWSコマンドを使うので確実）
aws cloudformation deploy `
    --template-file packaged.yaml `
    --stack-name $AppStackName `
    --endpoint-url $Endpoint `
    --profile $AwsProfile `
    --capabilities CAPABILITY_IAM

# --------------------------------------------------
# 確認
# --------------------------------------------------
Write-Host "=== 完了しました ===" -ForegroundColor Green
Write-Host "Lambda作成確認:"
aws lambda list-functions --endpoint-url $Endpoint --profile $AwsProfile