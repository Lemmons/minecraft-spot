variable "name" {}
variable "aws_region" {}
variable "rest_api_id" {}
variable "resource_id" {}
variable "resource_path" {}

variable "cors_methods" {
  type    = list(string)
  default = ["GET", "OPTIONS", "POST", "PUT"]
}

variable "cors_origins" {
  type    = list(string)
  default = ["*"]
}

variable "cors_headers" {
  type    = list(string)
  default = ["Content-Type", "X-Amz-Date", "Authorization", "X-Api-Key", "X-Amz-Security-Token"]
}

