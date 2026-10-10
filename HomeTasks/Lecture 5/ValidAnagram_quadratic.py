class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        remaining = list(t)

        for char in s:
            if char not in remaining:
                return False

            remaining.remove(char)

        return True