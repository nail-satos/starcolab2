### 必要な標準ライブラリをインポートする ###
import re

def isInteger(value):
    """
    整数チェック
    :param value: チェック対象の文字列
    :rtype: チェック対象文字列が、全て数値の場合 True
    """
    return re.match(r"^\d+$", value) is not None


def isDecimal(value):
    """
    小数チェック
    :param value: チェック対象の文字列
    :rtype: チェック対象文字列が、整数または小数の場合 True True
    """
    return re.match(r"^[+-]?[0-9]*[.]?[0-9]+$", value) is not None


def isAlpha(value):
    """
    半角英字チェック
    :param value: チェック対象の文字列
    :rtype: チェック対象文字列が、全て半角英字の場合 True
    """
    return re.match(r"^[a-z]+$", value) is not None


# 文字列が半角の英数字のみで構成されているかどうかを判定
def isalnum_ascii(s):  # 文字列のメソッドを使用
    return True if s.isalnum() and s.isascii() else False
# ［解決！Python］文字列が英数字（文字および数字）のみで構成されているかどうかを判定するには（isalnum／isasciiメソッド、正規表現）：解決！Python - ＠IT
# https://atmarkit.itmedia.co.jp/ait/articles/2102/26/news035.html

# def isAlphaNumeric(value):
#     """
#     半角英数字チェック
#     :param value: チェック対象の文字列
#     :rtype: チェック対象文字列が、全て半角英数字の場合 True
#     """
#     return re.match(r"^\w+$", value) is not None


def isHalf(value):
    """
    半角文字チェック
    :param value: チェック対象の文字列
    :rtype: チェック対象文字列が、全て半角文字の場合 True (半角カナは含まない)
    """
    return re.match(r"^[\x20-\x7E]+$", value) is not None


def isHalfKana(value):
    """
    半角カナチェック
    :param value: チェック対象の文字列
    :rtype: チェック対象文字列が、全て半角カナの場合 True
    """
    return re.match(r"^[ｦ-ﾟ]+$", value) is not None


def isFull(value):
    """
    全角文字チェック
    :param value: チェック対象の文字列
    :rtype: チェック対象文字列が、全て全角文字の場合 True 
    """
    return re.match(r"^[^\x01-\x7E]+$", value) is not None


# Pythonで正規表現を使って数値/英字チェックを実装する (コピペ用)-スケ郎のお話
# https://www.sukerou.com/2018/12/python.html
