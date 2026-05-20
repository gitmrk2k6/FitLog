resource "aws_ecs_cluster" "main" {
  name = "${var.app_name}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = { Name = "${var.app_name}-cluster" }
}

# Secrets Manager（DB パスワード・JWT シークレット）
resource "aws_secretsmanager_secret" "db_password" {
  name = "/${var.app_name}/${var.env}/db-password"
}

resource "aws_secretsmanager_secret_version" "db_password" {
  secret_id     = aws_secretsmanager_secret.db_password.id
  secret_string = var.db_password
}

resource "aws_secretsmanager_secret" "jwt_secret" {
  name = "/${var.app_name}/${var.env}/jwt-secret"
}

resource "aws_secretsmanager_secret_version" "jwt_secret" {
  secret_id     = aws_secretsmanager_secret.jwt_secret.id
  secret_string = var.jwt_secret
}

# CloudWatch Logs
resource "aws_cloudwatch_log_group" "backend" {
  name              = "/ecs/${var.app_name}-backend"
  retention_in_days = 30
}

# ECS タスク実行ロール（ECR pull・Secrets Manager 読み取り）
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.app_name}-ecs-task-execution"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "ecs_task_execution_secrets" {
  name = "secrets-access"
  role = aws_iam_role.ecs_task_execution.id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = ["secretsmanager:GetSecretValue"]
      Resource = [
        aws_secretsmanager_secret.db_password.arn,
        aws_secretsmanager_secret.jwt_secret.arn,
      ]
    }]
  })
}

# ECS タスクロール（S3 写真アップロード権限）
resource "aws_iam_role" "ecs_task" {
  name = "${var.app_name}-ecs-task"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_s3" {
  role       = aws_iam_role.ecs_task.name
  policy_arn = aws_iam_policy.s3_media_write.arn
}

# ECS タスク定義（FastAPI + Alembic）
# DB パスワードは entrypoint.sh で DATABASE_URL を組み立てる方式（ECS コンソール非表示）
resource "aws_ecs_task_definition" "backend" {
  family                   = "${var.app_name}-backend"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name      = "backend"
    image     = "${aws_ecr_repository.backend.repository_url}:latest"
    essential = true
    portMappings = [{ containerPort = 8000, protocol = "tcp" }]

    environment = [
      { name = "DB_USERNAME",                  value = var.db_username },
      { name = "DB_HOST",                      value = aws_db_instance.main.address },
      { name = "STORAGE_BACKEND",              value = "s3" },
      { name = "s3_bucket",                    value = aws_s3_bucket.media.bucket },
      { name = "s3_region",                    value = var.aws_region },
      { name = "s3_public_base_url",           value = "https://${aws_cloudfront_distribution.media.domain_name}" },
      { name = "FRONTEND_ORIGIN",              value = "https://${aws_cloudfront_distribution.main.domain_name}" },
      { name = "env",                          value = "production" },
      { name = "log_level",                    value = "INFO" },
      { name = "ACCESS_TOKEN_EXPIRE_MINUTES",  value = "60" },
    ]

    secrets = [
      { name = "DB_PASSWORD",  valueFrom = aws_secretsmanager_secret.db_password.arn },
      { name = "SECRET_KEY",   valueFrom = aws_secretsmanager_secret.jwt_secret.arn },
    ]

    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.backend.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "ecs"
      }
    }

    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 120
    }
  }])
}

# ECS サービス（パブリックサブネット、公開 IP 付与でインターネット到達可）
resource "aws_ecs_service" "backend" {
  name            = "${var.app_name}-backend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.backend.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = [aws_subnet.public_1a.id, aws_subnet.public_1c.id]
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.backend.arn
    container_name   = "backend"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]
}
