# 1分思考実験｜半自動動画生成パイプライン

思考実験のFact Packから、縦型ショート動画の台本、ナレーション、実測字幕、図解映像、投稿素材までを生成するPythonパイプラインです。

現在はトロッコ問題 `001` について、macOSならAPIキーなしでもナレーション入りの確認用MP4まで生成できます。

競合比較から作った `fast44` 改善版では、約41秒への短縮、条件変更の前倒し、中立なA/B表示、意味のある動き、ライセンス不要の自動生成BGM/SE、投稿後のPDCA記録まで確認できます。現行版は上書きせず、比較用の別フォルダへ出力します。

## 現在の到達点

```text
Fact Pack (YAML)
  → ブランドルールとプロンプトを合成
  → OpenAI Structured Outputs / オフライン合格サンプル
  → Pydantic構造検証と編集品質チェック
  → シーン単位TTS
  → 音声の実測秒数でタイムラインと字幕を再構築
  → 9:16の図解・字幕フレームを決定論的に描画
  → H.264/AACのMP4、絵コンテ、投稿素材を出力
```

### Phase 1：台本・編集素材

- 構造化台本とHook 3案
- シーン構成と予定タイムライン
- ナレーション原稿
- 予定時刻ベースのSRT字幕
- 投稿文と固定コメント
- 入力・モデル・品質検証結果を記録したmanifest

LLM部分はOpenAI Responses APIのStructured OutputsでPydanticスキーマへ直接変換します。形式が正しくてもブランドルールに違反する出力は後段の品質検証で停止します。

### Phase 2：音声・実測字幕・動画

- OpenAI音声、macOS内蔵音声、無音の3経路
- シーン単位のWAV生成と音量正規化
- 実際の音声長に追従するタイムラインとSRT
- 黒・白・金を基調にした1080×1920図解
- 字幕を焼き込んだMP4
- 9シーンを一覧できる絵コンテ
- AI生成音声の表示と投稿文への開示文追加
- 同一台本・同一音声設定を再利用するシーンキャッシュ

### Phase 3：比較・PDCA

- 現行版と改善版を別フォルダで保持
- 予定尺・実測尺・名称公開・条件変更・回答時間・文字量を自動比較
- 仮説、投稿前チェック、採否基準をMarkdownとJSONへ出力
- 公開2時間後・48時間後の実績を記録するCSVを自動作成
- 改善版のA/Bを停止画面では同じ面積・明るさへ戻し、回答誘導を抑制

OpenAI音声は公式の [Text to speechガイド](https://developers.openai.com/api/docs/guides/text-to-speech) に沿って `gpt-4o-mini-tts`、WAV、`cedar` を既定にしています。

## 必要環境

- Python 3.11以上
- macOS内蔵日本語音声、またはOpenAI APIキー（ナレーション用）
- OpenAI APIキー（実LLM台本生成時）

FFmpegは `imageio-ffmpeg` の配布バイナリを使うため、通常は別途インストール不要です。

## 最短セットアップ

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python pipeline.py validate

# fast44改善版だけを品質検証
python pipeline.py validate --experiment 001 --variant fast44
python pipeline.py 001 --offline
```

macOSでは、次のコマンドでAPI料金を使わずナレーション入り軽量プレビューを生成できます。

```bash
python pipeline.py render 001 --voice-provider system --preview
```

生成先は `output/001_trolley_problem/draft_preview.mp4` です。Linuxなど日本語システム音声がない環境では、まず無音版で映像工程を確認できます。

```bash
python pipeline.py render 001 --voice-provider silent --preview
```

同じ設定の音声はシーン単位で再利用されます。字幕や色だけを調整した再書き出しでは、音声を作り直しません。

## 競合分析反映版 `fast44` を確認する

現行版を残したまま、短尺・動的編集版を生成します。

```bash
python pipeline.py generate 001 --offline --variant fast44 --overwrite
python pipeline.py render 001 --variant fast44 --edit-profile kinetic --voice-provider system --preview --overwrite
python pipeline.py pdca 001 --variant fast44
```

主な出力先は次の通りです。

```text
output/variants/fast44/001_trolley_problem/draft_preview.mp4
output/variants/fast44/001_trolley_problem/storyboard.jpg
output/pdca/001_fast44/review.md
output/pdca/001_fast44/performance_log.csv
```

`kinetic` 編集は、列車・レバー・人物の意味に沿った動きと、低い環境音・レバー音・心拍・衝撃音を決定論的に生成します。外部の楽曲や効果音素材を使わないため、確認版の権利関係を単純に保てます。

## OpenAI APIで台本と音声を生成する

1. 環境変数例をコピーします。

   ```bash
   cp .env.example .env
   ```

2. `.env` の `OPENAI_API_KEY` に自分のAPIキーを設定します。`.env` はGitの対象外です。

3. 構造化台本を生成します。

   ```bash
   python pipeline.py 001 --overwrite
   ```

4. OpenAI音声で確認用動画を生成します。

   ```bash
   python pipeline.py render 001 --voice-provider openai --preview --overwrite
   ```

台本生成の既定モデルは `gpt-5.4-mini` です。変更する場合は `.env` の `OPENAI_MODEL` を更新してください。実装はOpenAI公式の [Responses API](https://developers.openai.com/api/reference/python/resources/responses) と [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) に沿っています。

`--voice-provider auto` は、APIキーがあればOpenAI音声、なければmacOS内蔵音声、どちらも使えなければ無音を選びます。意図しないAPI利用を避けたい確認段階では `system` または `silent` を明示してください。

## 投稿解像度で書き出す

`--preview` を外すと、1080×1920・30fpsの `draft.mp4` を生成します。

```bash
python pipeline.py render 001 --voice-provider openai --overwrite
```

公開前には必ず、人間が台本の事実、音声、字幕、セーフエリア、投稿文を確認してください。TikTok等への自動投稿は初期スコープに含めていません。

## 主なコマンド

```bash
# 登録テーマ一覧
python pipeline.py list

# 設定、Fact Pack、ゴールデンサンプルを一括検証
python pipeline.py validate

# APIへ送るsystem/userプロンプトを確認（API呼び出しなし）
python pipeline.py prompt 001

# APIなしでPhase 1成果物を生成
python pipeline.py generate 001 --offline

# generateは省略可能
python pipeline.py 001 --offline

# APIなしのナレーション入り軽量動画（macOS）
python pipeline.py render 001 --voice-provider system --preview

# 無音の軽量動画
python pipeline.py render 001 --voice-provider silent --preview

# 現行版とfast44のPDCA比較資料・計測表を生成
python pipeline.py pdca 001 --variant fast44

# 任意のLLM生成済みscript.jsonを再検証
python pipeline.py validate --generated output/001_trolley_problem/script.json

# 自動テスト
python -m pytest
```

既存成果物を意図的に更新するときだけ `--overwrite` を指定します。

## 出力

```text
output/001_trolley_problem/
├── script.json             # LLM構造化出力の正本
├── script.md               # 人間がレビューしやすい台本
├── narration.txt           # TTS入力用の連結原稿
├── scenes.json             # 各シーンと予定時刻
├── timeline.json           # 予定尺ベースの時間情報
├── subtitles.srt           # 予定尺ベースの仮字幕
├── caption.txt             # ハッシュタグ込み投稿文
├── pinned_comment.txt      # 固定コメント
├── manifest.json           # Phase 1生成条件と品質結果
├── audio/scenes/           # シーン単位WAVとキャッシュ情報
├── voice.wav               # 間を含む結合済みナレーション
├── audio_manifest.json     # 音声設定とシーン別実測秒数
├── timeline_actual.json    # 音声実測ベースの時間情報
├── subtitles_actual.srt    # 音声実測ベースの字幕
├── visuals/                # シーンカード、字幕フレーム、FFmpeg入力
├── storyboard.jpg          # 全シーン一覧
├── publish_caption.txt     # 音声開示文を含む投稿用文面
├── render_manifest.json    # Phase 2生成条件
├── draft_preview.mp4       # 540×960・15fps確認用動画
└── draft.mp4               # 1080×1920・30fps投稿用動画

output/variants/fast44/      # 現行版を壊さない改善版の成果物
output/pdca/001_fast44/      # 比較レポート、JSON、実績記録CSV
```

## リポジトリ構成

```text
config/                  # ブランド、動画、音声、LLM、プロンプト設定
content/
├── experiments.yaml     # テーマ一覧
├── experiments/         # 事実と論点を持つFact Pack
└── golden/              # APIなしで使う合格基準の構造化台本
templates/               # POV / 二択 / ミステリーの表現テンプレート
assets/                  # フォント、アイコン、BGM、SE
src/thought_pipeline/    # 生成、検証、音声、字幕、映像処理
tests/                   # APIなしの自動テスト
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

- 予定尺が40〜55秒に収まる
- Hookが3案あり、本命と第1シーンが一致する
- 冒頭に「トロッコ問題」「思考実験」「哲学」を出さない
- 視聴者を「あなた」として当事者化する
- A/Bを明示し、回答用の間を1.5秒以上置く
- 選択後に名称を公開する
- 家族という条件を第二の問いに含める
- 第二の問いの後にA/Bと理由を求める
- CTAで最初と最後の回答変化を回収できる
- 名称公開だけのシーンが3秒を超えない
- 第二の問いが全体の72%より前に始まる
- 予定読み上げ密度が毎秒7文字を超えない
- Fact PackのIDとタイトルが一致する
- 音声実測尺が目標範囲かをmanifestへ記録する
- 空音声を検知し、macOS音声は最大3回再試行する

## 新しい思考実験を追加する

1. `content/experiments/` に `002_slug.yaml` を追加します。
2. `content/experiments.yaml` にID、slug、パス、テンプレートを登録します。
3. `python pipeline.py validate` でFact Packを検証します。
4. `python pipeline.py prompt 002` でプロンプトを確認します。
5. `python pipeline.py 002` で台本を生成します。
6. `python pipeline.py render 002 --preview` で動画化します。

次の拡張候補は、POV・ミステリー専用図解、投稿用カバー生成、実績CSVからの自動評価、Google Sheetsからのテーマ投入です。
