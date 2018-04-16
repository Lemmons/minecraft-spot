resource "aws_api_gateway_authorizer" "authorizer" {
  name = "${var.name_prefix}authorizer"
  rest_api_id   = "${aws_api_gateway_rest_api.api.id}"
  authorizer_uri = "${aws_lambda_function.authorizer.invoke_arn}"
  authorizer_credentials = "${aws_iam_role.authorizer.arn}"

  identity_validation_expression = "^Bearer [-0-9a-zA-z\\.]*$"
  type = "TOKEN"
  identity_source = "method.request.header.Authorization"
}

resource "aws_iam_role" "authorizer" {
  name = "${var.name_prefix}authorizer"

  assume_role_policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": "sts:AssumeRole",
          "Principal": {
            "Service": "apigateway.amazonaws.com"
          },
          "Effect": "Allow",
          "Sid": ""
        }
      ]
    }
    EOF
}

resource "aws_iam_role_policy" "authorizer" {
  name = "${var.name_prefix}authorizer"
  role = "${aws_iam_role.authorizer.id}"

  policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": [
            "lambda:InvokeFunction"
          ],
          "Effect": "Allow",
          "Resource": "${aws_lambda_function.authorizer.arn}"
        }
      ]
    }
    EOF
}

resource "aws_lambda_function" "authorizer" {
  filename         = "${path.module}/custom_authorizer/custom-authorizer.zip"
  function_name    = "${var.name_prefix}jwtRsaCustomAuthorizer"
  role             = "${aws_iam_role.authorizer-lambda.arn}"
  handler          = "index.handler"
  runtime          = "nodejs4.3"
  source_code_hash = "${base64sha256(file("${path.module}/custom_authorizer/custom-authorizer.zip"))}"
  environment {
    variables = {
      TOKEN_ISSUER = "${var.auth_token_issuer}"
      JWKS_URI = "${var.auth_jwks_uri}"
      AUDIENCE = "${var.auth_audience}"
    }
  }
}

resource "aws_iam_role" "authorizer-lambda" {
  name = "${var.name_prefix}authorizer-lambda"

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

resource "aws_iam_role_policy" "authorizer-lambda" {
  name = "${var.name_prefix}authorizer-lambda"
  role = "${aws_iam_role.authorizer-lambda.id}"

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
