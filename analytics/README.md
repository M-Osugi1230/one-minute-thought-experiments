# TikTok analytics data

このディレクトリは「1分思考実験」TikTokアカウントの時系列データ置き場です。

- `latest.json`: TikTok Display APIから取得した最新スナップショット
- `snapshots/`: 6時間ごとの不変JSONスナップショット
- `history/post_snapshots.csv`: 投稿別の時系列
- `history/account_snapshots.csv`: アカウント統計の時系列
- `manual/`: TikTok Studioスクリーンショット等から取得したAPI外の指標
- `private/tiktok_refresh_token.fernet`: 暗号化されたrotating refresh token（平文ではない）
- `private/token_metadata.json`: tokenの非機密メタデータ

詳細なセットアップとセキュリティ方針は `docs/TIKTOK_ANALYTICS_AUTOMATION.md` を参照してください。
