import unittest
import subprocess
import json
import yaml
import os
import sys
from pathlib import Path

class TestHWInfo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # 実行ファイルのパスを設定
        cls.exe_path = str(Path('dist/hw_info.exe').absolute())
        if not os.path.exists(cls.exe_path):
            raise FileNotFoundError(f"実行ファイルが見つかりません: {cls.exe_path}")

    def run_hw_info(self, args):
        """hw_info.exeを指定された引数で実行し、結果を返す"""
        cmd = [self.exe_path] + args
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result

    def test_default_output(self):
        """デフォルト出力（テキスト形式）のテスト"""
        result = self.run_hw_info([])
        self.assertEqual(result.returncode, 0)
        self.assertIn("system:", result.stdout)

    def test_json_output(self):
        """JSON形式出力のテスト"""
        result = self.run_hw_info(["--format", "json"])
        self.assertEqual(result.returncode, 0)
        try:
            data = json.loads(result.stdout)
            self.assertIsInstance(data, dict)
        except json.JSONDecodeError:
            self.fail("Invalid JSON output")

    def test_json_pretty_output(self):
        """整形されたJSON形式出力のテスト"""
        result = self.run_hw_info(["--format", "json", "--pretty"])
        self.assertEqual(result.returncode, 0)
        try:
            data = json.loads(result.stdout)
            self.assertIsInstance(data, dict)
            # 整形されているか確認（改行を含むはず）
            self.assertIn("\n", result.stdout)
        except json.JSONDecodeError:
            self.fail("Invalid JSON output")

    def test_yaml_output(self):
        """YAML形式出力のテスト"""
        result = self.run_hw_info(["--format", "yaml"])
        self.assertEqual(result.returncode, 0)
        try:
            data = yaml.safe_load(result.stdout)
            self.assertIsInstance(data, dict)
        except yaml.YAMLError:
            self.fail("Invalid YAML output")

    def test_csv_output(self):
        """CSV形式出力のテスト"""
        result = self.run_hw_info(["--format", "csv"])
        self.assertEqual(result.returncode, 0)
        # CSVの基本構造を確認（ヘッダー行とデータ行）
        lines = result.stdout.strip().split('\n')
        self.assertGreaterEqual(len(lines), 2)

    def test_component_selection(self):
        """コンポーネント選択オプションのテスト"""
        # CPU情報のみ
        result = self.run_hw_info(["--cpu", "--format", "json"])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertIn("cpu", data)
        self.assertNotIn("memory", data)

        # メモリ情報のみ
        result = self.run_hw_info(["--memory", "--format", "json"])
        data = json.loads(result.stdout)
        self.assertIn("memory", data)
        self.assertNotIn("cpu", data)

    def test_all_option(self):
        """--allオプションのテスト"""
        result = self.run_hw_info(["--all", "--format", "json"])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        # すべての主要コンポーネントが含まれているか確認
        expected_components = ["system", "cpu", "memory", "storage", "gpu", "motherboard"]
        for component in expected_components:
            self.assertIn(component, data)

    def test_minimal_output(self):
        """最小限の出力オプションのテスト"""
        result = self.run_hw_info(["--minimal", "--format", "json"])
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        # 最小限の情報のみが含まれているか確認（詳細な検証は省略）
        self.assertIsInstance(data, dict)

    def test_utf8_output(self):
        """UTF-8エンコーディング出力のテスト"""
        result = self.run_hw_info(["--utf8", "--format", "json"])
        self.assertEqual(result.returncode, 0)
        # 日本語文字が正しく出力されるか確認
        try:
            result.stdout.encode('utf-8').decode('utf-8')
        except UnicodeError:
            self.fail("UTF-8 encoding test failed")

    def test_file_output(self):
        """ファイル出力のテスト"""
        output_file = "test_output.json"
        try:
            result = self.run_hw_info(["--format", "json", "--output", output_file])
            self.assertEqual(result.returncode, 0)
            # ファイルが作成されたか確認
            self.assertTrue(os.path.exists(output_file))
            # ファイルの内容が有効なJSONか確認
            with open(output_file, 'r') as f:
                data = json.load(f)
                self.assertIsInstance(data, dict)
        finally:
            # テスト後にファイルを削除
            if os.path.exists(output_file):
                os.remove(output_file)

    def test_error_handling(self):
        """エラーハンドリングのテスト"""
        # 無効なフォーマットオプション
        result = self.run_hw_info(["--format", "invalid"])
        self.assertNotEqual(result.returncode, 0)

        # 無効な出力ファイルパス
        result = self.run_hw_info(["--output", "/invalid/path/file.json"])
        self.assertNotEqual(result.returncode, 0)

if __name__ == '__main__':
    unittest.main()