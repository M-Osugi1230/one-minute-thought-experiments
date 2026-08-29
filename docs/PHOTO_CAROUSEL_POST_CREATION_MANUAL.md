# 1分思考実験｜TikTok写真カルーセル投稿 作成マニュアル

Version: 1.6  
Updated: 2026-08-29  
Validated base: #001 トロッコ問題 / #002 テセウスの船 / #003 水槽の中の脳 / #004 スワンプマン  
Newly validated in v1.6: #007 中国語の部屋

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
12. テンプレート再利用時は、旧作品の文言・画像・色・強調・配置残存を全ページ監査する。
13. **複製した旧作品は完成フォルダへ先に移動しない。編集・commit・再読込確認の後に移動する。**
14. **「編集できた」「プレビューで見えた」「保存された」「正しいフォルダにある」を別状態として扱う。**
15. 完成報告は、commit後のread-backとフォルダ監査まで通過してから行う。

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
- 旧作品の本文・画像・タイトルが0件

## Brand Shell
- **「1分思考実験」は全ページ #F2F3F5 に固定**
- ページ番号も原則 #F2F3F5
- 基本文字色は #F2F3F5
- 標準アクセント色は #FFB000
- 作品固有のアクセントを使う場合も、ブランド名とページ番号は変更しない
- 1ページ内の文字色を増やしすぎない
- 複製元の旧アクセント色が意図せず残っていない

## 保存・格納
- Canvaの編集内容がcommit成功
- commit後にデザインを再読込し、Final Copyと背景が保持されている
- デザインタイトルが当該作品名になっている
- 完成デザインが正しい作品フォルダにある
- 完成フォルダに前作品のデザイン・画像が混在していない
- 標準構成では「背景8枚＋完成デザイン1件」が揃っている

## 投稿
- TikTokタイトル確定
- Caption確定
- Hashtags確定
- Pinned Comment確定
- BGM方向性確定
- 投稿設定確認
- Production Pack保存

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
Canva Final Folder Check / Clean-up
  ↓
Canva Working Copy Creation
  ↓
Canva Asset Verification
  ↓
Canva Implementation
  ↓
Brand Token Reset
  ↓
QC
  ↓
User Preview / Approval
  ↓
Commit
  ↓
Post-commit Read-back
  ↓
Move Final Design to Episode Folder
  ↓
Folder Audit
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

## 4.3 議論中の論点を「証明済み」にしない

思考実験は結論ではなく、論点を切り出す装置である。

例：中国語の部屋では、

- OK: 「正しい答えを返せることと、意味を理解していることは同じか？」
- NG: 「中国語の部屋によってAIが理解できないことは証明された」

システム全体が理解しているのではないか、という反論などが存在する場合は、短尺でも結論を断定しない。

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

## 6.1 条件変更前後の回答差を取る

可能なテーマでは、中盤と最終ページで同型の問いを別条件に置き換える。

例：中国語の部屋

```text
Page 5: 「部屋全体」は理解している？
Page 8: AIは意味を理解している？
```

これにより、視聴者が条件変更で答えを変えるかをコメントから観察できる。

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
Brand name「1分思考実験」: #F2F3F5
Page number: #F2F3F5
Base text: #F2F3F5
Default accent: #FFB000
```

原則としてテキスト色は **Base + Accent の2色** に抑える。Episode Skin上の強い理由がある場合だけ例外を検討する。

**「1分思考実験」とページ番号にはEpisode Accentを使わない。**

## 8.2 Episode Skin｜可変

- 背景色
- アクセントの使い所
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
1. 「1分思考実験」全ページ → #F2F3F5
2. ページ番号全ページ → #F2F3F5
3. Base text → #F2F3F5
4. Accent → 原則 #FFB000
5. Brand Shell位置確認
6. 旧テーマ文言0件確認
7. 旧テーマ背景0件確認
8. その後にEpisode Skinを適用
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

## 9.2 1ページ＝1画像

各ページは独立した画像として設計する。

一括生成ツールを使う場合でも、各ページに独立プロンプト・独立出力を持たせる。意味的ドリフトが出た場合はページ単位で再生成する。

## 9.3 生成順≠採用順

生成結果がプロンプト意図からずれることがあるため、生成順をそのままPage 1→Nとみなさない。各画像を視覚確認し、物語上最も適切なページへ割り当てる。

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

# 12. Step 10｜Canva保存構造・ステージング

## 12.1 標準フォルダ

```text
1分思考実験/
  └─ {作品名}/
      ├─ 01_...png
      ├─ 02_...png
      ├─ ...
      ├─ 08_...png
      └─ {ID}作目｜{作品名}｜1分思考実験  ← 完成デザイン
```

Production PackはGitHub側を正本とし、Canvaフォルダへ無理に混在させない。

## 12.2 完成フォルダをステージング場所にしない

**テンプレート複製直後のデザインを、旧作品の内容が残ったまま新作品フォルダへ移動しない。**

作業順：

```text
既存Layeredテンプレートを複製
↓
作業中デザインとして保持（root / 元フォルダ / staging）
↓
タイトル・背景・本文・色を新作品へ完全置換
↓
全ページQC
↓
ユーザープレビュー
↓
commit
↓
再読込して保存内容を確認
↓
新作品フォルダへ移動
↓
フォルダ監査
```

## 12.3 作業中デザインの命名

推奨：

```text
WORKING_{ID}_{作品名}
```

commit後に：

```text
{ID}作目｜{作品名}｜1分思考実験
```

これにより、旧作品タイトルのまま完成フォルダへ混入する事故を防ぐ。

## 12.4 フォルダを汚した場合

誤った前作品デザイン・素材が入っていたら、新作作業を続ける前に先に退避する。

```text
1. 対象フォルダの全アイテムを列挙
2. 当該作品以外を特定
3. 元作品フォルダまたはrootへ移動
4. 対象フォルダを再列挙
5. クリーンになったことを確認
6. 新作制作を再開
```

---

# 13. Step 11｜Canva組み込み

## 13.1 検証済みテンプレート再利用を優先

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

## 13.2 レイヤー事故防止

全画面背景画像を後からinsertしない。

正解：

```text
既存背景プレースホルダー
↓
update_fillで差し替え
↓
その上にBrand Shellと本文
```

## 13.3 テキストはCanva要素だけ

- 先に最終全文を確定
- 文字は編集可能なCanvaテキスト要素
- 背景画像へ文字を焼き込まない

## 13.4 A/B

折り返し時の修正順：

```text
1. テキストボックス幅
2. 位置
3. 行間
4. 最後にフォントサイズ
```

A/Bは同サイズ・同色・同ウェイト・同幅・同整列を基本。

## 13.5 旧作品完全置換チェック

テンプレート複製後、最低限以下を確認する。

```text
[ ] デザインタイトルに旧作品名がない
[ ] 旧作品の本文語が0件
[ ] 旧作品の背景画像が0枚
[ ] 旧作品のA/B文言が0件
[ ] 旧Episode Accentの残存が意図的なものだけ
```

---

# 14. Canvaデザイン仕様

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

# 15. Step 12｜最終QC

**「要素が存在する」だけでは不合格。全ページの実サムネイルを見る。**

## 15.1 Brand Shell QC
- [ ] 全ページに「1分思考実験」
- [ ] 全ページの「1分思考実験」が #F2F3F5
- [ ] 全ページのページ番号が #F2F3F5
- [ ] ブランド位置が揃っている
- [ ] kickerあり
- [ ] Page 1スワイプ誘導

## 15.2 Background/Text Separation QC
- [ ] 背景画像に投稿本文が焼き込まれていない
- [ ] Canva本文が編集可能なテキスト要素
- [ ] 背景内文字とCanva文字の二重化なし
- [ ] 不要な文字・数字・ロゴ・UIなし

## 15.3 読みやすさQC
- [ ] 主見出しが背景に埋もれない
- [ ] 重要オブジェクトを隠さない
- [ ] 不自然な改行なし
- [ ] A/B片側だけ折り返していない
- [ ] 最終Pageが縮小表示でも質問→選択→CTAの順に読める

## 15.4 意味QC
- [ ] 文法成立
- [ ] 旧テーマ語0件
- [ ] 背景と文章の意味一致
- [ ] A/B中立
- [ ] 原典の基本形と変形を混同していない
- [ ] 議論中の論点を確定結論として書いていない

## 15.5 TikTok QC
- [ ] 右側UIと重要文字が重ならない
- [ ] 下部UIにCTAが隠れない
- [ ] Page 1単体でHook成立
- [ ] Page 1単体でスワイプ投稿と分かる

## 15.6 独立5巡QC

通常QC後、次を別巡で行う。

1. **旧テーマQC**：旧作品の文言・画像・タイトル0件
2. **旧色QC**：不要な旧アクセント色0件
3. **改行QC**：意味単位・孤立行・A/B折り返し
4. **Brand Label QC**：「1分思考実験」#F2F3F5を全ページ横断確認
5. **縮小QC**：スマホ相当の小さな表示で読めるか

---

# 16. Step 13｜保存・バージョン管理

## 16.1 保存状態をState Machineとして扱う

Canva作業では次を別状態として扱う。

```text
WORKING COPY
  ↓
DRAFT EDITED
  ↓
PREVIEWED
  ↓
USER APPROVED
  ↓
COMMITTED
  ↓
READ-BACK VERIFIED
  ↓
MOVED TO FINAL FOLDER
  ↓
FOLDER AUDITED
  ↓
COMPLETE
```

**COMMITTEDより前に「保存済み」と言わない。**  
**FOLDER AUDITEDより前に「完成フォルダ整理完了」と言わない。**

## 16.2 commitルール

- 編集操作と保存は別工程
- ユーザーの「保存」「これで良い」等、現在プレビューへの明示承認後にcommitする
- 承認を得たら、セッション失効を避けるため不要な別作業を挟まずcommitを優先する
- commitが失敗・失効した場合は「保存済み」と報告しない
- 失効時は、新規編集セッションを開く → 現在の保存済み状態を読む → 必要編集を再適用 → プレビュー → commitする

## 16.3 commit後read-back

commit成功だけで終わらせない。必ず再度デザインを読み、以下を確認する。

```text
[ ] タイトルが新作品名
[ ] Page 1が新作品Hook
[ ] Page 6〜7付近のRevealが新作品名
[ ] 最終Pageが新作品の第二の問い
[ ] 背景assetが新作品用
```

旧テーマの代表語が見つかった場合は完成扱いしない。

## 16.4 final folder監査

完成デザインを移動した後、対象フォルダをlistし直す。

標準構成：

```text
8 background images
+ 1 final design
= 9 items
```

背景のみデザイン等を意図的に保存する場合は、その理由と期待件数をProduction Packへ明記する。

監査：

```text
[ ] 01〜08がある
[ ] 完成デザインが1件ある
[ ] 完成デザインのタイトルが新作品名
[ ] 前作品デザイン0件
[ ] 前作品画像0件
```

## 16.5 保存後ハンドオフ

保存・移動・監査成功後、ユーザーへ以下を1回で伝える。

```text
Design title: ...
Canva folder: ...
Pages: N
Saved: committed
Folder audit: passed
Direct edit URL: ...
```

---

# 17. Step 14｜Production Pack

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
30. Canva Commit Status
31. Post-commit Read-back Result
32. Final Folder Expected / Actual Item Count

Production Packを別チャットでも使える正本とする。

---

# 18. TikTok投稿素材

## 18.1 Title
毎回必須。思考実験名だけに依存せず、考えたくなる問い・状況を短く表現する。

## 18.2 Caption
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

## 18.3 Pinned Comment
A/Bだけでなく「なぜ」「条件変更後に変わったか」を取る。

## 18.4 BGM
投稿時のTikTok内トレンドを確認しつつ、世界観を優先。

基本方向：
- ambient
- cinematic
- suspense
- minimal
- 読書を邪魔しない

---

# 19. TikTok投稿時の標準設定

- 写真カルーセル
- Page 1 → 最終Page
- Cover: Page 1
- Audience: Public
- Comments: ON
- Location: 原則なし
- Branded content: 該当しない限りOFF
- AI生成素材の表示が必要な場合はTikTok側ルールに従う

---

# 20. 投稿後PDCA

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

# 21. ChatGPTとユーザーの役割分担

## ChatGPT
- テーマ選定・採点
- Fact Pack
- Hook選定
- Page Plan / Final Copy / 改行
- Brand Shell / Episode Skin
- 画像設計・生成
- Image Mapping / Text Zone
- Canvaフォルダ監査・素材整理
- Canva組み込み
- Brand Token Reset
- QC
- commit後read-back
- final folder監査
- Title / Caption / Hashtags / Pinned Comment / BGM方向性
- Production Pack
- 投稿後分析

## ユーザー
- 必要時の最終感覚判断
- Canvaの重要な方向変更に対する承認
- TikTokアプリでの投稿操作
- TikTok内での最終BGM選択
- 投稿後URL・分析値共有（自動取得できない場合）

目標：最終判断＋投稿操作までユーザー作業を圧縮する。

---

# 22. よくある失敗と対処

| 症状 | 原因 | 対処 |
|---|---|---|
| Canvaで文字が見えない | 背景を後からinsert | 背景fillをupdate_fill |
| 背景に投稿本文がある | 画像生成AIで文字入れ | 背景は文字なし、Canvaテキストのみ |
| 日本語が滲む・崩れる | 画像生成文字 | Canvaの編集可能文字へ戻す |
| ブランド名の色がページで違う | テンプレート旧色継承 | 全ページ「1分思考実験」#F2F3F5へリセット |
| 文字色が増えすぎる | ページ単位で色を足す | 原則 #F2F3F5 + #FFB000 の2色 |
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
| 哲学的結論を断定 | 論点と結論を混同 | 問いとして提示し反論余地を残す |
| 新作フォルダに旧作デザインがある | 複製直後にfinal folderへ移動 | working copyはcommit後までstagingに置く |
| デザイン本文は新作だがタイトルが旧作 | update_title不足 | commit前QC + read-backでタイトル確認 |
| 保存済みと誤報 | draft / previewを保存と誤認 | commit成功後のみ保存済みと報告 |
| commit後に旧内容へ戻っている | transaction失効・draft消失 | reopen → 再適用 → commit → read-back |
| 正しいフォルダか分からない | 移動後の再確認不足 | final folderをlistし、期待件数と内容を監査 |
| 保存先が分かりにくい | ハンドオフ不足 | title + folder + URL + commit + audit statusを報告 |

---

# 23. 制作開始時セルフチェック

```text
[ ] Version 1.6を確認
[ ] Theme / Why Now
[ ] Fact Packを先に作成
[ ] Hook最低5案内部比較
[ ] Page Plan確定
[ ] Final Copyと改行確定
[ ] Brand Shell固定要素確認
[ ] 「1分思考実験」#F2F3F5固定
[ ] ページ番号 #F2F3F5固定
[ ] 基本文字 #F2F3F5 / 標準Accent #FFB000
[ ] Episode Skin設計
[ ] 背景画像には文字を生成しない
[ ] 各ページ独立画像
[ ] Image Mapping確定
[ ] 01〜のcanonical name
[ ] final folder内の旧作品アイテム0件
[ ] Canvaアップロード枚数・サムネイル確認
[ ] working copyをfinal folderへ先に移動しない
[ ] 既存Layeredテンプレート再利用
[ ] 背景はupdate_fill
[ ] 文字はCanvaテキストのみ
[ ] 旧作品本文0件 / 旧背景0枚 / 旧タイトル0件
[ ] 通常QC / 旧テーマQC / 旧色QC / 改行QC / Brand Label QC / 縮小QC
[ ] ユーザーへプレビュー提示
[ ] 現在プレビューへの保存承認
[ ] commit成功
[ ] post-commit read-back
[ ] final folderへ完成デザイン移動
[ ] final folder item audit
[ ] TikTokタイトル
[ ] Caption / Pinned Comment / BGM方向性
[ ] Production Pack
[ ] 保存先とURLを報告
```

---

# 24. 各投稿から得た確定知見

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
- 背景生成と文字入れを明確に分離する
- 生成順と最終Page順がズレる場合があるため、内容ベースでImage Mappingする
- Canvaアップロード後は01〜番号とサムネイルで対応確認する
- 因果的履歴が論点の場合、物理状態・行動と心的状態を区別する
- 編集完了と保存完了を区別する

## #007 中国語の部屋｜2026-08-29追記

今回の主要な躓き：

1. **旧作品テンプレートを新作フォルダへ早く移動した**
   - 6作目「ペーパークリップ・マキシマイザー」の複製が「中国語の部屋」フォルダに入り、新作フォルダが汚染された。
   - 対策：working copyはcommit後までstaging。final folderは完成物だけを置く。

2. **draft編集を保存済みと誤認した**
   - プレビュー上では中国語の部屋に差し替わっていたが、commitされておらず、再読込すると6作目の内容へ戻っていた。
   - 対策：PREVIEWEDとCOMMITTEDを明確に分離。commit成功前に「保存済み」と言わない。

3. **commit直後のread-backが不足していた**
   - 保存結果を再度開いて確認していれば、旧内容残存を早期発見できた。
   - 対策：commit後に必ずPage 1 / Reveal / Final / background asset / titleを再読込確認する。

4. **フォルダ監査を最後に行っていなかった**
   - ユーザー側でフォルダを見るまで、前作品デザインの混在を検知できなかった。
   - 対策：完成報告前にfinal folderをlistし、期待件数とアイテム名を照合する。

5. **Brand colorの標準が旧マニュアルと実運用でズレていた**
   - 旧マニュアルはブランド名 #FFFFFF としていたが、現行運用では #F2F3F5 を基本色、#FFB000 を標準アクセントとして統一する方が再現性が高い。
   - 対策：v1.6からBrand Shell tokenを更新。

6. **中国語の部屋を「AIは理解していない証明」と断定しない**
   - この思考実験は、形式的な記号操作と意味理解が同じかを問う。反論も存在する。
   - 対策：Reveal / Pointでは問いを明確化し、結論を固定しない。

### #007で確立した保存の原則

```text
編集する
→ プレビューする
→ 承認を得る
→ commitする
→ 再読込する
→ 内容を確認する
→ final folderへ移動する
→ folderを再列挙する
→ 期待件数・旧作0件を確認する
→ 完成報告
```

### 共通結論

- 説明より参加
- 背景は文字なし
- 文字はCanvaで編集可能にする
- Brand Shellは固定、Episode Skinは可変
- 画像順は内容で確定
- ブランド名・ページ番号は #F2F3F5
- テキスト色は原則2色へ抑える
- working copyとfinal folderを分離する
- commitとread-backをセットにする
- folder auditまでが保存工程
- 回答データを次投稿へ戻す

---

## 付記：動画パイプラインとの関係

縦型動画パイプラインは将来展開・比較検証用として保持する。現時点のTikTok初期運用では、本マニュアルの写真カルーセル制作フローを優先する。
