data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-xenial-16.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  owners = ["099720109477"] # Canonical
}

resource "aws_launch_configuration" "minecraft" {
  image_id      = "${data.aws_ami.ubuntu.id}"
  instance_type = "${var.instance_type}"
  spot_price    = "${var.spot_price}"

  iam_instance_profile = "${aws_iam_instance_profile.minecraft.name}"
  security_groups = ["${aws_security_group.minecraft.id}"]

  user_data = "${data.template_cloudinit_config.config.rendered}"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "minecraft" {
  name                 = "${var.name_prefix}minecraft"
  min_size = 0
  max_size = 1

  health_check_grace_period = 300
  health_check_type         = "EC2"

  vpc_zone_identifier = ["${var.public_subnets}"]

  tags = [
    {
      key                 = "Name"
      value               = "${var.name_prefix}minecraft"
      propagate_at_launch = true
    }
  ]

  launch_configuration = "${aws_launch_configuration.minecraft.name}"
}

resource "aws_autoscaling_lifecycle_hook" "minecraft-terminate" {
  name                   = "${var.name_prefix}minecraft-terminate"
  autoscaling_group_name = "${aws_autoscaling_group.minecraft.name}"
  default_result         = "CONTINUE"
  heartbeat_timeout      = 300
  lifecycle_transition   = "autoscaling:EC2_INSTANCE_TERMINATING"
}

resource "aws_iam_instance_profile" "minecraft" {
  name  = "${var.name_prefix}minecraft"
  role = "${aws_iam_role.minecraft.name}"
}

resource "aws_iam_role" "minecraft" {
  name = "${var.name_prefix}minecraft"
  path = "/"

  assume_role_policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": "sts:AssumeRole",
          "Principal": {
            "Service": "ec2.amazonaws.com"
          },
          "Effect": "Allow",
          "Sid": ""
        }
      ]
    }
    EOF
}

resource "aws_iam_role_policy" "minecraft" {
  name = "${var.name_prefix}minecraft"
  role = "${aws_iam_role.minecraft.id}"

  policy = <<-EOF
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Action": [
            "s3:GetObject",
            "s3:PutObject",
            "s3:ListBucket"
          ],
          "Effect": "Allow",
          "Resource": [
            "${aws_s3_bucket.minecraft.arn}",
            "${aws_s3_bucket.minecraft.arn}/*"
          ]
        },
        {
          "Action": [
            "route53:ChangeResourceRecordSets",
            "route53:ListResourceRecordSets"
          ],
          "Effect": "Allow",
          "Resource": "arn:aws:route53:::hostedzone/${data.aws_route53_zone.zone.id}"
        },
        {
          "Action": [
            "autoscaling:CompleteLifecycleAction",
            "autoscaling:SetDesiredCapacity"
          ],
          "Effect": "Allow",
          "Resource": "${aws_autoscaling_group.minecraft.arn}"
        },
        {
          "Action": [
            "autoscaling:DescribeAutoScalingInstances"
          ],
          "Effect": "Allow",
          "Resource": "*"
        }
      ]
    }
    EOF
}

resource "aws_s3_bucket" "minecraft" {
  bucket = "${var.bucket_name}"

  versioning {
    enabled = true
  }

  lifecycle_rule  {
    enabled = true
    noncurrent_version_expiration {
      days = 5
    }
  }
}
