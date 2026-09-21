import string

# Знаки препинания (латинские и типографские; как ispunct в Си)
PUNCT = set(string.punctuation) | set("«»–—…")

REQUIREMENTS = ("Пароль должен содержать строчные и прописные буквы "
                "и знаки препинания.")


# Проверка ограничений на пароль (вариант 13)
def check_password(pw: str) -> bool:
    """Есть строчная буква, прописная буква и знак препинания."""
    has_upper = any(c.isalpha() and c.isupper() for c in pw)
    has_lower = any(c.isalpha() and c.islower() for c in pw)
    has_punct = any(c in PUNCT for c in pw)
    return has_upper and has_lower and has_punct