# TikTok Analytics Automation

最終更新: 2026-08-31

## 目的

「1分思考実験」のTikTokアカウントについて、公開投稿の現在値を定期取得し、GitHub上に履歴を蓄積する。

これにより、ChatGPT側からGitHubコネクタ経由で次の分析を継続的に行えるようにする。

- 投稿別の再生数・いいね・コメント・シェア
- 前回スナップショットからの増分
- 投稿後の伸び方
- いいね率・コメント率・シェア率・総合エンゲージメント率
- フォロワー数などのアカウント統計（scopeが承認されている場合）
- 直近10本中央値と1.5倍基準による勝ち投稿判定

TikTok Studioだけで見られる詳細指標は公式Display APIでは取得できないため、API自動取得とスクリーンショット由来の手動データを分離して保存する。

## 現在の構成

```text
TikTok Developer API
        ↓
GitHub Actions（6時間ごと）
        ↓
scripts/tiktok_analytics.py
        ↓
analytics/latest.json
analytics/snapshots/YYYY/MM/DD/*.json
analytics/history/post_snapshots.csv
analytics/history/account_snapshots.csv
        ↓
ChatGPT / GitHub connector
```

refresh tokenは毎回TikTokから更新される可能性があるため、リポジトリには平文で保存しない。

```text
refresh token
  ↓ Fernet authenticated encryption
analytics/private/tiktok_refresh_token.fernet
```

復号鍵はGitHub Actions Secret `TIKTOK_TOKEN_ENCRYPTION_KEY` にだけ置く。

> このリポジトリは公開リポジトリなので、暗号化鍵をリポジトリへ絶対にコミットしないこと。

---

## 1. TikTok Developer側の準備

TikTok for Developersでアプリを作成する。

初期検証ではSandboxの利用を推奨する。

### 必要なProduct

- Login Kit
- TikTok API / Display API

### Platform

Desktopを使用する。

### Redirect URI

```text
http://127.0.0.1:8765/callback/
```

TikTok Desktop Login Kitではlocalhost / 127.0.0.1とポート付きURIを登録でき、HTTPも許可されている。

### 最低限必要なscope

```text
user.info.basic
video.list
```

### 推奨scope

```text
user.info.stats
user.info.profile
```

`user.info.stats` が承認されると、フォロワー数・フォロー数・累計いいね・投稿数も自動取得できる。

---

## 2. ローカル環境を準備

```bash
cd one-minute-thought-experiments
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

`.env`へTikTok Developer Portalの値を設定する。

```dotenv
TIKTOK_CLIENT_KEY=xxxxxxxx
TIKTOK_CLIENT_SECRET=xxxxxxxx
TIKTOK_SCOPES=user.info.basic,video.list,user.info.stats,user.info.profile
TIKTOK_REDIRECT_URI=http://127.0.0.1:8765/callback/
TIKTOK_ACCOUNT_KEY=1minshiko
```

---

## 3. 暗号化鍵を生成

```bash
python scripts/tiktok_analytics.py keygen
```

出力された1行を `.env` の次の項目へ入れる。

```dotenv
TIKTOK_TOKEN_ENCRYPTION_KEY=生成された値
```

この値は後でGitHub Actions Secretにも同じものを登録する。

---

## 4. TikTokアカウントを初回認証

```bash
python scripts/tiktok_analytics.py authorize
```

実行するとTikTok認証ページがブラウザで開く。

認証完了後、ローカルのcallback serverがauthorization codeを受け取り、TikTok token endpointへ交換する。

成功すると次のファイルが生成される。

```text
analytics/private/tiktok_refresh_token.fernet
analytics/private/token_metadata.json
```

refresh tokenの平文は保存しない。

---

## 5. API取得を手動確認

```bash
python scripts/tiktok_analytics.py collect
```

成功後に確認する。

```bash
python scripts/tiktok_analytics.py inspect
```

生成物:

```text
analytics/latest.json
analytics/snapshots/YYYY/MM/DD/YYYYMMDDTHHMMSSZ.json
analytics/history/post_snapshots.csv
analytics/history/account_snapshots.csv
```

### 最重要確認

現在の「1分思考実験」は写真カルーセル投稿で運用している。

TikTokのDisplay APIドキュメントは `/v2/video/list/` を「public video posts」と表記しているため、初回のAPI実測で写真投稿が返るかを必ず確認する。

返ればそのまま自動運用へ移行する。

返らない場合でも、この自動化は失敗ではなく、TikTok Studioのスクリーンショット/エクスポート値を取り込む半自動方式へ切り替える。

---

## 6. GitHub Actions Secrets

GitHubリポジトリ:

```text
M-Osugi1230/one-minute-thought-experiments
```

Settings → Secrets and variables → Actions → New repository secret で以下を登録する。

### 必須

```text
TIKTOK_CLIENT_KEY
TIKTOK_CLIENT_SECRET
TIKTOK_TOKEN_ENCRYPTION_KEY
```

### 任意のbootstrap用

```text
TIKTOK_REFRESH_TOKEN
```

通常はローカルauthorizeで暗号化tokenファイルを生成してコミットするため不要。

もし暗号化tokenファイルがない状態でGitHub Actionsを先に動かしたい場合だけ、一時的にrefresh tokenをsecretへ設定できる。

---

## 7. 初回tokenファイルをGitHubへ反映

```bash
git add analytics/private/tiktok_refresh_token.fernet analytics/private/token_metadata.json
git add analytics/latest.json analytics/snapshots analytics/history
git commit -m "chore: initialize TikTok analytics"
git push
```

暗号化tokenはGitHub Actions実行時にrefreshされた場合、Actions botが再暗号化した新tokenを自動コミットする。

---

## 8. 定期実行

`.github/workflows/tiktok-analytics.yml` が以下の時刻に自動実行する。

```text
UTC 03:20 / 09:20 / 15:20 / 21:20
JST 12:20 / 18:20 / 00:20 / 06:20
```

つまり6時間ごと。

初期TikTokアカウントでは投稿後24時間の伸び方が重要なため、1日1回ではなく6時間ごととしている。

手動実行も可能。

GitHub → Actions → TikTok Analytics Snapshot → Run workflow

---

## 9. 自動取得できる指標

TikTok Display API v2のVideo Objectから取得する。

- id
- create_time
- title
- video_description
- share_url
- duration
- is_aigc
- view_count
- like_count
- comment_count
- share_count

自動計算:

- like_rate
- comment_rate
- share_rate
- engagement_rate
- age_hours
- views_per_age_hour
- 前回取得からの再生増加
- 前回取得からのいいね増加
- 前回取得からのコメント増加
- 前回取得からのシェア増加

`user.info.stats` scopeがある場合:

- follower_count
- following_count
- likes_count
- video_count
- それぞれの前回差分

---

## 10. 自動取得できないTikTok Studio指標

少なくとも通常のDisplay APIでは以下を取得できない。

- 閲覧された写真数 2.8 / 8 等
- 総再生時間
- 継続率
- 新しいフォロワー（投稿起点）
- 保存数
- おすすめ / 検索 / プロフィール等のトラフィックソース比率
- 検索クエリ
- 視聴者属性

これらは `analytics/manual/` に別系統で保存する。

現在の初回データは:

```text
analytics/manual/2026-08-31-baseline.json
```

に保存済み。

将来的にはTikTok Studio画面のスクリーンショットを定型フォルダへ置き、OCR/画像解析でJSON化する補助フローを追加する。

---

## 11. ChatGPTからの確認方法

今後このプロジェクトで、例えば次のように依頼できる。

```text
現在のTikTokのコンディションを確認して
```

ChatGPT側ではGitHubの:

```text
analytics/latest.json
analytics/history/post_snapshots.csv
analytics/manual/*.json
```

を読み、最新状態と過去差分を比較する。

必要であれば次のレポートを自動生成できる。

- 直近24時間の伸び率ランキング
- 投稿後6h / 12h / 24h / 72hの再生推移
- いいね率ランキング
- コメント率ランキング
- 勝ち投稿（直近10本中央値×1.5以上）
- テーマ別勝率
- Hook文面と初速の関係
- 新規投稿で再利用すべき勝ち要素

---

## セキュリティ原則

次をGitHubへ平文でコミットしない。

```text
TIKTOK_CLIENT_SECRET
TIKTOK_TOKEN_ENCRYPTION_KEY
access_token
refresh_token
```

`TIKTOK_CLIENT_KEY` はsecret扱いでなくてもよいが、運用統一のためGitHub Actions Secretへ置く。

GitHub Actionsのログにもaccess token / refresh tokenを出力しない。

---

## 現在の実装状態

- [x] TikTok OAuth token交換
- [x] Desktop Login Kit PKCE認証補助
- [x] refresh tokenの暗号化保存
- [x] access token自動refresh
- [x] user/info取得
- [x] video/listページネーション
- [x] 投稿別指標計算
- [x] 前回差分計算
- [x] JSON snapshot保存
- [x] CSV history保存
- [x] GitHub Actions 6時間定期実行
- [x] 2026-08-31の手動baseline保存
- [ ] TikTok Developer App作成・scope承認
- [ ] 実アカウントOAuth
- [ ] 写真カルーセルがDisplay APIから返るか実測
- [ ] GitHub Actions Secrets設定
- [ ] 初回定期取得成功
