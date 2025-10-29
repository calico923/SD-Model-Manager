"""pytest が正しく動作することを確認するサンプルテスト"""


def test_sample_addition():
    """基本的な演算のテスト"""
    assert 1 + 1 == 2


def test_sample_string():
    """文字列操作のテスト"""
    text = "Hello, TDD!"
    assert text.startswith("Hello")
    assert "TDD" in text
