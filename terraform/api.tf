data "aws_caller_identity" "current" {}

resource "aws_api_gateway_rest_api" "api" {
  name = "${var.name_prefix}minecraft-spot-api"
}

resource "aws_api_gateway_resource" "start" {
  path_part = "start"
  parent_id = "${aws_api_gateway_rest_api.api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_method" "start_get" {
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  resource_id   = "${aws_api_gateway_resource.start.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "start" {
  rest_api_id             = "${aws_api_gateway_rest_api.api.id}"
  resource_id             = "${aws_api_gateway_resource.start.id}"
  http_method             = "${aws_api_gateway_method.start_get.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.start.arn}/invocations"
}

resource "aws_lambda_permission" "start" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.start.arn}"
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.start_get.http_method}${aws_api_gateway_resource.start.path}"
}

data "archive_file" "lambda" {
  type = "zip"
  source_file = "${path.module}/lambda.py"
  output_path = "${path.module}/lambda.zip"
}

resource "aws_lambda_function" "start" {
  filename         = "${data.archive_file.lambda.output_path}"
  function_name    = "start_minecraft"
  role             = "${aws_iam_role.lambda.arn}"
  handler          = "lambda.start"
  runtime          = "python3.6"
  source_code_hash = "${base64sha256(file("${data.archive_file.lambda.output_path}"))}"
  environment {
    variables = {
      GROUP_NAME = "${aws_autoscaling_group.minecraft.name}"
      PASSPHRASE = "${var.api_passphrase}"
    }
  }
}

resource "aws_api_gateway_resource" "stop" {
  path_part = "stop"
  parent_id = "${aws_api_gateway_rest_api.api.root_resource_id}"
  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
}

resource "aws_api_gateway_method" "stop_get" {
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  resource_id   = "${aws_api_gateway_resource.stop.id}"
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "stop" {
  rest_api_id             = "${aws_api_gateway_rest_api.api.id}"
  resource_id             = "${aws_api_gateway_resource.stop.id}"
  http_method             = "${aws_api_gateway_method.stop_get.http_method}"
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.stop.arn}/invocations"
}

resource "aws_lambda_permission" "stop" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = "${aws_lambda_function.stop.arn}"
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.api.id}/*/${aws_api_gateway_method.stop_get.http_method}${aws_api_gateway_resource.stop.path}"
}

resource "aws_lambda_function" "stop" {
  filename         = "${data.archive_file.lambda.output_path}"
  function_name    = "stop_minecraft"
  role             = "${aws_iam_role.lambda.arn}"
  handler          = "lambda.stop"
  runtime          = "python3.6"
  source_code_hash = "${base64sha256(file("${data.archive_file.lambda.output_path}"))}"
  environment {
    variables = {
      GROUP_NAME = "${aws_autoscaling_group.minecraft.name}"
      PASSPHRASE = "${var.api_passphrase}"
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
  role = "${aws_iam_role.lambda.id}"

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
        }
      ]
    }
    EOF
}

data "aws_route53_zone" "zone" {
  zone_id = "${var.hosted_zone_id}"
}

resource "aws_api_gateway_domain_name" "api" {
  domain_name = "${var.api_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}"
  certificate_arn = "${var.domain_ssl_certificate_arn}"
}

resource "aws_route53_record" "api" {
  zone_id = "${var.hosted_zone_id}"
  name = "${aws_api_gateway_domain_name.api.domain_name}"
  type = "A"

  alias {
    name                   = "${aws_api_gateway_domain_name.api.cloudfront_domain_name}"
    zone_id                = "${aws_api_gateway_domain_name.api.cloudfront_zone_id}"
    evaluate_target_health = false
  }
}

resource "aws_api_gateway_base_path_mapping" "minecraft" {
  api_id      = "${aws_api_gateway_rest_api.api.id}"
  stage_name  = "${aws_api_gateway_deployment.api.stage_name}"
  domain_name = "${aws_api_gateway_domain_name.api.domain_name}"
  base_path = "minecraft"
}

resource "aws_api_gateway_deployment" "api" {
  depends_on = ["aws_api_gateway_method.start_get", "aws_api_gateway_method.stop_get"]

  rest_api_id = "${aws_api_gateway_rest_api.api.id}"
  stage_name  = "prod"
}
