variable "name_prefix" {
  description = "A prefix to add to resource names to ensure uniqueness and easy searchabilty"
  default = ""
}

variable "username" {
  description = "a username to use for sshing into running machines"
}

variable "pub_ssh_key" {
  description = "a public ssh key associated with the user for sshing into running machines"
}

variable "hosted_zone_id" {
  description = "the hosted zone id your domain lives in."
}

variable "api_subdomain" {
  description = "the subdomain name to run the api at"
  default = "api"
}

variable "minecraft_subdomain" {
  description = "the subdomain name to run the minecraft instance at"
  default = "minecraft"
}

variable "domain_ssl_certificate_arn" {
  description = "the api domain's ssl cerficate arn. This MUST match the api name and be created in the us-east-1 (N. Virginia) zone"
}

variable "tools_docker_image_id" {
  description = "the docker image with the tools for checking and changing status of the server"
  default = "tlemmon/minecraft-spot-tools:0.6"
}

variable "aws_region" {
  description = "the aws region the server is running in"
}

variable "ftb_modpack_version" {
  description = "the ftb modpack version to use, like: https://www.feed-the-beast.com/projects/ftb-presents-direwolf20-1-12/files/2541246"
}

variable "instance_type" {
  description = "the aws instance type to use for the service"
  default = "m5.large"
}

variable "spot_price" {
  description = "the price to bid for the instance, in $/hour. If the price goes higher than this, you service will be automatically terminated. For an m5.large, 0.04 seems to work well"
  default = "0.04"
}

variable "public_subnets" {
  type = "list"
  description = "a list of public subnets, which will be used to spawn the infrastructure for the service"
}

variable "vpc_id" {
  description = "the vpc this service will run in"
}

variable "bucket_name" {
  description = "the name for an s3 bucket which will be created to store game data, both backups and periodic saves"
}

variable "no_user_grace_period" {
  description = "the amount of time (in seconds) no user can be present on the server before it terminates itself"
  default = "1800"
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
