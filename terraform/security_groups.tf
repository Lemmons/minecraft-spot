resource "aws_security_group" "minecraft" {
  name        = "${var.name_prefix}minecraft"
  description = "Traffic into Minecraft"
  vpc_id      = var.vpc_id
}

resource "aws_security_group_rule" "minecraft" {
  type        = "ingress"
  from_port   = 25565
  to_port     = 25565
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.minecraft.id
}

resource "aws_security_group_rule" "instance-ssh-ingress" {
  type        = "ingress"
  from_port   = 22
  to_port     = 22
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.minecraft.id
}

resource "aws_security_group_rule" "instance-http-egress" {
  type        = "egress"
  from_port   = 80
  to_port     = 80
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.minecraft.id
}

resource "aws_security_group_rule" "instance-https-egress" {
  type        = "egress"
  from_port   = 443
  to_port     = 443
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.minecraft.id
}

resource "aws_security_group_rule" "instance-dns-egress-udp" {
  type        = "egress"
  from_port   = 53
  to_port     = 53
  protocol    = "udp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.minecraft.id
}

resource "aws_security_group_rule" "instance-dns-egress-tcp" {
  type        = "egress"
  from_port   = 53
  to_port     = 53
  protocol    = "tcp"
  cidr_blocks = ["0.0.0.0/0"]

  security_group_id = aws_security_group.minecraft.id
}

