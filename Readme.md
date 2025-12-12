# 1. ビルド
# SAMが .aws-sam/build 配下にアーティファクトを生成します
samlocal build

# 2. デプロイ
# ここでZip化 → LocalStack S3へアップロード → Lambda作成が行われます
# LocalStackのログを見ると、この後のMountingプロセスでエラーが出ているか、無視されています
samlocal deploy \
  --stack-name layer-failure-stack \
  --resolve-s3 \
  --capabilities CAPABILITY_IAM \
  --region us-east-1

# 動作確認
awslocal lambda invoke \
  --function-name layer-test-function \
  response.json

# 以下のエラーが発生する。
ModuleNotFoundError: No module named 'my_shared_lib'

# 結果の確認
cat response.json

# 原因
LocalStackが「S3にアップロードされたLayerのZipファイル」を、Lambdaコンテナ起動時に /opt ディレクトリへ展開・マウントする処理に失敗しているため。
コンテナの中に入って確認すると /opt が空っぽ。

# 対策
dockerのvolumeでローカルのフォルダと/optを繋げたがうまくいかなかった。
そもそもlocalstack特有の現象のようなのでAWSの学習にならないと判断し中断。