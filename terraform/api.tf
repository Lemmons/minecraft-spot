data "aws_caller_identity" "current" {
}

resource "aws_api_gateway_rest_api" "api" {
  name = "${var.name_prefix}minecraft-spot-api"
}

resource "aws_api_gateway_resource" "start" {
  path_part   = "start"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

module "start-cors" {
  source = "./cors"

  name       = "${var.name_prefix}start"
  aws_region = var.aws_region

  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.start.id
  resource_path = aws_api_gateway_resource.start.path
  cors_origins = concat(
    var.extra_origins,
    [
      "https://${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}",
    ],
  )
}

resource "aws_api_gateway_method" "start_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.start.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.authorizer.id
}

resource "aws_api_gateway_integration" "start" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.start.id
  http_method             = aws_api_gateway_method.start_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.start.invoke_arn
}

resource "aws_lambda_permission" "start" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.start.arn
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.start_get.http_method}${aws_api_gateway_resource.start.path}"
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/lambda.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "start" {
  filename         = data.archive_file.lambda.output_path
  function_name    = "${var.name_prefix}start_minecraft"
  role             = aws_iam_role.lambda.arn
  handler          = "lambda.start"
  runtime          = "python3.6"
  source_code_hash = filebase64sha256(data.archive_file.lambda.output_path)
  environment {
    variables = {
      GROUP_NAME = aws_autoscaling_group.minecraft.name
      CORS_ORIGINS = join(
        ",",
        concat(
          var.extra_origins,
          [
            "https://${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}",
          ],
        ),
      )
    }
  }
}

resource "aws_api_gateway_resource" "stop" {
  path_part   = "stop"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

module "stop-cors" {
  source = "./cors"

  name       = "${var.name_prefix}stop"
  aws_region = var.aws_region

  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.stop.id
  resource_path = aws_api_gateway_resource.stop.path
  cors_origins = concat(
    var.extra_origins,
    [
      "https://${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}",
    ],
  )
}

resource "aws_api_gateway_method" "stop_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.stop.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.authorizer.id
}

resource "aws_api_gateway_integration" "stop" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.stop.id
  http_method             = aws_api_gateway_method.stop_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.stop.invoke_arn
}

resource "aws_lambda_permission" "stop" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.stop.arn
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.stop_get.http_method}${aws_api_gateway_resource.stop.path}"
}

resource "aws_lambda_function" "stop" {
  filename         = data.archive_file.lambda.output_path
  function_name    = "${var.name_prefix}stop_minecraft"
  role             = aws_iam_role.lambda.arn
  handler          = "lambda.stop"
  runtime          = "python3.6"
  source_code_hash = filebase64sha256(data.archive_file.lambda.output_path)
  environment {
    variables = {
      GROUP_NAME = aws_autoscaling_group.minecraft.name
      CORS_ORIGINS = join(
        ",",
        concat(
          var.extra_origins,
          [
            "https://${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}",
          ],
        ),
      )
    }
  }
}

resource "aws_api_gateway_resource" "status" {
  path_part   = "status"
  parent_id   = aws_api_gateway_rest_api.api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.api.id
}

module "status-cors" {
  source = "./cors"

  name       = "${var.name_prefix}status"
  aws_region = var.aws_region

  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.status.id
  resource_path = aws_api_gateway_resource.status.path
  cors_origins = concat(
    var.extra_origins,
    [
      "https://${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}",
    ],
  )
}

resource "aws_api_gateway_method" "status_get" {
  rest_api_id   = aws_api_gateway_rest_api.api.id
  resource_id   = aws_api_gateway_resource.status.id
  http_method   = "GET"
  authorization = "CUSTOM"
  authorizer_id = aws_api_gateway_authorizer.authorizer.id
}

resource "aws_api_gateway_integration" "status" {
  rest_api_id             = aws_api_gateway_rest_api.api.id
  resource_id             = aws_api_gateway_resource.status.id
  http_method             = aws_api_gateway_method.status_get.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.status.invoke_arn
}

resource "aws_lambda_permission" "status" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.status.arn
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.status_get.http_method}${aws_api_gateway_resource.status.path}"
}

resource "aws_lambda_function" "status" {
  filename         = data.archive_file.lambda.output_path
  function_name    = "${var.name_prefix}status_minecraft"
  role             = aws_iam_role.lambda.arn
  handler          = "lambda.status"
  runtime          = "python3.6"
  source_code_hash = filebase64sha256(data.archive_file.lambda.output_path)
  environment {
    variables = {
      GROUP_NAME = aws_autoscaling_group.minecraft.name
      CORS_ORIGINS = join(
        ",",
        concat(
          var.extra_origins,
          [
            "https://${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}",
          ],
        ),
      )
    }
  }
}

resource "aws_iam_role" "lambda" {
  name = "${var.name_prefix}lambda"

  assume_role_policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": "sts:AssumeRole",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Effect": "Allow",
          "Sid": ""
        }
      ]
    }
EOF

}

resource "aws_iam_role_policy" "lambda" {
  name = "${var.name_prefix}lambda"
  role = aws_iam_role.lambda.id

  policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": [
            "autoscaling:SetDesiredCapacity"
          ],
          "Effect": "Allow",
          "Resource": "${aws_autoscaling_group.minecraft.arn}"
        },
        {
          "Action": [
            "autoscaling:DescribeAutoScalingGroups"
          ],
          "Effect": "Allow",
          "Resource": "*"
        },
        {
          "Effect": "Allow",
          "Action": [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
          ],
          "Resource": "*"
        }
      ]
    }
EOF

}

data "aws_route53_zone" "zone" {
  zone_id = var.hosted_zone_id
}

resource "aws_api_gateway_domain_name" "api" {
  domain_name     = "${var.api_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}"
  certificate_arn = aws_acm_certificate.api.arn
}

resource "aws_route53_record" "api" {
  zone_id = var.hosted_zone_id
  name    = aws_api_gateway_domain_name.api.domain_name
  type    = "A"

  alias {
    name                   = aws_api_gateway_domain_name.api.cloudfront_domain_name
    zone_id                = aws_api_gateway_domain_name.api.cloudfront_zone_id
    evaluate_target_health = false
  }
}

resource "aws_api_gateway_base_path_mapping" "minecraft" {
  api_id      = aws_api_gateway_rest_api.api.id
  stage_name  = aws_api_gateway_deployment.api.stage_name
  domain_name = aws_api_gateway_domain_name.api.domain_name
  base_path   = "minecraft"
}

resource "aws_api_gateway_deployment" "api" {
  depends_on = [
    aws_api_gateway_integration.start,
    aws_api_gateway_integration.stop,
    aws_api_gateway_integration.status,
  ]

  rest_api_id = aws_api_gateway_rest_api.api.id
  stage_name  = "prod"

  variables = {
    version = "0.5"
  }

  lifecycle {
    create_before_destroy = true
  }
}
