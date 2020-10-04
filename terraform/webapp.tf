resource "aws_s3_bucket" "webapp" {
  bucket = "${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}"
  policy = data.aws_iam_policy_document.webapp.json
}

data "aws_iam_policy_document" "webapp" {
  statement {
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      "arn:aws:s3:::${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}",
      "arn:aws:s3:::${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}/*",
    ]

    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.webapp.iam_arn]
    }
  }
}

resource "aws_cloudfront_distribution" "webapp" {
  origin {
    domain_name = aws_s3_bucket.webapp.bucket_domain_name
    origin_id   = "${var.name_prefix}minecraft-spot-origin"
    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.webapp.cloudfront_access_identity_path
    }
  }

  enabled             = true
  default_root_object = "index.html"
  is_ipv6_enabled     = true
  aliases             = ["${var.webapp_subdomain}.${replace(data.aws_route53_zone.zone.name, "/[.]$/", "")}"]

  price_class = var.cloudfront_price_class

  default_cache_behavior {
    allowed_methods  = ["GET", "HEAD", "OPTIONS"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "${var.name_prefix}minecraft-spot-origin"

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 3600
    max_ttl                = 86400
  }

  restrictions {
    geo_restriction {
      restriction_type = "whitelist"
      locations        = var.cloudfront_location_whitelist
    }
  }

  custom_error_response {
    error_code            = "404"
    error_caching_min_ttl = "0"
    response_code         = "200"
    response_page_path    = "/index.html"
  }

  viewer_certificate {
    acm_certificate_arn      = aws_acm_certificate.webapp.arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.1_2016"
  }
}

resource "aws_cloudfront_origin_access_identity" "webapp" {
  comment = "${var.name_prefix}minecraft-spot-origin-access-identity"
}

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
  name    = aws_acm_certificate.webapp.domain_validation_options[0].resource_record_name
  type    = aws_acm_certificate.webapp.domain_validation_options[0].resource_record_type
  zone_id = data.aws_route53_zone.zone.id
  records = [aws_acm_certificate.webapp.domain_validation_options[0].resource_record_value]
  ttl     = 60
}

resource "aws_acm_certificate_validation" "webapp" {
  provider = aws.east

  certificate_arn         = aws_acm_certificate.webapp.arn
  validation_record_fqdns = [aws_route53_record.webapp_cert_validation.fqdn]
}

resource "aws_route53_record" "webapp" {
  name    = var.webapp_subdomain
  zone_id = data.aws_route53_zone.zone.id
  type    = "A"

  alias {
    name                   = aws_cloudfront_distribution.webapp.domain_name
    zone_id                = aws_cloudfront_distribution.webapp.hosted_zone_id
    evaluate_target_health = true
  }
}

output "webapp-distribution-id" {
  value = aws_cloudfront_distribution.webapp.id
}
