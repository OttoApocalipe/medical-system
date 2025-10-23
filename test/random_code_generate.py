import random
import string


def _generate_code(self, length: int = 6) -> str:
    """生成验证码"""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(random.choice(alphabet) for _ in range(length))


# 测试
if __name__ == "__main__":
    print(_generate_code(6))
