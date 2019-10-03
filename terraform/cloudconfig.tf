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

data "template_file" "minecraft" {
  template = <<-EOF
    #cloud-config
    packages:
      - python3-pip
    runcmd:
      - mkdir -p /srv/minecraft-spot/data
      - pip3 install awscli
      - aws configure set region ${var.aws_region}
      - docker run --name set_route -e AWS_DEFAULT_REGION=${var.aws_region} -e FQDN=${var.minecraft_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")} -e ZONE_ID=${var.hosted_zone_id} ${var.tools_docker_image_id} set_route.py
      - docker run --name restore_backup -e AWS_DEFAULT_REGION=${var.aws_region} -e S3_BUCKET=${var.bucket_name} -v /srv/minecraft-spot/data:/data ${var.tools_docker_image_id} restore_backup.py
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
              container_name: minecraft
              image: ${var.minecraft_docker_image_id}
              restart: on-failure
              ports:
                - 25565:25565
              volumes:
                - /srv/minecraft-spot/data:/data
              environment:
                EULA: "TRUE"
                MAX_RAM: "7G"
                TYPE: "FTB"
                FTB_SERVER_MOD: "${var.ftb_modpack_version}"
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
                BACKUP_COMMAND: "${var.ftb_backup_command}"
                BACKUP_INDEX_PATH: ${var.ftb_backup_index_path}
                BACKUPS_PATH: ${var.ftb_backups_path}
            check_players:
              container_name: check_players
              image: ${var.tools_docker_image_id}
              command: check_players.py
              restart: on-failure
              volumes:
                - /var/run/docker.sock:/var/run/docker.sock
              environment:
                AWS_DEFAULT_REGION: ${var.aws_region}
                GRACE_PERIOD: "${var.no_user_grace_period}"
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

