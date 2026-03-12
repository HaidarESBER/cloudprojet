# ─── Azure Authentication ───────────────────────────────────────────────────
variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

# ─── General ─────────────────────────────────────────────────────────────────
variable "location" {
  description = "Azure region to deploy all resources"
  type        = string
  default     = "West Europe"
}

variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "rg-flask-app"
}

variable "project_name" {
  description = "Short project name used as prefix for all resource names"
  type        = string
  default     = "flaskapp"
}

# ─── Virtual Machine ─────────────────────────────────────────────────────────
variable "vm_size" {
  description = "Size of the Azure virtual machine"
  type        = string
  default     = "Standard_B1s"
}

variable "admin_username" {
  description = "Admin username for the virtual machine"
  type        = string
  default     = "azureuser"
}

variable "admin_password" {
  description = "Admin password for the virtual machine"
  type        = string
  sensitive   = true
}

variable "vm_os_disk_size_gb" {
  description = "OS disk size in GB"
  type        = number
  default     = 30
}

# ─── Blob Storage ─────────────────────────────────────────────────────────────
variable "storage_account_tier" {
  description = "Tier for the Storage Account (Standard or Premium)"
  type        = string
  default     = "Standard"
}

variable "storage_replication_type" {
  description = "Replication type for the Storage Account (LRS, GRS, ZRS...)"
  type        = string
  default     = "LRS"
}

variable "container_name" {
  description = "Name of the Blob Storage container for static files"
  type        = string
  default     = "static-files"
}

# ─── PostgreSQL ───────────────────────────────────────────────────────────────
variable "db_admin_username" {
  description = "Admin username for the PostgreSQL server"
  type        = string
  default     = "pgadmin"
}

variable "db_admin_password" {
  description = "Admin password for the PostgreSQL server"
  type        = string
  sensitive   = true
}

variable "db_name" {
  description = "Name of the PostgreSQL database"
  type        = string
  default     = "flaskdb"
}

variable "db_sku" {
  description = "SKU for the PostgreSQL Flexible Server"
  type        = string
  default     = "B_Standard_B1ms"
}
