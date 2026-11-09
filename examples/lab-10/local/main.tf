terraform {
  required_version = ">= 1.4, < 2.0"
}

variable "api_replicas" {
  type    = number
  default = 1
  validation {
    condition     = var.api_replicas >= 1 && var.api_replicas <= 3 && floor(var.api_replicas) == var.api_replicas
    error_message = "Wybierz całkowitą liczbę replik od 1 do 3."
  }
}

resource "terraform_data" "deployment_plan" {
  input = {
    project      = "incidentflow"
    environment  = "learning"
    api_replicas = var.api_replicas
  }
}

output "deployment_plan" {
  value = terraform_data.deployment_plan.output
}
