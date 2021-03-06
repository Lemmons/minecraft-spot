variable "aws_region" {
  description = "the aws region the server is running in"
}

variable "name_prefix" {
  description = "A prefix to add to resource names to ensure uniqueness and easy searchabilty"
  default     = ""
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

variable "tools_docker_image_id" {
  description = "the docker image with the tools for checking and changing status of the server"
  default     = "tlemmon/spot-tools:latest"
}

variable "docker_image" {
  description = "the minecraft-server docker image to use"
  default     = "itzg/minecraft-server:20200129"
}

variable "bucket_name" {
  description = "the name for an s3 bucket which will be created to store game data, both backups and periodic saves"
}

variable "subdomain" {
  description = "the subdomain name to run the minecraft instance at"
  default     = "minecraft"
}

variable "no_user_grace_period" {
  description = "the amount of time (in seconds) no user can be present on the server before it terminates itself"
  default     = "1800"
}

variable "backups_path" {
  description = "the path where the server will backup relative to the minecraft data path"
  default     = "backups/"
}

variable "world_path" {
  description = "the path where the minecraft world lives"
  default     = "world/"
}

variable "discord_token" {
  description = "a discord bot token server control and status messages"
  default     = ""
}

variable "discord_server" {
  description = "a discord server for the discord bot to post in"
  default     = ""
}

variable "discord_channel" {
  description = "a discord channel for the discord bot to post in"
  default     = "general"
}
