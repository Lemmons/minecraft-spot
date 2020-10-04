output "userdata" {
  value = data.template_cloudinit_config.config.rendered
}

output "port" {
  value = 25565
}
