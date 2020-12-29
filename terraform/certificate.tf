provider "aws" {
  alias  = "east"
  region = "us-east-1"
}

resource "aws_acm_certificate" "webapp" {
  provider = aws.east

  domain_name       = "${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}"
  validation_method = "DNS"
}

resource "aws_route53_record" "webapp_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.webapp.domain_validation_options: dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.zone.id
}

resource "aws_acm_certificate_validation" "webapp" {
  provider = aws.east

  certificate_arn         = aws_acm_certificate.webapp.arn
  validation_record_fqdns = [for record in aws_route53_record.webapp_cert_validation: record.fqdn]
}

resource "aws_acm_certificate" "api" {
  provider = aws.east

  domain_name       = "${var.api_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}"
  validation_method = "DNS"
}

resource "aws_route53_record" "api_cert_validation" {
  for_each = {
    for dvo in aws_acm_certificate.api.domain_validation_options: dvo.domain_name => {
      name   = dvo.resource_record_name
      record = dvo.resource_record_value
      type   = dvo.resource_record_type
    }
  }
  allow_overwrite = true
  name            = each.value.name
  records         = [each.value.record]
  ttl             = 60
  type            = each.value.type
  zone_id         = data.aws_route53_zone.zone.id
}

resource "aws_acm_certificate_validation" "api" {
  provider = aws.east

  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [for record in aws_route53_record.api_cert_validation: record.fqdn]
}
