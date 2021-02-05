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
  name    = tolist(aws_acm_certificate.webapp.domain_validation_options)[0].resource_record_name
  type    = tolist(aws_acm_certificate.webapp.domain_validation_options)[0].resource_record_type
  zone_id = data.aws_route53_zone.zone.id
  records = [tolist(aws_acm_certificate.webapp.domain_validation_options)[0].resource_record_value]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "webapp" {
  provider = aws.east

  certificate_arn         = aws_acm_certificate.webapp.arn
  validation_record_fqdns = [aws_route53_record.webapp_cert_validation.fqdn]
}

resource "aws_acm_certificate" "api" {
  provider = aws.east

  domain_name       = "${var.api_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}"
  validation_method = "DNS"
}

resource "aws_route53_record" "api_cert_validation" {
  name    = tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_name
  type    = tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_type
  zone_id = data.aws_route53_zone.zone.id
  records = [tolist(aws_acm_certificate.api.domain_validation_options)[0].resource_record_value]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "api" {
  provider = aws.east

  certificate_arn         = aws_acm_certificate.api.arn
  validation_record_fqdns = [aws_route53_record.api_cert_validation.fqdn]
}
