variable "name_prefix" {
  description = "A prefix to add to resource names to ensure uniqueness and easy searchabilty"
  default     = ""
}

variable "hosted_zone_id" {
  description = "the hosted zone id your domain lives in."
}

variable "api_subdomain" {
  description = "the subdomain name to run the api at"
  default     = "api"
}

variable "webapp_subdomain" {
  description = "the subdomain name to run the web application at"
  default     = "app"
}

variable "aws_region" {
  description = "the aws region the server is running in"
}

variable "instance_type" {
  description = "the aws instance type to use for the service"
  default     = "m5.large"
}

variable "spot_price" {
  description = "the price to bid for the instance, in $/hour. If the price goes higher than this, you service will be automatically terminated. For an m5.large, 0.04 seems to work well"
  default     = "0.04"
}

variable "vpc_id" {
  description = "the vpc this service will run in"
}

variable "public_subnets" {
  type        = list(string)
  description = "a list of public subnets, which will be used to spawn the infrastructure for the service"
}

variable "bucket_name" {
  description = "the name for an s3 bucket which will be created to store game data, both backups and periodic saves"
}

variable "auth_token_issuer" {
  description = "The issuer of the auth token"
}

variable "auth_jwks_uri" {
  description = "The URL of the JWKS auth endpoint"
}

variable "auth_audience" {
  description = "The audience of the auth token.  Usually this would be the fqdn of your api, such as https://api.mysite.com"
}

variable "extra_origins" {
  description = "Extra origins to add for cors support. Useful for debugging locally, but shouldn't be needed in production"
  type        = list(string)
  default     = []
}

variable "cloudfront_location_whitelist" {
  description = "The cloudfront locations to distribute the webapp to"
  type        = list(string)
  default     = ["US", "CA", "GB", "DE"]
}

variable "cloudfront_price_class" {
  description = "The cloudfront price class to us when distributing the webapp"
  default     = "PriceClass_100"
}

variable "game_rendered_cloudconfig" {
  description = "The rendered cloudconfig for the game server"
}

variable "game_port" {
  description = "The port the game server is running on"
}
