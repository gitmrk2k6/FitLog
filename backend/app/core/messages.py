"""ユーザー向け日本語メッセージの単一ソース。

docs/functional-requirements.md でログイン失敗の文言のみ確定しているため
それを正とし、その他は要件の趣旨に沿った暫定文言として一元管理する。
"""

# F-01 認証
EMAIL_ALREADY_REGISTERED = "このメールアドレスは既に登録されています"
USERNAME_ALREADY_TAKEN = "このユーザー名は既に使用されています"
WEAK_PASSWORD = "パスワードは8文字以上で、英字と数字を両方含めてください"
INVALID_CREDENTIALS = "メールアドレスまたはパスワードが正しくありません"
NOT_AUTHENTICATED = "認証が必要です"
