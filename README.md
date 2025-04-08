# cflpy - 文脈自由言語 with Python

文脈自由文法(CFG)を操作するための Python ライブラリです。文法の定義、文字列の生成、メンバーシップ判定、チョムスキー標準形への変換などの機能を提供します。

## ガイド

### 基本機能

cflpy は文脈自由文法(CFG)を操作するための Python ライブラリです。主な機能は以下の通りです:

- `CFGrammar`クラス: 文脈自由文法の基本操作

  - 文法の定義(非終端記号、終端記号、開始記号、生成規則)
  - 文字列の生成
  - 言語へのメンバーシップ判定

- `CFGParser`クラス: 文法定義ファイル(.cfl)の解析
  - ファイル/文字列からの文法構築
  - カスタム構文解析設定(区切り文字など)

### チョムスキー標準形(CNF)変換

文法をチョムスキー標準形に変換する機能を提供します。変換は 5 つのステップで行われます:

1. **開始記号の処理**: 開始記号が右辺に現れる場合、新しい開始記号を追加
2. **ε 規則の除去**: 空文字列を生成する規則を除去
3. **単位規則の除去**: A→B 形式の規則を除去
4. **長い規則の分解**: 右辺が 3 つ以上の記号を持つ規則を 2 記号規則に分解
5. **終端記号の処理**: 2 項規則中の終端記号を非終端記号で置換

```python
grammar = CFGrammar(...)
cnf_grammar = grammar.to_chomsky_normal_form()
```

### 文字列操作

- **文字列生成**: 文法からランダムに文字列を生成

  ```python
  grammar.generate_string()  # 1つの文字列を生成
  grammar.generate_strings(5)  # 5つの文字列を生成
  ```

- **メンバーシップ判定**: 文字列が言語に含まれるか判定(CYK アルゴリズム)
  ```python
  cnf_grammar.is_member("a b c")  # True/False
  ```

### ファイル入出力

.cfl 形式のファイルから文法を読み込み:

```python
from cflpy import CFGParser
parser = CFGParser()
grammar = parser.from_file("path/to/grammar.cfl")
```

文法ファイルの例:

```
<S> := <A> <B> | "a"
<A> := "a" <A> | ε
<B> := "b" "c" | <B> "d"
```
