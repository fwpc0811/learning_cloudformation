# settei
$StackName = "my-stack"
$TemplatePath = "file://templates/s3_eventbridge.yaml"
$Endpoint = "http://localhost:4566"
$AwsProfile = "localstack"  # ←ここを変えました ($Profile -> $AwsProfile)

# delete old stack
Write-Host "1. 古いスタックを削除しています... ($StackName)" -ForegroundColor Cyan
aws cloudformation delete-stack --stack-name $StackName --endpoint-url $Endpoint --profile $AwsProfile

# wait
Write-Host "   削除の完了を待機中..." -ForegroundColor Gray
aws cloudformation wait stack-delete-complete --stack-name $StackName --endpoint-url $Endpoint --profile $AwsProfile

# create new stack
Write-Host "2. 新しいスタックを作成しています..." -ForegroundColor Cyan
aws cloudformation create-stack --stack-name $StackName --template-body $TemplatePath --endpoint-url $Endpoint --profile $AwsProfile

# show result
Write-Host "3. 作成されたS3バケットを確認します..." -ForegroundColor Cyan
aws s3 ls --endpoint-url $Endpoint --profile $AwsProfile

Write-Host "=== 完了しました ===" -ForegroundColor Green