# 1分思考実験｜TikTok写真カルーセル投稿 作成マニュアル

Version: 1.5  
Updated: 2026-08-28  
Validated posts: #001 トロッコ問題 / #002 テセウスの船 / #003 水槽の中の脳 / #004 スワンプマン

---

## 0. このマニュアルの目的

この文書は、「1分思考実験」のTikTok写真カルーセル投稿を、別チャット・別テーマでも同じ思想・工程・品質で再現するための標準作業手順（SOP）兼成果物仕様書である。

現在の第一フォーマットは **9:16の写真カルーセル（スワイプ式）**。顔出し・本人ナレーションに依存せず、視聴者自身を思考実験の主人公にして、背景画像・短い文章・選択・コメントによって参加させる。

最重要原則：

1. 哲学を説明する前に、視聴者に考えさせる。
2. 思考実験名から始めず、「あなた」から始める。
3. 原則として、状況 → 葛藤 → 選択 → 条件変更 → 再考をつくる。
4. 結論で閉じず、コメント欄を第二部にする。
5. Canvaは原則 **背景1枚＋編集可能な文字** だけで構成する。
6. **投稿本文を画像生成で描かない。文字はCanvaのテキスト要素で入れる。**
7. Brand Shellは固定し、Episode Skinはテーマごとに変える。
8. Cinematic + realistic + minimal editorialを親画風とする。
9. トレンドは主役にせず、テーマ選定・Hook・投稿タイミングの追い風として使う。
10. Hookは最低5案を内部比較し、通常は採用案だけを成果物として出す。
11. 重大な分岐がない限り、制作途中の確認回数を増やさず完成まで進める。
12. テンプレート再利用時は、旧作品の文言・改行・色・強調・配置残存を全ページ監査する。

---

# 1. 投稿1本の完成条件（Definition of Done）

以下をすべて満たした時点で「完成」とする。

## 企画・事実
- テーマ選定理由が記録されている
- Fact Packがある
- 基本状況・作者・論点が事実確認済み
- 基本形と後世の変形・追加条件が区別されている
- 短尺化の言い換えで哲学的論点を壊していない

## コピー
- Hookを最低5案内部比較し、採用Hookが確定
- ページ数と役割が確定
- 各ページ1メッセージ
- Final Copyが確定
- 意図した改行位置まで確定
- 思考実験名は原則後半まで明かしていない
- A/Bが中立
- 最終ページに第二の問いまたはコメント誘導

## 画像
- 1ページにつき1枚の背景が確定
- 背景に投稿本文・ブランド名・ページ番号等の文字が焼き込まれていない
- Image Mappingが確定
- ファイル名だけでなくサムネイルでも照合済み
- 各ページのText Zoneが決まっている

## Canva
- 背景は既存背景プレースホルダーのfill差し替え
- 文字はすべて編集可能なCanvaテキスト
- 全ページに「1分思考実験」
- 全ページにページ番号
- Page 1にスワイプ誘導
- 英語kickerあり
- 不自然な自動折り返しなし
- TikTok UI安全域を侵していない
- 重要オブジェクトを文字が隠していない
- 実サムネイルで全ページQC済み

## Brand Shell
- **「1分思考実験」は全ページ #FFFFFF に固定**
- ブランド名の色をEpisode Accentにしない
- ページ番号は高コントラストneutral light
- Episode Accentは本文強調・kicker等に限定
- 複製元の旧アクセント色が意図せず残っていない

## 投稿
- TikTokタイトル確定
- Caption確定
- Hashtags確定
- Pinned Comment確定
- BGM方向性確定
- 投稿設定確認
- Production Pack保存
- Canvaの保存状態がcommit成功で確認済み

---

# 2. 成果物の順序｜Output Contract

原則として次の順序を崩さない。

```text
Theme / Why Now
  ↓
Fact Pack
  ↓
Hook Selection
  ↓
Page Plan
  ↓
Final Copy
  ↓
Line Breaks / Emphasis
  ↓
Brand Shell Check
  ↓
Episode Skin / Art Direction
  ↓
Image Plan
  ↓
Page-by-page Image Generation
  ↓
Image QC
  ↓
Image Mapping / Canonical Naming
  ↓
Text Zone
  ↓
Canva Asset Verification
  ↓
Canva Implementation
  ↓
Brand Token Reset
  ↓
QC
  ↓
TikTok Title
  ↓
Caption / Hashtags / Pinned Comment
  ↓
BGM Direction
  ↓
Production Pack Save
  ↓
User Handoff
```

「今回は画像から先」「今回はCanvaから先」「Hookは後で決める」は原則しない。既存素材再利用やユーザー明示指定のみ例外。

---

# 3. Step 1｜テーマ選定

101個を本の順番どおりに機械的に投稿しない。

評価は **コンテンツ力80 + タイミング20** を基本とする。

### コンテンツ力80
- Hook力
- 自分事化
- 意見分裂性
- 短尺理解性
- 条件変更・再考の作りやすさ
- 映像化しやすさ
- Evergreen性

### タイミング20
- 今考えやすいテーマか
- AI、格差、SNS、仕事、孤独、科学、未来等と自然につながるか
- 一過性ニュースに依存しすぎないか

トレンドは作品の主役にしない。

---

# 4. Step 2｜Fact Pack

標準保存先：

```text
content/experiments/{ID}_{slug}.yaml
```

最低限：

- title
- one_line_summary
- core_question
- viewer_role
- initial_state
- constraints
- choices
- variation_question
- philosophical_focus
- facts
- sources
- must_include
- must_not_include

## 4.1 基本形と変形

- 書籍は理解の起点として使える
- Kindle画面や書籍文章をそのまま投稿素材へ転用しない
- 必要に応じて原典・信頼できる資料で作者・成立時期・基本形を確認
- 後世の追加条件や独自変形は基本形と混同しない

## 4.2 心的状態を勝手に断定しない

思考実験の論点が「意味」「記憶」「意識」「因果的履歴」等そのものにある場合、短尺化のために結論を先取りする表現を使わない。

例：スワンプマンでは、

- OK: 「同じ身体・同じ脳・同じように振る舞う」
- 慎重に扱う: 「同じ記憶を持つ」

原典が問題にしている心的状態を、投稿側で事実として確定させない。

---

# 5. Step 3｜Hook

毎回最低5案を内部生成し、次で比較する。

```text
1秒理解性
→ 自分事化
→ 葛藤・謎
→ スワイプ理由
→ 過剰煽りがないか
```

基本形：

```text
あなた + 事件 / 条件 + 問い
```

避ける：

- 「今日は○○を解説します」
- 思考実験名から始める
- 哲学者名・専門語を入口にする

Page 1の標準スワイプ誘導：

```text
スワイプして考える　›
```

スワイプ誘導自体はBrand Shell固定要件。

---

# 6. Step 4｜ページ構成

標準は8ページ。ただし内容優先で7/8/9ページを判断する。

| Page | 標準役割 |
|---|---|
| 1 | Hook |
| 2 | Scene |
| 3 | Change / Mechanism |
| 4 | Conflict / Personalize |
| 5 | Choice |
| 6 | Condition Change / Reveal |
| 7 | Reveal / Point |
| 8 | Your Answer / Second Question |

原則：

- 1ページ1メッセージ
- 説明を詰め込まない
- 選択前に必要条件を揃える
- A/Bのどちらかを正解のように見せない
- Reveal位置は後半なら固定しない
- 最後に再考・第二の問い・理由コメントを残す

---

# 7. Step 5｜文章・改行

### 文章量
- 主見出し：1〜3行目安、必要なら4行
- 補足：1〜2行基本
- 長文説明を1ページに詰めない

### トーン
- 短い
- 直接的
- 「あなた」を使う
- 過剰に煽らない
- 視聴者の人格を評価しない
- 哲学的立場を正解扱いしない

### 改行
改行は文章仕様の一部。

- 意味のかたまりで切る
- 助詞だけを孤立させない
- 1行を極端に短くしない
- 文字サイズを先に小さくして逃げない
- A/Bは可能な限り1選択肢＝1行

---

# 8. Step 6｜Brand Shell / Episode Skin

## 8.1 Brand Shell｜固定

- 1080×1920 / 9:16
- 全ページ「1分思考実験」
- 全ページページ番号
- 英語kicker
- Page 1スワイプ誘導
- 主見出し・補足・A/Bの情報階層
- TikTok UI安全域
- 背景1枚＋編集可能文字
- 中盤Choice
- 最終CTA

### 固定色トークン

```text
Brand name「1分思考実験」: #FFFFFF
Page number: neutral light / 高コントラスト
Base text: white / off-white
Episode accent: 可変
```

**「1分思考実験」にはEpisode Accentを使わない。**

## 8.2 Episode Skin｜可変

- 背景色
- アクセント色
- 光源色
- 霧・粒子・グリッチ等
- 時代感
- 背景モチーフ
- kickerの具体語

親画風：

```text
Cinematic
Realistic
Minimal Editorial
Restrained Lighting
Controlled Information Density
```

## 8.3 テンプレート複製直後のBrand Token Reset

旧作品の見た目を引きずらないため、複製後すぐに全ページの固定ブランド要素をリセットする。

```text
1. 「1分思考実験」全ページ → #FFFFFF
2. ページ番号 → neutral light
3. Brand Shell位置確認
4. 旧テーマ文言0件確認
5. その後にEpisode Skinを適用
```

---

# 9. Step 7｜背景画像生成

### 共通仕様

- 9:16 vertical
- cinematic + realistic + minimal editorial
- negative space確保
- 重要オブジェクトをText Zoneから外す
- no text / no letters / no numbers / no signage / no logos / no UI / no watermark
- goreを避ける
- generic stock photo感を避ける

## 9.1 画像生成と文字生成を分離

**背景画像生成工程では、投稿本文・タイトル・ブランド名・A/B・CTAを一切生成しない。**

背景が完成した後に「画像編集」に移る場合でも、文字を追加する目的でimage generationを再実行しない。

正解：

```text
背景画像生成
↓
Canvaへアップロード
↓
Canvaの編集可能なテキスト要素で文字入れ
```

禁止：

```text
背景画像生成
↓
画像生成AIで日本語文字を焼き込み
↓
Canvaへ配置
```

理由：

- 日本語文字崩れ
- 誤字・滲み
- 後編集不可
- ブランド色修正が困難
- テンプレート再利用性低下

## 9.2 1ページ＝1画像

各ページは独立した画像として設計する。

一括生成ツールを使う場合でも、**各ページに独立プロンプト・独立出力を持たせること**。生成結果に意味的ドリフトが出た場合は、ページ単位で再生成する。

## 9.3 生成順≠採用順

生成結果がプロンプト意図からずれることがあるため、生成順をそのままPage 1→Nとみなさない。

各画像を視覚確認し、物語上最も適切なページへ割り当てる。

---

# 10. Step 8｜Image Mapping / Canonical Naming

Canva投入前に正本対応表を作る。

推奨命名：

```text
01_HOOK_{short-name}
02_SCENE_{short-name}
03_CHANGE_{short-name}
04_CONFLICT_{short-name}
05_CHOICE_{short-name}
06_REVEAL_{short-name}
07_POINT_{short-name}
08_FINAL_{short-name}
```

最低限、先頭に2桁番号を付ける。

### Canvaアップロード後の確認

編集開始前に必ず：

```text
[ ] 対象フォルダを確認
[ ] 必要枚数とアップロード枚数が一致
[ ] 01〜最終番号が揃っている
[ ] 各番号のサムネイル内容がPage Planと一致
[ ] API反映前なら「見えている」と断定しない
```

ファイル名よりサムネイルを優先する。

---

# 11. Step 9｜Text Zone

背景確定後、ページごとに決める。

```text
Primary text zone: left / center / right
Secondary text zone: left / center / right
Bright areas to avoid: ...
Key objects to protect: ...
```

文字位置固定より可読性優先。

---

# 12. Step 10｜Canva組み込み

## 12.1 検証済みテンプレート再利用を優先

```text
既存Layeredテンプレート複製
↓
Brand Token Reset
↓
背景fill差し替え
↓
本文差し替え
↓
Episode Skin
↓
Text Zone調整
↓
QC
```

## 12.2 レイヤー事故防止

全画面背景画像を後からinsertしない。

正解：

```text
既存背景プレースホルダー
↓
update_fillで差し替え
↓
その上にBrand Shellと本文
```

## 12.3 テキストはCanva要素だけ

- 先に最終全文を確定
- replace_text / find_and_replace_text等で編集
- 色・サイズ・位置はformat / resize / positionで調整
- 背景画像へ文字を焼き込まない

## 12.4 A/B

折り返し時の修正順：

```text
1. テキストボックス幅
2. 位置
3. 行間
4. 最後にフォントサイズ
```

A/Bは同サイズ・同色・同ウェイト・同幅・同整列を基本。

---

# 13. Canvaデザイン仕様

### Canvas
- 1080×1920

### 安全域目安
- Left: 72〜76px以上
- Top: 150〜200px以降を主領域
- Right: TikTok UIを考慮
- Bottom: 320〜380px程度をUI回避域として意識

### 標準位置
- ブランド名：上部左
- ページ番号：上部右
- kicker：ブランド名の下
- 主見出し：上〜中央
- 補足：下側だがUIより上
- Page 1スワイプ誘導：主見出しより下位階層

### 文字サイズ目安
- 主見出し：約72〜90px
- 本文：約48〜54px
- kicker：約22〜34px
- A/B：約52〜60px

---

# 14. Step 11｜最終QC

**「要素が存在する」だけでは不合格。全ページの実サムネイルを見る。**

## 14.1 Brand Shell QC
- [ ] 全ページに「1分思考実験」
- [ ] **全ページの「1分思考実験」が #FFFFFF**
- [ ] ブランド位置が揃っている
- [ ] 全ページページ番号
- [ ] kickerあり
- [ ] Page 1スワイプ誘導

## 14.2 Background/Text Separation QC
- [ ] 背景画像に投稿本文が焼き込まれていない
- [ ] Canva本文が編集可能なテキスト要素
- [ ] 背景内文字とCanva文字の二重化なし
- [ ] 不要な文字・数字・ロゴ・UIなし

## 14.3 読みやすさQC
- [ ] 主見出しが背景に埋もれない
- [ ] 重要オブジェクトを隠さない
- [ ] 不自然な改行なし
- [ ] A/B片側だけ折り返していない
- [ ] 最終Pageが縮小表示でも質問→選択→CTAの順に読める

## 14.4 意味QC
- [ ] 文法成立
- [ ] 旧テーマ語0件
- [ ] 背景と文章の意味一致
- [ ] A/B中立
- [ ] 原典の基本形と変形を混同していない
- [ ] 短尺化で論点を先取りしていない

## 14.5 TikTok QC
- [ ] 右側UIと重要文字が重ならない
- [ ] 下部UIにCTAが隠れない
- [ ] Page 1単体でHook成立
- [ ] Page 1単体でスワイプ投稿と分かる

## 14.6 独立3巡QC

通常QC後、次を別巡で行う。

1. **旧色QC**：旧アクセント色0件
2. **改行QC**：意味単位・孤立行・A/B折り返し
3. **Brand Label QC**：「1分思考実験」の色を全ページ横断確認

---

# 15. Step 12｜保存・バージョン管理

Canva名例：

```text
{テーマ}｜{Episode Skin}｜Layered v1
```

構造変更は新バージョン、軽微修正は同一版で可。

### 保存ルール

- 編集操作後はdraft状態と保存済みを混同しない
- **commit成功前に「保存済み」と報告しない**
- Canvaのcommitは、ユーザーの明示承認を得てから実行する
- 過去の「保存してよい」という包括承認を、新しい編集トランザクションのcommit承認として自動流用しない

### 保存後ハンドオフ

保存成功後、ユーザーへ必ず以下を1回で伝える。

```text
Design title: ...
Canva folder: ...
Pages: N
Saved: committed
Direct edit URL: ...
```

必要に応じてページごとのFinal Copyも提示できる状態にする。

---

# 16. Step 13｜Production Pack

標準保存先：

```text
content/publishing/{ID}_{slug}.md
```

必須：

1. Theme
2. Why Now
3. Theme Score
4. Fact Pack Summary
5. Adopted Hook
6. Page Plan
7. Final Copy
8. Line Breaks / Emphasis
9. Brand Shell Check
10. Episode Skin / Art Direction
11. Image Plan
12. Image Mapping
13. Canonical Asset Names
14. Text Zone
15. Canva Folder / Design Title / URL / Creative Status
16. QC Result
17. TikTok Title
18. Caption
19. Hashtags
20. Pinned Comment
21. BGM Direction
22. Upload Order
23. Cover Page
24. Posting Settings
25. Pre-post Check
26. Post-post Actions
27. KPI Log
28. Comment Classification
29. Derivative Post Candidates

Production Packを別チャットでも使える正本とする。

---

# 17. TikTok投稿素材

## 17.1 Title
毎回必須。思考実験名だけに依存せず、考えたくなる問い・状況を短く表現する。

## 17.2 Caption
再説明しすぎない。検索性＋参加補助。

標準：

```text
Hookの言い換え
最初の問い
条件変更 / 第二の問い
思考実験名
コメント要求
ハッシュタグ
```

## 17.3 Pinned Comment
A/Bだけでなく「なぜ」「条件変更後に変わったか」を取る。

## 17.4 BGM
投稿時のTikTok内トレンドを確認しつつ、世界観を優先。

基本方向：
- ambient
- cinematic
- suspense
- minimal
- 読書を邪魔しない

---

# 18. TikTok投稿時の標準設定

- 写真カルーセル
- Page 1 → 最終Page
- Cover: Page 1
- Audience: Public
- Comments: ON
- Location: 原則なし
- Branded content: 該当しない限りOFF
- AI生成素材の表示が必要な場合はTikTok側ルールに従う

---

# 19. 投稿後PDCA

最低限：1時間 / 24時間 / 72時間。

記録候補：
- views
- likes
- comments
- shares
- saves
- profile views
- follows gained
- average viewing time
- completion系
- search traffic / terms

コメントはA/B、条件変更前後、理由パターンを分類し、次投稿へ戻す。

---

# 20. ChatGPTとユーザーの役割分担

## ChatGPT
- テーマ選定・採点
- Fact Pack
- Hook選定
- Page Plan / Final Copy / 改行
- Brand Shell / Episode Skin
- 画像設計・生成
- Image Mapping / Text Zone
- Canva組み込み
- Brand Token Reset
- QC
- Title / Caption / Hashtags / Pinned Comment / BGM方向性
- Production Pack
- 投稿後分析

## ユーザー
- 必要時の最終感覚判断
- TikTokアプリでの投稿操作
- TikTok内での最終BGM選択
- 投稿後URL・分析値共有（自動取得できない場合）

目標：最終判断＋投稿操作までユーザー作業を圧縮する。

---

# 21. よくある失敗と対処

| 症状 | 原因 | 対処 |
|---|---|---|
| Canvaで文字が見えない | 背景を後からinsert | 背景fillをupdate_fill |
| 背景に投稿本文がある | 画像生成AIで文字入れ | 背景は文字なし、Canvaテキストのみ |
| 日本語が滲む・崩れる | 画像生成文字 | Canvaの編集可能文字へ戻す |
| ブランド名の色がページで違う | テンプレート旧色継承 | 全ページ「1分思考実験」#FFFFFFへリセット |
| 画像順が分からない | 生成順・アップロード順を信用 | 01〜番号＋サムネイル照合 |
| 画像名と内容が違う | 意味的ドリフト | 内容ベースで再マッピング |
| Canvaフォルダにまだ見えない | API反映遅延 | 件数確認前に「アップロード済み」と断定しない |
| 背景がごちゃつく | 全ページ同強度 | Choice / Reveal / Finalを静かに |
| オブジェクト二重 | 背景とCanvaで重複 | 背景＋文字へ戻す |
| 8ページが1枚絵になる | まとめ生成 | 各ページ独立プロンプト |
| 文章が壊れる | 場当たり置換 | 最終全文を先に確定 |
| 不自然な改行 | 自動折り返し | 明示改行＋改行QC |
| A/B片方だけ2行 | 幅不足 | 幅→位置→行間→サイズ |
| 原典説明が不正確 | 基本形と変形混同 | Fact Packで分離 |
| 心的状態を断定しすぎる | 短尺化で論点先取り | 行動・物理状態と心的状態を区別 |
| 保存済みと誤報 | commit未確認 | commit成功後のみ保存済みと報告 |
| 保存先が分かりにくい | ハンドオフ不足 | Design title + folder + URL + saved statusを報告 |

---

# 22. 制作開始時セルフチェック

```text
[ ] Version 1.5を確認
[ ] Theme / Why Now
[ ] Fact Packを先に作成
[ ] Hook最低5案内部比較
[ ] Page Plan確定
[ ] Final Copyと改行確定
[ ] Brand Shell固定要素確認
[ ] 「1分思考実験」#FFFFFF固定
[ ] Episode Skin設計
[ ] 背景画像には文字を生成しない
[ ] 各ページ独立画像
[ ] Image Mapping確定
[ ] 01〜のcanonical name
[ ] Canvaアップロード枚数・サムネイル確認
[ ] 既存Layeredテンプレート再利用
[ ] 背景はupdate_fill
[ ] 文字はCanvaテキストのみ
[ ] 通常QC / 旧色QC / 改行QC / Brand Label QC / 縮小QC
[ ] TikTokタイトル
[ ] Caption / Pinned Comment / BGM方向性
[ ] Production Pack
[ ] commit前にユーザー明示承認
[ ] commit成功後に保存先とURLを報告
```

---

# 23. #001〜#004から得た確定知見

## #001 トロッコ問題
- Page 1のスワイプ誘導が有効
- 背景を後からinsertすると文字が隠れる
- 背景fill差し替えが安全

## #002 テセウスの船
- 複数ページを1枚の画像として作らない
- 簡易代替へ迂回すると品質が下がる
- 検証済みテンプレート再利用優先
- 自動折り返しは意味を壊す
- 基本形と後世の追加条件を区別する

## #003 水槽の中の脳
- Brand ShellとEpisode Skin分離は有効
- テンプレート色移行は独立工程が必要
- A/Bはテキスト幅を先に見る
- 文字位置固定よりText Zone可読性優先
- スマホ縮小QCが必要
- commit前の編集セッション失効に備える

## #004 スワンプマン
- **背景生成と文字入れを明確に分離する。背景に文字を生成しない**
- 画像生成後の文字入れはCanva編集機能のみを使う
- 生成順と最終Page順がズレる場合があるため、内容ベースでImage Mappingする
- Canvaアップロード後は01〜番号とサムネイルで対応確認する
- テンプレート再利用時、「1分思考実験」の色を最初に全ページ #FFFFFFへ固定する
- Episode Accentをブランド名へ流用しない
- スワンプマンのように因果的履歴が論点の場合、「同じ記憶」等を安易に断定せず、物理状態・行動と心的状態を区別する
- 編集完了と保存完了を区別し、commit成功後にのみ保存済みと報告する
- 保存後はユーザーが迷わないよう、デザイン名・フォルダ・URL・保存状態をまとめて伝える

### 共通結論

- 説明より参加
- 背景は文字なし
- 文字はCanvaで編集可能にする
- Brand Shellは固定、Episode Skinは可変
- 画像順は内容で確定
- ブランド名は全ページ同一色
- 保存状態は厳密に扱う
- 回答データを次投稿へ戻す

---

## 付記：動画パイプラインとの関係

縦型動画パイプラインは将来展開・比較検証用として保持する。
現時点のTikTok初期運用では、本マニュアルの写真カルーセル制作フローを優先する。
