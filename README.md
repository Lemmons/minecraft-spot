# minecraft-spot
This repo contains some python code and a terraform module for the purpose of easily setting up the code and infrastructure to run minecraft using spot instances in aws.

The instance can be brought up using an api endpoint, and will automatically tear itself down after the instance is inactive (with no players online) after a certain period of time.

It requires moderate experiance with [terraform](https://www.terraform.io/intro/index.html) and [AWS](https://aws.amazon.com/)

Currently only supports [FTB](https://www.feed-the-beast.com/) modded versions of minecraft.

## Usage
The easiest way to get going is to add this as a terraform module in your aws terraform infrastructure.

Below is an example of what this might look like:
```
module "minecraft-spot" {
  source = "github.com/Lemmons/minecraft-spot//terraform?ref=0.1"

  username = "<your desired login username>"
  pub_ssh_key = "<your public ssh key for logging in>"

  hosted_zone_id = "<your route53 hosted zone>"
  api_subdomain= "api"
  minecraft_subdomain= "minecraft"
  domain_ssl_certificate_arn = "<an ACM cert arn in us-east-1 for the api_subdomain FQDN>"

  aws_region = "us-west-2"

  ftb_modpack_version = "https://www.feed-the-beast.com/projects/ftb-presents-direwolf20-1-12/files/2541246"

  spot_price = "0.035"
  instance_type = "m5.large"

  public_subnets = "<a list of public subnet ids in your infra>"

  bucket_name = "my-minecraft-data"
  api_passphrase = "something-clever"

  vpc_id = "<the vpc_id containing the above subnets>"
}
```

## Future plans
- Proper authentication for the api page using Auth0
- An html status page for checking server status, bringing up the server, tearing it down, etc
- Periodic backups (not just at shutdown time)
- Backup system upgrades
    - Faster shutdown
    - Use versioned s3 bucket with deletion policy for backups (rather than current timestamp based one)
    - Support modpack version upgrades (the current backup system doesn't allow upgrades due to it snapshotting the entire minecraft file system)
- Add support for vanilla minecraft
- Ensure minecraft exits when given the command to
