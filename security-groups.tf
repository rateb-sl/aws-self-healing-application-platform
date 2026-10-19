resource "aws_security_group" "alb" {
  name        = "${local.project_name}-alb"
  description = "Public entry point for CloudSentinel."
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "HTTP demo traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "ALB responses to application targets"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "app" {
  name        = "${local.project_name}-app"
  description = "Private CloudSentinel application targets."
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "ALB to application"
    from_port       = 8080
    to_port         = 8080
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  egress {
    description = "Application outbound package and AWS API access"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "rds" {
  name        = "${local.project_name}-rds"
  description = "Database access from the CloudSentinel application tier only."
  vpc_id      = aws_vpc.main.id

  ingress {
    description     = "Application to MySQL"
    from_port       = 3306
    to_port         = 3306
    protocol        = "tcp"
    security_groups = [aws_security_group.app.id]
  }
}
