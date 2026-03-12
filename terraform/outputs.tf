# ─── VM ───────────────────────────────────────────────────────────────────────
output "vm_public_ip" {
  description = "Public IP address of the virtual machine"
  value       = azurerm_public_ip.vm.ip_address
}

output "vm_ssh_command" {
  description = "SSH command to connect to the VM"
  value       = "ssh ${var.admin_username}@${azurerm_public_ip.vm.ip_address}"
}

output "flask_app_url" {
  description = "URL to access the Flask application"
  value       = "http://${azurerm_public_ip.vm.ip_address}:5000"
}

# ─── Storage ──────────────────────────────────────────────────────────────────
output "storage_account_name" {
  description = "Name of the Azure Storage Account"
  value       = azurerm_storage_account.main.name
}

output "storage_container_name" {
  description = "Name of the Blob Storage container"
  value       = azurerm_storage_container.static.name
}

output "storage_primary_endpoint" {
  description = "Primary blob endpoint URL"
  value       = azurerm_storage_account.main.primary_blob_endpoint
}

# ─── Database ─────────────────────────────────────────────────────────────────
output "postgres_fqdn" {
  description = "Fully Qualified Domain Name of the PostgreSQL server"
  value       = azurerm_postgresql_flexible_server.main.fqdn
}

output "postgres_connection_string" {
  description = "PostgreSQL connection string (sensitive)"
  value       = "postgresql://${var.db_admin_username}:${var.db_admin_password}@${azurerm_postgresql_flexible_server.main.fqdn}:5432/${var.db_name}"
  sensitive   = true
}

# ─── Resource Group ───────────────────────────────────────────────────────────
output "resource_group_name" {
  description = "Name of the resource group"
  value       = azurerm_resource_group.main.name
}
