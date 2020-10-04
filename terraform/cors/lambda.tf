data "aws_caller_identity" "current" {
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "${path.module}/../lambda.py"
  output_path = "${path.module}/../lambda.zip"
}

resource "aws_lambda_permission" "lambda" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.arn
  principal     = "apigateway.amazonaws.com"

  source_arn = "arn:aws:execute-api:${var.aws_region}:${data.aws_caller_identity.current.account_id}:${var.rest_api_id}/*/${aws_api_gateway_method.options.http_method}${var.resource_path}"
}

resource "aws_lambda_function" "lambda" {
  filename         = data.archive_file.lambda.output_path
  function_name    = "${var.name}-cors-response"
  role             = aws_iam_role.lambda.arn
  handler          = "lambda.cors"
  runtime          = "python3.6"
  source_code_hash = filebase64sha256(data.archive_file.lambda.output_path)
  environment {
    variables = {
      CORS_HEADERS = join(",", var.cors_headers)
      CORS_METHODS = join(",", var.cors_methods)
      CORS_ORIGINS = join(",", var.cors_origins)
    }
  }
}

resource "aws_iam_role" "lambda" {
  name = "${var.name}-lambda"

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
  name = "${var.name}-lambda"
  role = aws_iam_role.lambda.id

  policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
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
