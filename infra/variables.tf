variable "aws_region" {
  description = "AWS リージョン"
  default     = "ap-northeast-1"
}

variable "app_name" {
  description = "アプリケーション名（リソース名のプレフィックス）"
  default     = "fitlog"
}

variable "env" {
  description = "デプロイ環境"
  default     = "prod"
}

variable "db_username" {
  description = "RDS マスターユーザー名"
  sensitive   = true
}

variable "db_password" {
  description = "RDS マスターパスワード"
  sensitive   = true
}

variable "jwt_secret" {
  description = "JWT 署名シークレット（256bit 以上推奨）"
  sensitive   = true
}
