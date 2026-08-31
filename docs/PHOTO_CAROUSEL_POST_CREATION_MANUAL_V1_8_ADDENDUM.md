# 1分思考実験｜TikTok写真カルーセル投稿 作成マニュアル v1.8 追補

Version: 1.8 Addendum  
Updated: 2026-09-01  
Validated in this addendum: #011 バイオリニスト

> 本文書は `PHOTO_CAROUSEL_POST_CREATION_MANUAL.md` v1.6 および v1.7 Addendum の追補である。内容が競合する場合、より新しい追補を優先する。

---

## 1. #011 バイオリニストで発生した主要な躓き

#011では、最終的なCanva成果物は完成したが、制作途中で主に4種類の問題が発生した。

1. **背景画像生成で、背景1枚ではなく文字入りストーリーボード／企画書風画像が生成された**
2. **代替背景の一部がページの意味と弱くしか一致せず、後から差し替えが必要になった**
3. **Canvaの編集トランザクションが保存承認まで維持されず、ドラフト内容を復元して再commitする必要が生じた**
4. **Page 8など、旧テンプレートの配置をそのまま使うとTikTok右UI安全域に寄り過ぎる箇所があった**

これらを今後の標準工程に反映する。

---

## 2. 背景画像生成は「1枚の背景写真」以外を絶対に生成しない

#011で最初の画像生成に、企画意図・ページ役割・台本情報を含めすぎた結果、生成器が「背景画像」ではなく**ストーリーボード／インフォグラフィック／企画書**として解釈した。

### 今後の絶対ルール

背景画像生成プロンプトには、次を入れない。

```text
- Page 1 / Page 2 などのページ番号
- HOOK / REVEAL / YOUR CHOICE などの制作ラベル
- 台本全文
- 投稿本文
- A/B選択肢
- 秒数・尺
- ハッシュタグ
- 制作メモ
- 表・レイアウト指示
- ストーリーボードという語
- インフォグラフィックという語
```

生成器へ渡すのは原則として**視覚情報だけ**にする。

### 推奨プロンプト構造

```text
1枚の縦長9:16背景写真だけ。

Scene:
- 何が写っているか
- カメラ位置
- 照明
- 色調
- 人物・物体
- Text Zone

Do not include:
- text
- letters
- numbers
- symbols
- logos
- UI
- labels
- subtitles
- diagrams
- panels
- borders
- collage
- storyboard
- infographic
- watermark
```

### 失敗時の処理

文字入り・複数分割・ストーリーボードが出た場合、その画像を「ほぼ使える」と評価しない。

```text
失敗画像
→ 不採用
→ プロンプトを短くする
→ 背景1枚だけで再生成
```

一度企画書化した生成結果を何度も部分修正して救済しようとしない。

**背景生成と投稿コピー制作は工程を完全に分離する。**

---

## 3. 背景画像8枚はCanva投入前に「意味一致QC」を通す

#011では、縦1080×1920という形式は合っていても、ページの意味との一致が弱い背景が一部混ざった。

今後は、ファイル名・サイズだけで背景を合格にしない。

### Background Semantic QC

全8枚について、Canvaへ配置する前にサムネイルで確認する。

```text
[ ] そのページの役割と画面内容が一致している
[ ] 重要オブジェクトが存在する
[ ] 別テーマに見えない
[ ] 文字・数字・ロゴ・UIが焼き込まれていない
[ ] 画像だけで過剰な説明をしていない
[ ] Text Zoneが確保されている
[ ] 8枚の世界観・色調が大きく分断されていない
[ ] 人物の顔・服・病室などの連続性が必要な作品では矛盾が大きくない
```

### 重要

`1080×1920` かつ暗い画像であっても、それだけでは合格ではない。

例：

```text
Choiceページなのに一般オフィスに見える
Connectionページなのに人物だけで接続構造が伝わらない
Revealページなのにテーマ固有物がない
```

この場合は**Canvaに置いてから妥協せず、背景assetの段階で差し替える。**

---

## 4. 外部ストック画像は「緊急fallback」に限定する

背景生成が不調な場合、外部ストック画像を使うと工程は前進できるが、以下の弱点がある。

- 同一人物・同一空間の連続性を作りにくい
- テーマ固有の状況を正確に再現しにくい
- ページごとに撮影条件・色温度・構図が変わりやすい
- 一見きれいでも「そのページの意味」と弱くしか一致しないことがある

したがって今後の優先順位は：

```text
1. テーマ専用に生成した背景
2. 再生成・プロンプト簡素化
3. 既存の高品質な専用asset
4. 外部ストック画像（緊急fallback）
```

ストックを使う場合も、**8枚セットとしてSemantic QC / visual continuity QCを行う。**

---

## 5. Canvaトランザクションは「ドラフトは消える前提」で扱う

#011では、全8ページの編集・プレビューまで完了した後、ユーザーの「保存」回答時点で元の編集トランザクションをそのままcommitできず、再読込すると旧作品の状態へ戻っていた。

これは重要な運用知見である。

### 新しい原則

> Canvaの未commit編集は、次のターンまで確実に残るとは考えない。

### 正しい保存フロー

```text
編集開始
↓
全編集
↓
全ページthumbnail QC
↓
ユーザーへプレビュー
↓
明示的な「保存」承認
↓
同じtransaction_idを最優先で即commit
↓
commit成功レスポンス確認
↓
新規read-back
↓
保存済み内容を再確認
```

### 禁止事項

```text
- 保存承認後に、理由なく新しいediting transactionを開始する
- commit前に別Design IDへ移動する
- draft previewを「保存済み」と表現する
- commit成功レスポンス前に完成報告する
```

---

## 6. トランザクション失効時のRecovery Protocol

保存承認時に、前のtransactionが失効・消失していた場合は、あわててデザインを手作業で再構築しない。

#011では、Production Pack、Canonical Asset IDs、既存element IDsを使うことで同じ編集内容を再適用できた。

### Recoveryの標準手順

```text
1. Canonical Design IDを再確認
2. start-editing-transactionで現状read-back
3. 旧テーマへ戻っていることを確認
4. Production PackのFinal Copyを参照
5. 8枚のCanonical Asset IDを参照
6. 既存text element / fill element IDsへ同じ変更を再適用
7. Page-specific position / resizeも再適用
8. thumbnail QC
9. 既にユーザーから保存承認済みなら、復元内容が同一であることを確認後commit
10. commit後に新しいread-back
```

### Recovery Bundleとして記録するもの

作品ごとのProduction Packには最低限以下を残す。

```text
- Canonical Design ID
- Final Copy 8ページ分
- Canonical Background Asset IDs
- Image Mapping
- Text Zone
- Page-specific位置調整
- final title
```

この情報があれば、ドラフト消失時にも再現可能になる。

---

## 7. 再利用テンプレートでは「削除」より「空文字化」を優先する場合がある

#011のRecoveryでは、一度削除した旧テキスト要素を再現するより、既存element IDを維持して空文字にする方が再適用しやすかった。

今後、旧テンプレートの不要テキスト枠については、次の基準を使う。

### delete_elementを使う

- 明確に不要で、今後も再利用しない
- 残すとレイアウトやクリック操作の邪魔になる
- element IDの安定性が不要

### 空文字化を使う

- テンプレートの固定枠として今後も再利用する可能性がある
- Recovery時にelement IDを維持したい
- 見た目には何も表示されず、レイアウト事故も起こさない

```text
replace_text(..., "")
```

**再現性を重視する場合、固定テンプレート要素のIDをむやみに破壊しない。**

---

## 8. ページ別Text Zoneは旧テンプレート位置を信用しない

#011のPage 8では、旧作品の本文・A/B・CTAが画面右側に寄っており、そのまま新コピーに置換するとTikTokの右UI安全域へ近づいた。

したがって、テンプレート再利用時は：

```text
text replaceだけで完成としない
↓
新しい文章量で実サムネイル確認
↓
必要なら position_element
↓
必要なら resize_element
```

を必須にする。

### 特に確認するページ

- Page 1 Hook
- A/B選択ページ
- Page 8 第二の問い
- 長い哲学的問いのページ

### Safe Area QC

```text
[ ] 右端UI領域に本文が寄っていない
[ ] 下部キャプションUI領域へCTAが沈んでいない
[ ] 文字が背景主役を隠していない
[ ] 自動折り返しで1語だけ次行に落ちていない
```

---

## 9. 「編集成功」「保存成功」「完成」は3段階に分ける

v1.6 / v1.7でも状態分離は定義していたが、#011で改めて重要性が確認された。

### 状態A：DRAFT VALID

```text
編集操作成功
+ thumbnailで見た目が正しい
```

まだ保存済みではない。

### 状態B：COMMITTED

```text
commit-editing-transaction が success / committed
```

保存済みだが、まだ最終確認前。

### 状態C：FINAL VERIFIED

```text
新しいtransactionまたはread-backで内容確認
+ final folder audit
```

この状態になって初めて「完成」と報告する。

---

## 10. #011で追加するFinal Folder Audit

完成フォルダは作品単位で以下を確認する。

```text
[ ] canonical background 8枚
[ ] final design 1件
[ ] 合計9件が基本
[ ] final design titleが作品番号・作品名と一致
[ ] 旧テーマの画像が混在していない
[ ] 旧Working Copyが完成候補として混在していない
```

例：

```text
011.バイオリニスト/
├─ 011_01_HOOK_wakeup.png
├─ 011_02_SCENE_violinist.png
├─ 011_03_CHANGE_connection.png
├─ 011_04_CONFLICT_no_consent.png
├─ 011_05_CHOICE_disconnect.png
├─ 011_06_REVEAL_violin.png
├─ 011_07_POINT_rights.png
├─ 011_08_FINAL_family.png
└─ 011作目｜バイオリニスト｜1分思考実験
```

---

## 11. v1.8 Canva標準フロー

v1.7のフローを以下へ更新する。

```text
1. Fact Pack確定
2. Production Pack / Final Copy確定
3. 背景8枚を1枚ずつ生成
4. Background Semantic QC
5. Canonical asset names / IDs確定
6. 検証済みLayeredテンプレートを1回だけ複製
7. Canonical Working Design ID確定
8. 各ページ既存full-page fill確認
9. update_fillで背景差し替え
10. 既存text elementへFinal Copyを置換
11. Brand Token Reset
12. Page-specific position / resize
13. 全8ページthumbnail QC
14. Layer Visibility QC
15. Old Theme QC
16. Safe Area QC
17. ユーザーへ最終プレビュー
18. 明示承認
19. 同じtransactionを即commit
20. commit成功確認
21. commit後read-back
22. final title確定
23. final folderへ移動
24. final folder audit（8 backgrounds + 1 design）
25. Production PackへDesign ID / commit / QC結果を記録
26. 投稿パッケージ確定
```

---

## 12. v1.8追加セルフチェック

制作開始時：

```text
[ ] 背景生成プロンプトに台本・表・Pageラベルを入れていない
[ ] 背景は「1枚の縦長写真だけ」と明示
[ ] 文字・数字・記号・ロゴ・UI・コラージュを禁止
[ ] 8枚生成後、Canva前にSemantic QCを実施
[ ] Canonical Asset IDsを記録
[ ] Canonical Working Design IDを1件に固定
```

Canva編集時：

```text
[ ] 背景はupdate_fillのみ
[ ] 既存element IDを必要以上に削除していない
[ ] 新しい文章量に合わせてposition / resizeを確認
[ ] Page 8右UI安全域を確認
[ ] 全ページ実サムネイルを取得
```

保存時：

```text
[ ] ユーザーが最終プレビューを確認済み
[ ] 明示的な保存承認がある
[ ] 承認後は同じtransaction_idを即commit
[ ] commit成功レスポンスを確認
[ ] 保存後read-backを実施
[ ] final folderが背景8枚＋完成デザイン1件
```

---

## 13. #011 バイオリニスト｜確定知見

1. **背景生成に制作情報を詰め込みすぎると、ストーリーボード化しやすい。視覚情報だけを渡す。**
2. **文字入り・分割画像が生成されたら救済せず、背景1枚として再生成する。**
3. **1080×1920だから合格ではない。ページの意味との一致をCanva投入前に確認する。**
4. **ストック画像は緊急fallback。テーマ専用生成背景を優先する。**
5. **Canvaの未commit draftは次ターンまで残る前提にしない。**
6. **保存承認後は同じtransactionを最優先で即commitする。**
7. **transaction失効時はProduction Pack＋Asset IDs＋Element IDsから決定論的に復元する。**
8. **固定テンプレートのelement IDを維持するとRecoveryが容易になる。**
9. **旧テンプレートの文字位置を信用せず、新コピーでSafe Areaを再確認する。**
10. **commit後read-backと9件folder auditを通過して初めて完成とする。**

### #011で確立した復旧安全原則

```text
Production Pack
+ Canonical Asset IDs
+ Canonical Design ID
+ Stable element IDs
↓
Deterministic re-apply
↓
Thumbnail QC
↓
Commit
↓
Read-back
↓
Folder audit
```

この復旧経路を今後の標準とする。
