# Rapport de Déploiement — Terraform Flask Azure

---

## Étape 1 — Initialisation de Terraform

**Commande :** `terraform init`
**Statut :** ✅ Succès

```
Initializing the backend...
Initializing provider plugins...
- Finding hashicorp/azurerm versions matching "~> 3.90"...
- Installing hashicorp/azurerm v3.117.1...
- Installing hashicorp/random v3.8.1...

Terraform has been successfully initialized!
```

---

## Étape 2 — Plan Terraform

**Commande :** `terraform plan`
**Statut :** ❌ Erreur

```
Error: unable to build authorizer for Resource Manager API:
could not configure AzureCli Authorizer:
could not parse Azure CLI version:
launching Azure CLI: exec: "az": executable file not found in %PATH%
```

**Cause :** Azure CLI installé mais PATH non mis à jour dans le terminal actuel.

**Solution :** Ouvrir un nouveau terminal PowerShell, lancer `az login`, puis relancer `terraform plan`.

---

## Étape 3 — Terraform Plan (succès)

**Commande :** `terraform plan`
**Statut :** ✅ Succès — 16 ressources à créer

| Ressource | Nom Azure | Description |
|---|---|---|
| `azurerm_resource_group` | `rg-flask-app` | Groupe de ressources |
| `azurerm_virtual_network` | `flaskapp-vnet` | Réseau virtuel 10.0.0.0/16 |
| `azurerm_subnet` (VM) | `flaskapp-subnet-vm` | Sous-réseau VM 10.0.1.0/24 |
| `azurerm_subnet` (DB) | `flaskapp-subnet-db` | Sous-réseau PostgreSQL 10.0.2.0/24 |
| `azurerm_public_ip` | `flaskapp-public-ip` | IP publique statique Standard |
| `azurerm_network_security_group` | `flaskapp-nsg` | Règles SSH (22), HTTP (80), Flask (5000) |
| `azurerm_network_interface` | `flaskapp-nic` | Interface réseau de la VM |
| `azurerm_network_interface_security_group_association` | — | Association NIC ↔ NSG |
| `azurerm_linux_virtual_machine` | `flaskapp-vm` | Ubuntu 22.04, Standard_B2s_v2 |
| `azurerm_storage_account` | `flaskappstorage<random>` | Compte de stockage Standard LRS |
| `azurerm_storage_container` | `static-files` | Conteneur Blob privé |
| `azurerm_private_dns_zone` | `flaskapp.postgres.database.azure.com` | Zone DNS privée PostgreSQL |
| `azurerm_private_dns_zone_virtual_network_link` | `flaskapp-dns-link` | Lien DNS ↔ VNet |
| `azurerm_postgresql_flexible_server` | `flaskapp-postgres` | PostgreSQL 15, B_Standard_B1ms |
| `azurerm_postgresql_flexible_server_database` | `flaskdb` | Base de données UTF8 |
| `random_string.suffix` | — | Suffixe aléatoire pour le nom du storage |

---

## Étape 4 — Terraform Apply (1ère tentative)

**Statut :** ❌ Erreur — Région non autorisée

```
Error: RequestDisallowedByAzure
Resource 'flaskapp-vnet' was disallowed by Azure
Resource 'flaskapp-public-ip' was disallowed by Azure
```

**Cause :** La région West Europe n'est pas autorisée par la politique EFREI (compte Azure Étudiant).

**Solution :** Utiliser `francecentral` (région autorisée par l'EFREI).

---

## Étape 5 — Corrections et Apply final

- [x] Région changée : `francecentral`
- [x] Bug PostgreSQL corrigé : `public_network_access_enabled = false`
- [x] Bug zone PostgreSQL : `lifecycle { ignore_changes = [zone] }`
- [x] VM size : `Standard_B2s_v2` zone 2 (seule SKU disponible)
- [x] State drift résolu via `terraform import` (VNet, Storage, NIC)

### Outputs

| Output | Valeur |
|---|---|
| `vm_public_ip` | `4.233.118.182` |
| `flask_app_url` | `http://4.233.118.182:5000` |
| `storage_account_name` | `flaskappstorage61atxp` |
| `postgres_fqdn` | `flaskapp-postgres.postgres.database.azure.com` |
| `resource_group_name` | `rg-flask-app` |

---

## Étape 6 — Tests CRUD ✅

| Test | Résultat |
|---|---|
| GET /health | `{"status": "ok"}` |
| POST /files | Upload Blob + métadonnées PostgreSQL ✅ |
| GET /files | Liste retournée ✅ |
| PUT /files/<id> | Description mise à jour ✅ |
| DELETE /files/<id> | Suppression Blob + PostgreSQL ✅ |

---

## Étape 7 — Destruction de l'infrastructure

- [ ] `terraform destroy`
