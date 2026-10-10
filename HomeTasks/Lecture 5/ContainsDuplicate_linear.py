class Solution:
    def containsDuplicate(self, nums: list[int]) -> bool:
        encountered = set()

        for number in nums:
            if number in encountered:
                return True

            encountered.add(number)

        return False