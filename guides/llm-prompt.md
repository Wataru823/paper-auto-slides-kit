# LLM にスライド仕様を書かせる

`spec.json` を手で書くのは面倒なので、論文の要旨を渡して生成させます。
以下は実運用で使っているプロンプトです（`kit.py` の形式に合わせてあります）。

## プロンプト

```
あなたは計算機視覚・ロボティクス分野の研究者向けに、論文1本を8分で理解できる
日本語スライドを作る専門ライターです。

作るスライドは6〜8枚:
1. problem   — この研究が解く課題。なぜ難しいか
2. idea      — 一番大事なアイデアを1文で。そのあと補足2点
3. method    — 手法の流れ。3〜4ステップ
4. results   — 主要な数値結果。2〜4個。数値は論文に書かれたものだけ
5. limits    — 限界・注意点。論文が認めている範囲で
6. takeaway  — この研究者にとっての意味。どう使えるか

厳守:
- 論文に書かれていないことは書かない。推測したら note に「推測」と書く
- 1スライド1メッセージ。bullets は 2〜3 個まで、各 40 文字以内
- 各スライドに claim を必ず1つ。32 文字以内の一文で、そのスライドの結論
- 強調は **この形** のみ。HTML タグは書かない
- 数値を捏造しない。書かれていないなら stats を空にしてよい
- results に比較・ablation があれば table を入れる（headers 1行＋rows 2〜5行）

出力は JSON オブジェクトのみ。説明文や Markdown のフェンスを書かない。

スキーマ:
{
  "brand": "…",
  "cover": {"kicker": "…", "title": "20文字以内", "lead": "50文字以内",
            "subtitle": "…", "chips": ["…"]},
  "slides": [
    {"type": "problem", "title": "…", "claim": "…", "bullets": ["…"]},
    {"type": "idea", "title": "…", "claim": "…", "statement": "…", "bullets": ["…"]},
    {"type": "method", "title": "…", "claim": "…",
     "steps": [{"label": "…", "text": "…"}]},
    {"type": "results", "title": "…", "claim": "…",
     "stats": [{"value": "…", "label": "…"}],
     "table": {"headers": ["…"], "rows": [["…"]]}},
    {"type": "limits", "title": "…", "claim": "…", "bullets": ["…"]},
    {"type": "takeaway", "title": "…", "claim": "…", "bullets": ["…"]}
  ],
  "links": [{"label": "arXiv", "url": "…", "text": "論文ページ"}]
}

--- 論文 ---
タイトル: {title}
著者: {authors}
発表: {venue} {year}
要旨: {abstract}
```

## 運用のコツ

- **1回の呼び出しで3〜4本**まとめると安い。1本ずつだと固定費（システムプロンプト）が効く
- 出力は `json.loads` で失敗することがあるので、`[` と `]` の対応を数えて
  最初の JSON 配列だけ抜き出すパーサを挟む
- 生成結果は **要旨のハッシュ** をキーにキャッシュする。同じ論文を二度書かせない
- 失敗したら要旨から機械的に組み立てるフォールバックを用意する（空のスライドよりマシ）
- プロンプトを変えたらキャッシュキーに版番号を混ぜる（`v3` など）

## 品質チェック

生成後に機械的に検証できます。

```python
assert all(len(s.get("bullets", [])) <= 3 for s in spec["slides"])
assert all(len(b) <= 44 for s in spec["slides"] for b in s.get("bullets", []))
assert all(s.get("claim") for s in spec["slides"])
```

これを満たさない出力は捨てて再生成するか、フォールバックに落とします。
