#!/usr/bin/env bash

aws s3 sync dist/ s3://$1
aws cloudfront create-invalidation --distribution-id $2 --paths /index.html
