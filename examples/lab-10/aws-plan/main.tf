terraform {
  required_version = ">= 1.4, < 2.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0, < 7.0"
    }
  }
}

provider "aws" {
  region = "eu-central-1"
}

resource "aws_vpc" "lab" {
  cidr_block = "10.42.0.0/16"
  tags = {
    Name    = "incidentflow-learning"
    Project = "IncidentFlow"
  }
}
