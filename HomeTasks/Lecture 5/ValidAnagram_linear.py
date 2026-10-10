class Solution:
    def isAnagram(self, s: str, t: str) -> bool:
        if len(s) != len(t):
            return False

        frequency = {}

        for char in s:
            frequency[char] = frequency.get(char, 0) + 1

        for char in t:
            if frequency.get(char, 0) == 0:
                return False

            frequency[char] -= 1

        return True