terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # State ファイルを S3 で管理
  # このバケット自体は Terraform 管理外（手動で事前作成が必要）
  # 作成手順: docs/deploy.md を参照
  backend "s3" {
    bucket = "fitlog-tfstate"
    key    = "prod/terraform.tfstate"
    region = "ap-northeast-1"
  }
}

provider "aws" {
  region = var.aws_region
}
