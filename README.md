# Déploiement Infrastructure Azure avec Terraform

Application Flask déployée sur Azure via Terraform, avec stockage de fichiers sur Azure Blob Storage et métadonnées dans PostgreSQL.

## Architecture

```
Internet
    │
    ▼
[Azure Public IP]
    │
    ▼
[VM Ubuntu 22.04]
  ├── Nginx (port 80)  →  reverse proxy
  └── Gunicorn / Flask (port 5000)
            │                   │
            ▼                   ▼
  [Azure PostgreSQL]    [Azure Blob Storage]
  (métadonnées)         (fichiers binaires)
```

## Ressources créées (16 au total)

| Ressource | Nom | Description |
|---|---|---|
| Resource Group | `rg-flask-app` | Conteneur de toutes les ressources |
| Virtual Network | `flaskapp-vnet` | Réseau `10.0.0.0/16` |
| Subnet VM | `flaskapp-subnet-vm` | `10.0.1.0/24` |
| Subnet DB | `flaskapp-subnet-db` | `10.0.2.0/24` |
| Public IP | `flaskapp-public-ip` | IP statique Standard |
| NSG | `flaskapp-nsg` | Ports 22, 80, 5000 |
| Network Interface | `flaskapp-nic` | NIC de la VM |
| Linux VM | `flaskapp-vm` | Ubuntu 22.04, Standard_B2s_v2, zone 2 |
| Storage Account | `flaskappstorage<suffix>` | Standard LRS |
| Storage Container | `static-files` | Accès privé |
| Private DNS Zone | `flaskapp.postgres.database.azure.com` | DNS privé PostgreSQL |
| DNS VNet Link | `flaskapp-dns-link` | Lien DNS ↔ VNet |
| PostgreSQL Server | `flaskapp-postgres` | Flexible Server v15, B_Standard_B1ms |
| PostgreSQL DB | `flaskdb` | UTF8 |
| NIC/NSG Association | — | Association NIC ↔ NSG |
| Random Suffix | — | Suffixe unique pour le storage |

## Prérequis

- [Terraform](https://developer.hashicorp.com/terraform/install) 1.3+
- [Azure CLI](https://learn.microsoft.com/fr-fr/cli/azure/install-azure-cli) 2.50+

## Déploiement

### 1. Connexion Azure

```bash
az login
az account show
```

### 2. Configurer les variables

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
# éditer terraform.tfvars avec votre subscription_id, mots de passe, etc.
```

### 3. Déployer

```bash
terraform init
terraform plan
terraform apply
```

### 4. Récupérer les outputs

```bash
terraform output vm_public_ip
terraform output flask_app_url
```

## API — Endpoints

| Méthode | Route | Description |
|---|---|---|
| GET | `/health` | Statut de l'application |
| POST | `/files` | Upload d'un fichier (multipart) |
| GET | `/files` | Liste tous les fichiers |
| PUT | `/files/<id>` | Modifie la description |
| DELETE | `/files/<id>` | Supprime le fichier (Blob + DB) |

### Exemples curl

```bash
# Health check
curl http://<IP>/health

# Upload
curl -X POST http://<IP>/files -F "file=@test.txt" -F "description=Mon fichier"

# Liste
curl http://<IP>/files

# Mise à jour
curl -X PUT http://<IP>/files/<id> -H "Content-Type: application/json" -d '{"description": "Nouvelle description"}'

# Suppression
curl -X DELETE http://<IP>/files/<id>
```

## Structure du projet

```
terraform-flask-azure/
├── terraform/
│   ├── provider.tf              # Provider Azure (auth via az login)
│   ├── main.tf                  # 16 ressources Azure
│   ├── variables.tf             # Déclaration des variables
│   ├── outputs.tf               # IP publique, URLs, FQDN
│   ├── terraform.tfvars.example # Template de configuration
│   └── scripts/
│       └── cloud-init.yaml      # Provisioning automatique de la VM
├── backend/
│   ├── app.py                   # Flask CRUD + Azure Blob Storage
│   ├── requirements.txt
│   └── .env.example
├── rapport/
│   └── etapes.md                # Journal de déploiement
├── .gitignore
└── README.md
```

## Sécurité

- `terraform.tfvars` et `*.tfstate` exclus du dépôt Git
- Blob Storage en accès **privé** (pas d'URL publique anonyme)
- PostgreSQL accessible uniquement via réseau privé (`public_network_access_enabled = false`)
- NSG restreint aux ports 22 (SSH), 80 (HTTP), 5000 (Flask)

## Destruction

```bash
terraform destroy
```
