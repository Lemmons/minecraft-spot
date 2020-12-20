data "aws_route53_zone" "zone" {
  zone_id = var.hosted_zone_id
}

data "template_cloudinit_config" "config" {
  gzip          = true
  base64_encode = true

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.users.rendered
    merge_type   = "list(append)+dict(recurse_array)+str()"
  }

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.docker.rendered
    merge_type   = "list(append)+dict(recurse_array)+str()"
  }

  part {
    content_type = "text/cloud-config"
    content      = data.template_file.minecraft.rendered
    merge_type   = "list(append)+dict(recurse_array)+str()"
  }
}

locals {
  game = "minecraft"
}

data "template_file" "minecraft" {
  template = <<-EOF
    #cloud-config
    packages:
      - python3-pip
    runcmd:
      - mkdir -p /srv/minecraft-spot/data
      - pip3 install awscli
      - aws configure set region ${var.aws_region}
      - docker run --name set_route -e AWS_DEFAULT_REGION=${var.aws_region} -e FQDN=${var.subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")} -e ZONE_ID=${var.hosted_zone_id} -e GAME=${local.game} -e BACKUPS_PATH=${var.backups_path} ${var.tools_docker_image_id} set_route.py
      - docker run --name restore_backup -e AWS_DEFAULT_REGION=${var.aws_region} -e S3_BUCKET=${var.bucket_name} -e GAME=${local.game} -e BACKUPS_PATH=${var.backups_path} -v /srv/minecraft-spot/data:/data ${var.tools_docker_image_id} restore_backup.py
      - chmod -R a+rwX /srv/minecraft-spot/data
      - docker-compose -f /srv/minecraft-spot/docker-compose.yaml up -d
    write_files:
      - path: /srv/minecraft-spot/docker-compose.yaml
        permissions: "0644"
        owner: root
        content: |
          version: "3"
          services:
            minecraft:
              container_name: ${local.game}
              image: ${var.docker_image}
              restart: on-failure
              ports:
                - 25565:25565
              volumes:
                - /srv/minecraft-spot/data:/data
              environment:
                EULA: "TRUE"
                MAX_MEMORY: "7G"
                TYPE: "${var.modpack_type}"
                ${var.modpack_type == "FTB" ? "FTB_SERVER_MOD" : "CF_SERVER_MOD"}: "${var.modpack_version}"
            check_termination:
              container_name: check_termination
              image: ${var.tools_docker_image_id}
              command: check_termination.py
              restart: on-failure
              volumes:
                - /srv/minecraft-spot/data:/data
                - /var/run/docker.sock:/var/run/docker.sock
              environment:
                AWS_DEFAULT_REGION: ${var.aws_region}
                S3_BUCKET: ${var.bucket_name}
                LIFECYCLE_HOOK_NAME: "${var.name_prefix}minecraft-terminate"
                BACKUP_COMMAND: "${var.backup_command}"
                BACKUP_INDEX_PATH: ${var.backup_index_path}
                BACKUPS_PATH: ${var.backups_path}
                GAME: "${local.game}"
            check_players:
              container_name: check_players
              image: ${var.tools_docker_image_id}
              command: check_players.py
              restart: on-failure
              volumes:
                - /var/run/docker.sock:/var/run/docker.sock
              environment:
                AWS_DEFAULT_REGION: ${var.aws_region}
                S3_BUCKET: ${var.bucket_name}
                LIFECYCLE_HOOK_NAME: "${var.name_prefix}minecraft-terminate"
                BACKUP_COMMAND: "${var.backup_command}"
                BACKUP_INDEX_PATH: ${var.backup_index_path}
                BACKUPS_PATH: ${var.backups_path}
                GRACE_PERIOD: "${var.no_user_grace_period}"
                GAME: "${local.game}"
            discord_bot:
              container_name: discord_bot
              image: ${var.tools_docker_image_id}
              command: discord_bot.py
              restart: on-failure
              volumes:
                - /srv/factorio-spot/data:/data
                - /var/run/docker.sock:/var/run/docker.sock
              environment:
                AWS_DEFAULT_REGION: ${var.aws_region}
                S3_BUCKET: ${var.bucket_name}
                LIFECYCLE_HOOK_NAME: "${var.name_prefix}minecraft-terminate"
                BACKUPS_PATH: ${var.backups_path}
                WORLD_PATH: ${var.world_path}
                GRACE_PERIOD: "${var.no_user_grace_period}"
                GAME: "${local.game}"
                FQDN: "${var.subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}"
                DISCORD_TOKEN: "${var.discord_token}"
                DISCORD_CHANNEL: "${var.discord_channel}"
                DISCORD_SERVER: "${var.discord_server}"
EOF

}

data "template_file" "users" {
  template = <<-EOF
    #cloud-config
    users:
      - default
      - name: ${var.username}
        groups: docker,wheel
        shell: /bin/bash
        sudo: ALL=(ALL) NOPASSWD:ALL
        lock_passwd: true
        ssh-import-id: None
        ssh-authorized_keys:
          - ${var.pub_ssh_key}
EOF

}

data "template_file" "docker" {
  template = <<-EOF
    #cloud-config
    packages:
      - apt-transport-https
      - ca-certificates
      - curl
    runcmd:
      - curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
      - add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu xenial stable"
      - apt-get update -y
      - apt-get install -y docker-ce
      - curl -L https://github.com/docker/compose/releases/download/1.17.0/docker-compose-linux-x86_64 > /usr/bin/docker-compose
      - chmod +x /usr/bin/docker-compose
EOF

}

