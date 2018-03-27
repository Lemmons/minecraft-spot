# minecraft-spot

This repo contains some python code and a terraform module for the purpose of easily setting up the code and infrastructure to run minecraft using spot instances in aws.

The instance can be brought up using an api endpoint, and will automatically tear itself down after the instance is inactive (with no players online) after a certain period of time.
