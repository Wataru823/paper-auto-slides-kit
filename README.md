# PaperGaki Slides Kit

論文1本を、**8枚の日本語スライド**に落とすための最小キット。
依存パッケージなし・ビルドなし。HTML を開けばそのまま発表できます。

- **1920×1080 の固定ステージ** — 画面幅で文字サイズが変わらない
- **1スライド1メッセージ** — 箇条書きは3項目まで、各40文字以内
- **図・表・動画のどれかを必ず1つ** — 文字だけのスライドを作らない
- **締めの一文** — タイトル直下に「この1枚で言いたいこと」を置く
- **キーボード操作** — `←` `→` 移動、`F` 全画面、`P` 印刷（PDF化）

```
examples/index.html   ← デモ（このキット自身の説明スライド）
```

## クイックスタート

```bash
git clone https://github.com/Wataru823/papergaki-slides-kit.git
cd papergaki-slides-kit
python3 kit.py examples/spec.json examples/index.html
open examples/index.html
```

`kit.py` は JSON を HTML に変換するだけの 300 行です。サーバーもビルドも要りません。

## 仕様（spec.json）

```jsonc
{
  "brand": "PaperGaki Slides Kit",
  "cover": {
    "kicker": "PAPERGAKI · SLIDES KIT",
    "title": "読ませず、**見せる**スライド",   // **強調** だけ使える
    "lead": "1文の要約",
    "subtitle": "補足の一行",
    "chips": ["1920×1080 固定", "依存なし"],
    "image": "../docs/example-results.jpg"   // 無くてもよい
  },
  "slides": [
    {
      "type": "problem",              // problem / idea / method / results / limits / takeaway / detail
      "title": "見出し",
      "claim": "この1枚で言いたいこと（1文）",
      "bullets": ["3項目まで", "各40文字以内"],
      "note": "補足（任意）"
    },
    {
      "type": "method",
      "title": "手順",
      "claim": "…",
      "steps": [{ "label": "短い見出し", "text": "1文" }],
      "media": { "kind": "image", "src": "../docs/layout-anatomy.png" }
    },
    {
      "type": "results",
      "title": "結果",
      "claim": "…",
      "stats": [{ "value": "92.7%", "label": "何の数値か" }],
      "table": {
        "headers": ["項目", "Before", "After"],
        "rows": [["箇条書きの数", "6〜8", "3"]]
      }
    }
  ],
  "links": [{ "label": "arXiv", "url": "https://…", "text": "論文ページ" }]
}
```

| キー | 効果 |
|---|---|
| `statement` | 大きく出す1文（`idea` 用） |
| `steps` | 番号付きの手順。3件なら行が広く、4件なら詰まる |
| `stats` | 数値カード。`table` があるときは自動で省略 |
| `table` | 比較表。ヘッダ1行＋本文6行まで |
| `media.band` | `true` で図を全幅の帯に（横長の図向け） |
| `cite` | 見出しの右に `[CoRL 2026]` を付ける |
| `section` | セクションバーのラベルを上書き |

## 設計の根拠

[docs/DESIGN.md](DESIGN.md) に、余白・文字サイズ・色数・図表の置き方をまとめています。
「なぜこの形なのか」を知りたいときはそちらを。

## LLM に書かせる

[guides/llm-prompt.md](guides/llm-prompt.md) に、論文の要旨からこの `spec.json` を
生成させるためのプロンプトを置いています。実運用では毎朝10本ぶんを自動生成しています。

## 発表前チェック

[guides/checklist.md](guides/checklist.md)

## 元ネタ

- [伝わるデザイン](https://student.tsutawarudesign.com/powerpoint_slide/) — 情報量と色数の原則
- [frontend-slides](https://github.com/zarazhangrui/frontend-slides) — 固定ステージ方式

実用例: [papergaki-slides](https://wataru823.github.io/papergaki-slides/)（論文の自動スライド）

## License

MIT
