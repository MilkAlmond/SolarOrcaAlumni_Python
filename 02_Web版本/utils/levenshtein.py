# utils/levenshtein.py
# 字符串相似度工具（Levenshtein 编辑距离）

from typing import Optional


def get_levenshtein_distance(s1: Optional[str], s2: Optional[str]) -> int:
    """
    计算两个字符串的 Levenshtein 编辑距离。
    使用动态规划算法，时间复杂度 O(n×m)。

    参数：
        s1: 第一个字符串
        s2: 第二个字符串

    返回：
        编辑距离（最小编辑操作次数），任一参数为 None 时返回 999999
    """
    if s1 is None or s2 is None:
        return 999999

    a = s1.lower()
    b = s2.lower()

    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]

    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j

    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i-1] == b[j-1] else 1
            dp[i][j] = min(
                dp[i-1][j] + 1,
                dp[i][j-1] + 1,
                dp[i-1][j-1] + cost
            )

    return dp[len(a)][len(b)]


def get_similarity(s1: Optional[str], s2: Optional[str]) -> float:
    """
    计算两个字符串的相似度百分比（0-100）。
    相似度 = (1 - 编辑距离 / 最大长度) × 100%

    参数：
        s1: 第一个字符串
        s2: 第二个字符串

    返回：
        相似度百分比，任一参数为 None 时返回 0
    """
    if s1 is None or s2 is None:
        return 0.0

    distance = get_levenshtein_distance(s1, s2)
    max_len = max(len(s1), len(s2))

    if max_len == 0:
        return 100.0

    return (1.0 - distance / max_len) * 100