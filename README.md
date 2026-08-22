# 1分思考実験｜半自動動画生成パイプライン

思考実験のFact Packから、縦型ショート動画の台本と編集前素材を生成するPythonパイプラインです。

Phase 1では、テーマID `001` を指定すると次を自動生成します。

- 構造化台本とHook 3案
- シーン構成と予定タイムライン
- ナレーション原稿
- 仮タイミングのSRT字幕
- 投稿文と固定コメント
- 入力・モデル・品質検証結果を記録したmanifest

LLMを使う部分はOpenAI Responses APIのStructured OutputsでPydanticスキーマに直接変換します。形式が正しくてもブランドルールに違反する出力は、後段の品質検証で停止します。

## 現在の到達点

Phase 1は、APIキーなしで全工程を確認できるオフライン経路を含みます。

```text
Fact Pack (YAML)
  → ブランドルールとプロンプトを合成
  → LLM Structured Outputs / ゴールデンサンプル
  → Pydantic構造検証
  → 尺・Hook・A/B・名称公開順・第二の問い・CTAを品質検証
  → 台本・シーン・字幕・投稿素材を出力
```

音声、実測タイミング、映像レンダリングはPhase 2です。Phase 1の `timeline.json` と `subtitles.srt` は予定尺ベースで、後からシーン単位のTTS実測時間へ置き換えられる構造になっています。

## 必要環境

- Python 3.11以上
- OpenAI APIキー（実LLM生成時のみ）
- FFmpeg（Phase 2以降。Phase 1では不要）

## 最短セットアップ

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python pipeline.py validate
python pipeline.py 001 --offline
```

成功すると `output/001_trolley_problem/` に9ファイルが作られます。

## OpenAI APIで台本を生成する

1. 環境変数例をコピーします。

   ```bash
   cp .env.example .env
   ```

2. `.env` の `OPENAI_API_KEY` に自分のAPIキーを設定します。`.env` はGitの対象外です。

3. 実行します。

   ```bash
   python pipeline.py 001
   ```

既定モデルは `gpt-5.4-mini` です。変更する場合は `.env` の `OPENAI_MODEL` を更新してください。実装は、OpenAI公式ドキュメントの [Responses API](https://developers.openai.com/api/reference/python/resources/responses) と [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) に沿っています。

既存成果物を意図的に更新する場合だけ、次を使います。

```bash
python pipeline.py 001 --offline --overwrite
```

## コマンド

```bash
# 登録テーマ一覧
python pipeline.py list

# 設定、Fact Pack、ゴールデンサンプルを一括検証
python pipeline.py validate

# APIへ送るsystem/userプロンプトを確認（API呼び出しなし）
python pipeline.py prompt 001

# APIなしで成果物を生成
python pipeline.py generate 001 --offline

# generateは省略可能
python pipeline.py 001 --offline

# 任意のLLM生成済みscript.jsonを再検証
python pipeline.py validate --generated output/001_trolley_problem/script.json

# 自動テスト
python -m pytest
```

## 出力

```text
output/001_trolley_problem/
├── script.json          # LLM構造化出力の正本
├── script.md            # 人間がレビューしやすい台本
├── narration.txt        # TTS入力用の連結原稿
├── scenes.json          # 各シーンと予定時刻
├── timeline.json        # Phase 2が差し替える時間情報
├── subtitles.srt        # 予定時刻ベースの仮字幕
├── caption.txt          # ハッシュタグ込み投稿文
├── pinned_comment.txt   # 固定コメント
└── manifest.json        # 生成条件、入力ハッシュ、品質結果
```

同じ出力先が存在する場合、誤上書きを避けるため処理は停止します。更新時は `--overwrite` が必要です。

## リポジトリ構成

```text
config/                  # ブランド、動画、音声、LLM、プロンプト設定
content/
├── experiments.yaml     # テーマ一覧
├── experiments/         # 事実と論点を持つFact Pack
└── golden/              # APIなしで使う合格基準の構造化台本
templates/               # POV / 二択 / ミステリーの表現テンプレート
assets/                  # フォント、アイコン、BGM、SE（実素材はGit対象外）
src/thought_pipeline/    # 生成、検証、タイムライン、出力処理
tests/                   # オフライン自動テスト
pipeline.py              # 実行入口
```

## トロッコ問題のデータ方針

`content/experiments/001_trolley_problem.yaml` は動画文面そのものではなく、次を保存します。

- 基本状況とA/Bの結果
- 第三の選択肢を入れない等の制約
- 中核の哲学的論点
- 家族を条件にした第二の問い
- 原典情報と過剰断定を避けるルール

これにより、事実は人間が管理し、Hook・ナレーション・画面表現だけをLLMに任せられます。

## 自動品質チェック

生成直後に少なくとも次を検査します。

- 予定尺が40〜55秒に収まる
- Hookが3案あり、本命と第1シーンが一致する
- 冒頭に「トロッコ問題」「思考実験」「哲学」を出さない
- 視聴者を「あなた」として当事者化する
- A/Bを明示し、回答用の間を1.5秒以上置く
- 選択後に名称を公開する
- 家族という条件を第二の問いに含める
- 第二の問いの後にA/Bと理由を求める
- Fact PackのIDとタイトルが一致する

失敗時は動画素材を出力せず、違反コードと場所を表示します。

## 新しい思考実験を追加する

1. `content/experiments/` に `002_slug.yaml` を追加します。
2. `content/experiments.yaml` にID、slug、パス、テンプレートを登録します。
3. `python pipeline.py validate` でFact Packを検証します。
4. `python pipeline.py prompt 002` でプロンプトを確認します。
5. `python pipeline.py 002` で生成します。

公開前には、Fact Packの一次資料、独自表現、字幕の読みやすさ、音声の間、最終的な映像を人間が確認してください。

## Phase 2への接続点

次段階では、既存スキーマを壊さず次を追加できます。

1. `voice.yaml` を使ったシーン単位TTS
2. 音声ファイルの実測秒数で `timeline.json` を再構築
3. 実測時刻からSRTを再生成
4. `visual_template` に対応するSVG・背景・テキスト描画
5. FFmpegで1080×1920の `draft.mp4` を生成
6. BGM/SEの仮配置と音量正規化

TikTok等への自動投稿は、公開直前の人間確認を残すため初期スコープに含めません。
