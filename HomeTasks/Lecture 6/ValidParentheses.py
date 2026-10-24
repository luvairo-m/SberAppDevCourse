class Solution:
    def isValid(self, s: str) -> bool:
        stack = []
        matching_brackets = {
            ")": "(",
            "]": "[",
            "}": "{",
        }

        for bracket in s:
            if bracket in matching_brackets.values():
                stack.append(bracket)
            elif not stack or stack[-1] != matching_brackets[bracket]:
                return False
            else:
                stack.pop()

        return len(stack) == 0


# Временная сложность — O(n), потому что строка просматривается один раз.
# Стек подходит, так как закрывающая скобка относится к последней открытой — это LIFO.
# Пространственная сложность — O(n) в случае, если строка состоит из открывающих скобок.
