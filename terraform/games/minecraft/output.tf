output "userdata" {
  value = "${data.template_cloudinit_config.config.rendered}"
}
