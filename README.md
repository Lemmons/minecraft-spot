# minecraft-spot
This repo contains some python code and a terraform module for the purpose of easily setting up the code and infrastructure to run minecraft using spot instances in aws.

The instance can be brought up using an api endpoint, and will automatically tear itself down after the instance is inactive (with no players online) after a certain period of time.

It requires moderate experience with [terraform](https://www.terraform.io/intro/index.html) and [AWS](https://aws.amazon.com/)

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

Once the module has been applied and you have waited a few minutes for everything to stablize, you can go to the route `https://api.<your_domain>/minecraft/start?magic_word=something-clever` to start the minecraft instance. 
The first run it might take 10-20 minutes to load, but subsiquent start should only take around 5 mins.
Once it's up and running, you can shutdown the server using `https://api.<your_domain>/minecraft/stop?magic_word=something-clever`,
or the server will shutdown on it's own after 30 mins of inactivity (no users connected to the minecraft server).

## Toubleshooting
You can ssh into your instance using your username and ssh key provided in the module config.  Depending on how far through it's start it got, you might be able to ssh to the instance using `minecraft.<your_domain>`.  If that doesn't work, you will have to get the instance's public ip address from the aws console or CLI.

## Future plans
- Proper authentication for the api page using Auth0
- An html status page for checking server status, bringing up the server, tearing it down, etc
- Backup system upgrades
    - Periodic backups (not just at shutdown time)
    - Faster shutdown
    - Support modpack version upgrades (~the current backup system doesn't allow upgrades due to it snapshotting the entire minecraft file system~
    Actually we just need to use the `REMOVE_OLD_MODS="TRUE"` env var when starting the minecraft container.  Still not sure how this should be implemented... probably some how through the api)
- Add support for vanilla minecraft
- Ensure minecraft exits when given the command to
- More restrictive iam resources for permissions
