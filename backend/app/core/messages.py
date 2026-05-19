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

# F-04 ナイストレ / F-05 アドバイス
WORKOUT_NOT_FOUND = "記録が見つかりません"
CANNOT_CHEER_OWN = "自分の記録にはナイストレできません"
ALREADY_CHEERED = "すでにナイストレ済みです"
NOT_CHEERED = "ナイストレしていません"
CANNOT_ADVISE_OWN = "自分の記録にはアドバイスできません"
ADVICE_NOT_FOUND = "アドバイスが見つかりません"
NOT_ADVICE_OWNER = "このアドバイスを削除する権限がありません"

# F-06 フォロー
USER_NOT_FOUND = "ユーザーが見つかりません"
CANNOT_FOLLOW_SELF = "自分自身はフォローできません"
ALREADY_FOLLOWING = "すでにフォローしています"
NOT_FOLLOWING = "フォローしていません"
WORKOUT_NOT_VISIBLE = "この記録を閲覧する権限がありません"

# F-07 目標
GOAL_NOT_FOUND = "目標が設定されていません"

# F-10 写真
PHOTO_TYPE_INVALID = "対応していない画像形式です（JPEG / PNG のみ）"
PHOTO_TOO_LARGE = "画像サイズが大きすぎます（最大5MB）"
PHOTO_EMPTY = "画像ファイルが空です"
