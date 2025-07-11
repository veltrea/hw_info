# ハードウェア情報収集ツール

このツールは、Windowsシステムのハードウェア情報を収集し、様々な形式で出力するPythonベースのユーティリティです。

## 機能

- システム、CPU、メモリ、ストレージ、GPU、マザーボードの情報収集
- 複数の出力形式（テキスト、JSON、YAML、CSV）
- 詳細度の調整（最小限/詳細）
- シリアル番号の除外オプション
- ファイル出力サポート
- UTF-8エンコーディングサポート

## インストール

1. 必要な依存関係をインストール：
```bash
pip install -r requirements.txt
```

2. 実行ファイルを生成（オプション）：
```bash
pyinstaller --onefile hw_info.py
```

## 使用方法

### 基本的な使用方法

```bash
# すべての情報を表示（デフォルト：テキスト形式）
hw_info.exe

# JSON形式で出力
hw_info.exe --format json

# 整形されたJSON形式で出力
hw_info.exe --format json --pretty
```

### 出力形式の指定

```bash
# YAML形式で出力
hw_info.exe --format yaml

# CSV形式で出力
hw_info.exe --format csv
```

### コンポーネントの選択

```bash
# すべてのコンポーネント情報を表示
hw_info.exe --all

# CPU情報のみ表示
hw_info.exe --cpu

# メモリ情報のみ表示
hw_info.exe --memory

# ストレージ情報のみ表示
hw_info.exe --storage

# GPU情報のみ表示
hw_info.exe --gpu

# マザーボード情報のみ表示
hw_info.exe --motherboard
```

### その他のオプション

```bash
# 最小限の情報を表示
hw_info.exe --minimal

# シリアル番号を除外
hw_info.exe --exclude-serials

# ファイルに出力
hw_info.exe --output hardware_info.json

# タイムスタンプを除外
hw_info.exe --no-timestamps

# UTF-8エンコーディングで出力
hw_info.exe --utf8
```

## 実行ファイルの生成

PyInstallerを使用して実行ファイルを生成できます：

```bash
pyinstaller --onefile hw_info.py
```

生成された実行ファイルは`dist`ディレクトリに配置されます。

## テスト

ユニットテストを実行するには：

```bash
python -m unittest test_hw_info.py
```

## 要件

- Python 3.6以上
- Windows OS
- psutil>=5.9.0
- wmi>=1.5.1
- PyYAML>=6.0.1

## ライセンス

MIT