resource "random_password" "db_password" {
  length  = 24
  special = false
}

resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnets"
  subnet_ids = aws_subnet.public[*].id
}

# Small non-production RDS instance for the technical-test demo.
resource "aws_db_instance" "loans" {
  identifier             = "${local.name_prefix}-db"
  engine                 = "postgres"
  engine_version         = "16"
  instance_class         = var.db_instance_class
  allocated_storage      = 20
  db_name                = "loans"
  username               = "loan_app"
  password               = random_password.db_password.result
  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false
  skip_final_snapshot    = true

  tags = {
    Name = "${local.name_prefix}-db"
  }
}

locals {
  database_url = "postgresql://${aws_db_instance.loans.username}:${random_password.db_password.result}@${aws_db_instance.loans.address}:${aws_db_instance.loans.port}/${aws_db_instance.loans.db_name}"
  service_url  = "http://${aws_lb.app.dns_name}"
}

resource "aws_secretsmanager_secret" "database_url" {
  name = "${local.name_prefix}/database-url"
}

resource "aws_secretsmanager_secret_version" "database_url" {
  secret_id     = aws_secretsmanager_secret.database_url.id
  secret_string = local.database_url
}

resource "aws_secretsmanager_secret" "auth0_client_secret" {
  name = "${local.name_prefix}/auth0-client-secret"
}

resource "aws_secretsmanager_secret_version" "auth0_client_secret" {
  secret_id     = aws_secretsmanager_secret.auth0_client_secret.id
  secret_string = var.auth0_client_secret
}

resource "aws_secretsmanager_secret" "app_secret_key" {
  name = "${local.name_prefix}/app-secret-key"
}

resource "aws_secretsmanager_secret_version" "app_secret_key" {
  secret_id     = aws_secretsmanager_secret.app_secret_key.id
  secret_string = var.app_secret_key
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${local.name_prefix}"
  retention_in_days = 7
}

resource "aws_iam_role" "task_execution" {
  name = "${local.name_prefix}-task-execution"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "task_execution" {
  role       = aws_iam_role.task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role_policy" "read_secrets" {
  name = "${local.name_prefix}-read-secrets"
  role = aws_iam_role.task_execution.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.database_url.arn,
          aws_secretsmanager_secret.auth0_client_secret.arn,
          aws_secretsmanager_secret.app_secret_key.arn
        ]
      }
    ]
  })
}

resource "aws_lb" "app" {
  name               = "${local.name_prefix}-alb"
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = aws_subnet.public[*].id
}

resource "aws_lb_target_group" "app" {
  name        = "${local.name_prefix}-tg"
  port        = 5000
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = aws_vpc.main.id

  health_check {
    path                = "/health"
    matcher             = "200"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 3
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

resource "aws_ecs_cluster" "app" {
  name = "${local.name_prefix}-cluster"
}

resource "aws_ecs_task_definition" "app" {
  family                   = "${local.name_prefix}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = var.task_cpu
  memory                   = var.task_memory
  execution_role_arn       = aws_iam_role.task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "app"
      image     = var.image_uri
      essential = true
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
      environment = [
        { name = "AUTH0_DOMAIN", value = var.auth0_domain },
        { name = "AUTH0_CLIENT_ID", value = var.auth0_client_id },
        { name = "AUTH0_AUDIENCE", value = var.auth0_audience },
        { name = "AUTH0_CALLBACK_URL", value = "${local.service_url}/callback" },
        { name = "AUTH0_LOGOUT_RETURN_URL", value = "${local.service_url}/" },
        { name = "LOAN_REQUIRE_DATABASE_URL", value = "true" }
      ]
      secrets = [
        { name = "DATABASE_URL", valueFrom = aws_secretsmanager_secret.database_url.arn },
        { name = "AUTH0_CLIENT_SECRET", valueFrom = aws_secretsmanager_secret.auth0_client_secret.arn },
        { name = "APP_SECRET_KEY", valueFrom = aws_secretsmanager_secret.app_secret_key.arn }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "app"
        }
      }
    }
  ])
}

resource "aws_ecs_service" "app" {
  name            = "${local.name_prefix}-service"
  cluster         = aws_ecs_cluster.app.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 5000
  }

  depends_on = [
    aws_db_instance.loans,
    aws_lb_listener.http
  ]
}
