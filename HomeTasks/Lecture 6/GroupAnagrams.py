class Solution:
    def groupAnagrams(self, strs: list[str]) -> list[list[str]]:
        groups = {}

        for word in strs:
            frequency = [0] * 26

            for char in word:
                frequency[ord(char) - ord("a")] += 1

            key = tuple(frequency)

            if key not in groups:
                groups[key] = []

            groups[key].append(word)

        return list(groups.values())


# Временная сложность — O(n), где n — общее количество символов во всех словах.
# HashMap подходит, потому что слова с одинаковым частотным словарём являются анаграммами и получают общий ключ.
# Пространственная сложность — O(n), так как все слова сохраняются в группах.
