# Déploiement Automatisé d'Infrastructure Azure avec Terraform

Application Flask déployée sur Azure avec :
- **Azure VM** (Ubuntu 22.04) — héberge l'application Flask via Gunicorn + Nginx
- **Azure Blob Storage** — stockage des fichiers statiques (images, logs, etc.)
- **Azure PostgreSQL Flexible Server** — base de données relationnelle
- **API CRUD** — gestion des fichiers et de leurs métadonnées

---

## Architecture

```
Internet
    │
    ▼
[Azure Public IP]
    │
    ▼
[VM Ubuntu 22.04]
  ├── Nginx (port 80) → reverse proxy
  └── Gunicorn / Flask (port 5000)
          │                   │
          ▼                   ▼
  [Azure PostgreSQL]   [Azure Blob Storage]
  (métadonnées)        (fichiers binaires)
```

---

## Prérequis

| Outil        | Version minimale | Installation |
|--------------|-----------------|--------------|
| Terraform    | 1.3+            | https://developer.hashicorp.com/terraform/install |
| Azure CLI    | 2.50+           | https://learn.microsoft.com/fr-fr/cli/azure/install-azure-cli |
| Python       | 3.10+           | https://www.python.org/ |

---

## Étape 1 — Configurer Azure

### 1.1 Connexion à Azure CLI

```bash
az login
az account show   # vérifier la subscription active
```

### 1.2 Créer un Service Principal Terraform

```bash
az ad sp create-for-rbac \
  --name "terraform-flask" \
  --role Contributor \
  --scopes /subscriptions/<SUBSCRIPTION_ID>
```

Résultat :
```json
{
  "appId":       "client_id",
  "password":    "client_secret",
  "tenant":      "tenant_id"
}
```

---

## Étape 2 — Configurer Terraform

### 2.1 Créer le fichier de variables

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
```

Éditer `terraform.tfvars` et renseigner toutes les valeurs.

### 2.2 Initialiser Terraform

```bash
terraform init
```

### 2.3 Vérifier le plan d'exécution

```bash
terraform plan
```

### 2.4 Déployer l'infrastructure

```bash
terraform apply
```

Taper `yes` pour confirmer. Le déploiement prend ~10 minutes.

### 2.5 Récupérer les outputs

```bash
terraform output vm_public_ip
terraform output flask_app_url
terraform output storage_account_name
```

---

## Étape 3 — Tester l'application

### Health check

```bash
curl http://<VM_PUBLIC_IP>/health
```

### Upload d'un fichier (CREATE)

```bash
curl -X POST http://<VM_PUBLIC_IP>/files \
  -F "file=@mon_image.png" \
  -F "description=Logo du projet"
```

### Lister les fichiers (READ)

```bash
curl http://<VM_PUBLIC_IP>/files
```

### Obtenir un fichier par ID (READ)

```bash
curl http://<VM_PUBLIC_IP>/files/<file_id>
```

### Modifier la description (UPDATE)

```bash
curl -X PUT http://<VM_PUBLIC_IP>/files/<file_id> \
  -H "Content-Type: application/json" \
  -d '{"description": "Nouvelle description"}'
```

### Supprimer un fichier (DELETE)

```bash
curl -X DELETE http://<VM_PUBLIC_IP>/files/<file_id>
```

---

## Développement local

```bash
cd backend/
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

pip install -r requirements.txt
cp .env.example .env            # configurer les variables
python app.py
```

L'application est accessible sur `http://localhost:5000`.

---

## Étape 4 — Détruire l'infrastructure

```bash
cd terraform/
terraform destroy
```

> **Attention** : cette commande supprime toutes les ressources Azure créées, y compris les données en base et dans le Blob Storage.

---

## Structure du projet

```
terraform-flask-azure/
├── terraform/
│   ├── provider.tf          # Configuration du provider Azure
│   ├── main.tf              # Ressources principales (VM, Storage, DB, Réseau)
│   ├── variables.tf         # Déclaration des variables
│   ├── outputs.tf           # Sorties (IP publique, URLs, etc.)
│   ├── terraform.tfvars.example
│   └── scripts/
│       └── cloud-init.yaml  # Provisioning automatique de la VM
├── backend/
│   ├── app.py               # Application Flask (CRUD + Azure Blob)
│   ├── requirements.txt
│   └── .env.example
├── .gitignore
└── README.md
```

---

## Sécurité

- Les secrets (mots de passe, clés) sont dans `terraform.tfvars` — **ne jamais commiter ce fichier**
- Le Blob Storage est configuré en accès **privé** (pas d'accès public anonyme)
- Le NSG autorise uniquement les ports 22 (SSH), 80 (HTTP) et 5000 (Flask direct)
- Les mots de passe PostgreSQL sont marqués `sensitive` dans Terraform
