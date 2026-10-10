class Solution:
    def twoSum(self, nums: list[int], target: int) -> list[int]:
        waiting = {}

        for position, number in enumerate(nums):
            partner_position = waiting.get(number)

            if partner_position is not None:
                return [partner_position, position]

            waiting[target - number] = position
