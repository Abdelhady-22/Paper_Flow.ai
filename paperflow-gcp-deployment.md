# Paper Flow AI — GCP Deployment Guide
> Complete guide to deploying Paper Flow AI on Google Cloud Platform using 4 services, with AWS comparisons, architecture, and cost breakdown.

---

## Table of Contents
1. [App Overview](#app-overview)
2. [GCP vs AWS — Full Comparison](#gcp-vs-aws-comparison)
3. [Full Architecture](#full-architecture)
4. [GCP Services Used](#gcp-services-used)
5. [Step-by-Step Setup](#step-by-step-setup)
   - [Step 1 — Project & APIs](#step-1--project--apis)
   - [Step 2 — Compute Engine (EC2)](#step-2--compute-engine--ec2)
   - [Step 3 — Cloud Storage (S3)](#step-3--cloud-storage--s3)
   - [Step 4 — Secret Manager](#step-4--secret-manager)
   - [Step 5 — Cloud Monitoring](#step-5--cloud-monitoring)
   - [Step 6 — Deploy the App](#step-6--deploy-the-app)
6. [Demo Day Workflow](#demo-day-workflow)
7. [GitHub Actions Auto-Deploy](#github-actions-auto-deploy)
8. [Cost Breakdown](#cost-breakdown)
9. [Cleanup After Demo](#cleanup-after-demo)
10. [Troubleshooting](#troubleshooting)

---

## App Overview

**Paper Flow AI** is a full-stack AI-powered academic paper assistant with 8 services:

| # | Feature | Technology | Cost |
|---|---|---|---|
| 1 | Upload PDF | FastAPI + PostgreSQL | Free |
| 2 | OCR | PaddleOCR (runs locally on CPU) | Free |
| 3 | Chat | OpenAI GPT-4o-mini via RAG + Qdrant | ~$0.001–0.003/req |
| 4 | Summarize | OpenAI GPT-4o-mini | ~$0.002–0.005/req |
| 5 | Translate (EN↔AR) | OpenAI GPT-4o-mini | ~$0.002–0.005/req |
| 6 | Q&A Generation | OpenAI GPT-4o-mini | ~$0.002–0.005/req |
| 7 | Text-to-Speech | Edge TTS (free cloud) | Free |
| 8 | Discover Papers | OpenAI Agent + Semantic Scholar | ~$0.001/req |

### Containers (5 total via Docker Compose)

```
Frontend   (Nginx + React)     :3000
Gateway    (FastAPI backend)   :8000
PostgreSQL (user data)         :5432
Qdrant     (vector embeddings) :6333
Redis      (cache + progress)  :6379
```

---

## GCP vs AWS Comparison

| AWS Service | GCP Equivalent | Used In This Guide | Purpose |
|---|---|---|---|
| EC2 | **Compute Engine (GCE)** | ✅ Yes | Virtual machine — runs all containers |
| S3 | **Cloud Storage (GCS)** | ✅ Yes | Object storage — stores uploaded PDFs |
| Secrets Manager | **Secret Manager** | ✅ Yes | Stores API keys and passwords securely |
| CloudWatch | **Cloud Monitoring** | ✅ Yes | Metrics, alerts, logs, uptime checks |
| RDS | Cloud SQL | ❌ Not needed | Managed PostgreSQL (runs in container instead) |
| ElastiCache | Memorystore | ❌ Not needed | Managed Redis (runs in container instead) |
| ECR | Artifact Registry | ❌ Not needed | Docker image storage |
| CodePipeline | Cloud Build | ❌ Not needed | CI/CD pipeline |
| Route 53 | Cloud DNS | ❌ Not needed | Domain management |
| ALB | Cloud Load Balancing | ❌ Not needed | Traffic distribution |
| Elastic IP | Static External IP | ✅ Yes | Fixed public IP address |
| Security Groups | Firewall Rules | ✅ Yes | Port access control |
| IAM Role on EC2 | Service Account | ✅ Yes | VM permissions to access GCP services |

### Key Differences AWS vs GCP

| Topic | AWS | GCP |
|---|---|---|
| CLI tool | `aws` | `gcloud` |
| SSH into VM | `aws ec2-instance-connect` or key pair | `gcloud compute ssh` (handles keys automatically) |
| Stop billing for VM | `aws ec2 stop-instances` | `gcloud compute instances stop` |
| Permissions model | IAM Role attached to EC2 | Service Account attached to VM |
| Free trial | 12 months free tier (limited) | **$300 credits for 90 days** |
| Static IP when stopped | Charged if unattached | Charged if unattached |

---

## Full Architecture

```
┌──────────────────────────────────────────────────────────┐
│            Compute Engine VM (e2-standard-2)              │
│                   = AWS EC2                               │
│                   us-central1-a                           │
│                                                           │
│   ┌──────────────┐      ┌──────────────────────────────┐ │
│   │   Frontend   │─────▶│          Gateway             │ │
│   │  Nginx+React │      │   FastAPI + OCR + Whisper    │ │
│   │    :3000     │      │          :8000               │ │
│   └──────────────┘      └──────────────────────────────┘ │
│                                                           │
│   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│   │  PostgreSQL  │  │    Qdrant    │  │    Redis     │  │
│   │    :5432     │  │    :6333     │  │    :6379     │  │
│   └──────────────┘  └──────────────┘  └──────────────┘  │
└──────────────────────────────────────────────────────────┘
          │                  │                  │
          ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│  Cloud Storage   │ │    Secret    │ │  Cloud Monitoring │
│   = AWS S3       │ │   Manager   │ │  = CloudWatch     │
│                  │ │  = AWS SM   │ │                   │
│  Bucket:         │ │             │ │  - CPU / Memory   │
│  paperflow-pdfs  │ │ OPENAI_KEY  │ │  - Uptime checks  │
│                  │ │ DB password │ │  - Log Explorer   │
│  Uploaded PDFs   │ │             │ │  - Alerts         │
│  survive reboots │ │ No .env file│ │                   │
└──────────────────┘ └──────────────┘ └──────────────────┘

External:
┌──────────────────┐
│   OpenAI API     │
│  GPT-4o-mini     │
│  (chat/summary/  │
│  translate/Q&A)  │
└──────────────────┘
```

---

## GCP Services Used

### 1. Compute Engine (= AWS EC2)
Runs all 5 Docker containers on a single VM using Docker Compose.
- Machine type: `e2-standard-2` (2 vCPU, 8 GB RAM)
- OS: Ubuntu 22.04 LTS
- Zone: `us-central1-a`
- Cost: ~$0.067/hr

### 2. Cloud Storage (= AWS S3)
Stores uploaded PDF files outside the VM so they survive reboots and redeployments.
- Location: `US-CENTRAL1`
- Storage class: Standard
- Access: Private (VM service account only)
- Cost: ~$0.02/GB/month

### 3. Secret Manager (= AWS Secrets Manager)
Stores all sensitive values — no API keys or passwords in `.env` files or code.
- Secrets stored: `OPENAI_API_KEY`, `POSTGRES_PASSWORD`
- Access: VM service account only
- Cost: Free under 10,000 operations/month

### 4. Cloud Monitoring (= AWS CloudWatch)
Monitors VM health, tracks uptime, sends alerts, and stores logs.
- Metrics: CPU, memory, network, disk
- Uptime checks: frontend (:3000) and API (:8000)
- Alerts: CPU > 80%
- Cost: Free (first 5 GB logs/month)

---

## Step-by-Step Setup

### Step 1 — Project & APIs

**Login to GCP:**
```bash
gcloud auth login
```

**Set your project:**
```bash
gcloud config set project YOUR_PROJECT_ID
```

**Enable all required service APIs:**
```bash
gcloud services enable compute.googleapis.com
```

```bash
gcloud services enable storage.googleapis.com
```

```bash
gcloud services enable secretmanager.googleapis.com
```

```bash
gcloud services enable monitoring.googleapis.com
```

```bash
gcloud services enable logging.googleapis.com
```

---

### Step 2 — Compute Engine (= EC2)

**Create a static external IP (so URL never changes after restart):**
```bash
gcloud compute addresses create paperflow-ip \
  --region=us-central1
```

**Check your static IP value:**
```bash
gcloud compute addresses describe paperflow-ip \
  --region=us-central1 \
  --format="get(address)"
```

**Create the VM:**
```bash
gcloud compute instances create paperflow-vm \
  --zone=us-central1-a \
  --machine-type=e2-standard-2 \
  --image-family=ubuntu-2204-lts \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=50GB \
  --address=paperflow-ip \
  --tags=paperflow-server \
  --scopes=cloud-platform
```

> `--scopes=cloud-platform` allows the VM to talk to Cloud Storage, Secret Manager, and Monitoring automatically.

**Open port 3000 (Frontend):**
```bash
gcloud compute firewall-rules create allow-paperflow-frontend \
  --allow=tcp:3000 \
  --target-tags=paperflow-server \
  --description="PaperFlow frontend port"
```

**Open port 8000 (API / Swagger):**
```bash
gcloud compute firewall-rules create allow-paperflow-api \
  --allow=tcp:8000 \
  --target-tags=paperflow-server \
  --description="PaperFlow API port"
```

**Verify VM is running:**
```bash
gcloud compute instances list
```

---

### Step 3 — Cloud Storage (= S3)

**Create the bucket (name must be globally unique, lowercase only):**
```bash
gcloud storage buckets create gs://paperflow-pdfs-demo \
  --location=US-CENTRAL1 \
  --uniform-bucket-level-access
```

**Get your project number (needed for IAM binding):**
```bash
gcloud projects describe YOUR_PROJECT_ID \
  --format="get(projectNumber)"
```

**Give the VM permission to read and write the bucket:**
```bash
gcloud storage buckets add-iam-policy-binding \
  gs://paperflow-pdfs-demo \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/storage.objectAdmin"
```

> Replace `YOUR_PROJECT_NUMBER` with the number from the previous command.

**Verify the bucket was created:**
```bash
gcloud storage buckets list
```

**Test upload from VM (run this after SSHing into the VM):**
```bash
echo "test" > test.txt && gcloud storage cp test.txt gs://paperflow-pdfs-demo/
```

**List bucket contents:**
```bash
gcloud storage ls gs://paperflow-pdfs-demo/
```

---

### Step 4 — Secret Manager (= AWS Secrets Manager)

**Store your OpenAI API key:**
```bash
echo -n "sk-your-real-openai-key-here" | \
  gcloud secrets create OPENAI_API_KEY \
  --data-file=- \
  --replication-policy=automatic
```

**Store your Postgres password:**
```bash
echo -n "your-strong-db-password" | \
  gcloud secrets create POSTGRES_PASSWORD \
  --data-file=- \
  --replication-policy=automatic
```

**Verify secrets are stored:**
```bash
gcloud secrets list
```

**Grant the VM access to OPENAI_API_KEY:**
```bash
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Grant the VM access to POSTGRES_PASSWORD:**
```bash
gcloud secrets add-iam-policy-binding POSTGRES_PASSWORD \
  --member="serviceAccount:YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

**Test fetching a secret (run on VM after SSH):**
```bash
gcloud secrets versions access latest --secret="OPENAI_API_KEY"
```

---

### Step 5 — Cloud Monitoring (= CloudWatch)

**Get your static IP for uptime checks:**
```bash
gcloud compute addresses describe paperflow-ip \
  --region=us-central1 \
  --format="get(address)"
```

**Create uptime check for the frontend (:3000):**
```bash
gcloud monitoring uptime create \
  --display-name="PaperFlow Frontend Check" \
  --http-check-path="/" \
  --port=3000 \
  --hostname=YOUR_STATIC_IP
```

**Create uptime check for the API (:8000):**
```bash
gcloud monitoring uptime create \
  --display-name="PaperFlow API Check" \
  --http-check-path="/docs" \
  --port=8000 \
  --hostname=YOUR_STATIC_IP
```

**View live metrics in GCP Console:**
```
console.cloud.google.com → Monitoring → Dashboards
```

**View all logs:**
```
console.cloud.google.com → Logging → Log Explorer
```

**Filter logs by your VM:**
```
resource.type="gce_instance" AND resource.labels.instance_id="paperflow-vm"
```

---

### Step 6 — Deploy the App

**SSH into the VM:**
```bash
gcloud compute ssh paperflow-vm --zone=us-central1-a
```

**Update system packages:**
```bash
sudo apt update && sudo apt upgrade -y
```

**Install Docker:**
```bash
curl -fsSL https://get.docker.com | sh
```

**Add your user to Docker group:**
```bash
sudo usermod -aG docker $USER
```

**Apply group change without logout:**
```bash
newgrp docker
```

**Verify Docker is installed:**
```bash
docker --version && docker compose version
```

**Fetch OpenAI key from Secret Manager into environment:**
```bash
export OPENAI_API_KEY=$(gcloud secrets versions access latest --secret="OPENAI_API_KEY")
```

**Fetch Postgres password from Secret Manager into environment:**
```bash
export POSTGRES_PASSWORD=$(gcloud secrets versions access latest --secret="POSTGRES_PASSWORD")
```

> `gcloud` is pre-installed on GCE Ubuntu images and auto-authenticates via the VM's service account. No manual install or login needed.

**Clone the repository:**
```bash
git clone https://github.com/Abdelhady-22/Paper_Flow.ai.git
```

**Go into the project directory:**
```bash
cd Paper_Flow.ai
```

**Copy the OpenAI env template:**
```bash
cp .env.local-openai .env
```

**Inject the OpenAI key into .env (no manual editing):**
```bash
sed -i "s|OPENAI_API_KEY=.*|OPENAI_API_KEY=${OPENAI_API_KEY}|" .env
```

**Inject the Postgres password into .env:**
```bash
sed -i "s|POSTGRES_PASSWORD=.*|POSTGRES_PASSWORD=${POSTGRES_PASSWORD}|" .env
```

**Fix the password inside DATABASE_URL too:**
```bash
sed -i "s|securepassword|${POSTGRES_PASSWORD}|g" .env
```

**Enable GCS storage backend (PDFs stored in Cloud Storage bucket):**
```bash
sed -i "s|STORAGE_BACKEND=.*|STORAGE_BACKEND=gcs|" .env
sed -i "s|GCS_BUCKET_NAME=.*|GCS_BUCKET_NAME=paperflow-pdfs-demo|" .env
```

**Set CORS to allow access from the static IP:**
```bash
STATIC_IP=$(curl -s http://metadata.google.internal/computeMetadata/v1/instance/network-interfaces/0/access-configs/0/external-ip -H "Metadata-Flavor: Google")
sed -i "s|CORS_ORIGINS=.*|CORS_ORIGINS=http://localhost:3000,http://${STATIC_IP}:3000|" .env
```

**Set DEBUG to false for production:**
```bash
sed -i "s|DEBUG=.*|DEBUG=false|" .env
```

**Build and start all 5 containers:**
```bash
docker compose up --build -d
```

> First build takes 10–15 minutes (downloads Python packages, ML models, Node modules). All subsequent starts take seconds.

**Watch container health (wait until all show "healthy"):**
```bash
watch -n 3 docker compose ps
```

**Check gateway logs to confirm it started correctly:**
```bash
docker compose logs gateway --tail 50
```

**Test the app is reachable:**
```bash
curl http://localhost:3000
```

```bash
curl http://localhost:8000/docs
```

**Your app is now live at:**
```
http://YOUR_STATIC_IP:3000       ← Main App
http://YOUR_STATIC_IP:8000/docs  ← API Swagger Docs
```

---

## Demo Day Workflow

### Before the Demo

**Start the VM (if it was stopped):**
```bash
gcloud compute instances start paperflow-vm --zone=us-central1-a
```

**SSH into the VM:**
```bash
gcloud compute ssh paperflow-vm --zone=us-central1-a
```

**Start all containers:**
```bash
cd Paper_Flow.ai && docker compose up -d
```

**Monitor container health:**
```bash
watch -n 3 docker compose ps
```

### During the Demo

**Keep live logs running in a second terminal:**
```bash
docker compose logs -f gateway
```

**Check all containers are still healthy:**
```bash
docker compose ps
```

**Check GPU / CPU usage on VM:**
```bash
top
```

### After the Demo

**Stop containers to free VM resources:**
```bash
docker compose down
```

**Stop the VM — no compute charges while stopped:**
```bash
gcloud compute instances stop paperflow-vm --zone=us-central1-a
```

> ⚠️ Use `stop` not `delete` — stopping keeps your data. Deleting removes everything.

---

## GitHub Actions Auto-Deploy

Automatically deploy to your GCP VM when you push to `main`.

### How It Works

```
You push to main → GitHub Actions triggers → SSH into GCP VM → git pull → docker compose up --build -d → Live!
```

### One-Time Setup

**1. Generate a deploy SSH key (on your local machine):**
```bash
ssh-keygen -t ed25519 -f ~/.ssh/paperflow-deploy -N ""
```

**2. Add the public key to the GCP VM:**
```bash
gcloud compute instances add-metadata paperflow-vm \
  --zone=us-central1-a \
  --metadata-from-file=ssh-keys=<(echo "$(whoami):$(cat ~/.ssh/paperflow-deploy.pub)")
```

**3. Add these secrets to your GitHub repository:**

Go to: `GitHub Repo → Settings → Secrets and variables → Actions → New repository secret`

| Secret Name | Value |
|---|---|
| `GCP_VM_IP` | Your static IP (run `gcloud compute addresses describe paperflow-ip --region=us-central1 --format="get(address)"`) |
| `GCP_SSH_PRIVATE_KEY` | Content of `~/.ssh/paperflow-deploy` (the private key file) |
| `GCP_SSH_USER` | Your username on the VM (usually your Google account username, run `whoami` on the VM) |

**4. Verify:** Push a commit to `main` and check the Actions tab — you should see the "Deploy to GCP" workflow run.

### Manual Trigger

You can also trigger a deploy manually:
```
GitHub Repo → Actions → Deploy to GCP → Run workflow
```

### Workflow File

The deploy workflow is at `.github/workflows/deploy-gcp.yml`.

---

## Cost Breakdown

### Machine Type Options

| GCP Machine | vCPU | RAM | Cost/hr | 3-day max |
|---|---|---|---|---|
| `e2-medium` | 2 | 4 GB | ~$0.033/hr | ~$2.40 |
| **`e2-standard-2`** ✅ | **2** | **8 GB** | **~$0.067/hr** | **~$4.80** |
| `e2-standard-4` | 4 | 16 GB | ~$0.134/hr | ~$9.70 |

> `e2-standard-2` is the sweet spot — 8 GB RAM handles all 5 containers comfortably.

### Full 3-Day Cost

| Service | AWS Equivalent | 3-Day Cost | From $300 Credits |
|---|---|---|---|
| Compute Engine e2-standard-2 (24 active hrs) | EC2 t3.medium | ~$4.80 | ✅ Free |
| Cloud Storage (few PDFs uploaded) | S3 | ~$0.01 | ✅ Free |
| Secret Manager (< 10,000 ops) | Secrets Manager | ~$0.00 | ✅ Free |
| Cloud Monitoring (< 5 GB logs) | CloudWatch | ~$0.00 | ✅ Free |
| Static External IP | Elastic IP | ~$0.01 | ✅ Free |
| **Total** | | **~$4.82** | **$295.18 remaining** |

### OpenAI API Cost (separate from GCP)

| Operation | Model | Cost per Call |
|---|---|---|
| Chat (RAG) | gpt-4o-mini | ~$0.001–0.003 |
| Summarize | gpt-4o-mini | ~$0.002–0.005 |
| Translate | gpt-4o-mini | ~$0.002–0.005 |
| Q&A Generate | gpt-4o-mini | ~$0.002–0.005 |
| Agent (discover) | gpt-4o-mini | ~$0.001 |
| **Full test session** | | **~$0.02–0.05** |

### Cost Saving Tips

**Stop VM between demos (save ~$0.067/hr):**
```bash
gcloud compute instances stop paperflow-vm --zone=us-central1-a
```

**Restart when needed:**
```bash
gcloud compute instances start paperflow-vm --zone=us-central1-a
```

> If you only run the VM 8 hours/day across 3 days (24 hrs total), cost drops to **~$1.60** instead of $4.80.

---

## Cleanup After Demo

**Delete VM:**
```bash
gcloud compute instances delete paperflow-vm --zone=us-central1-a
```

**Delete static IP:**
```bash
gcloud compute addresses delete paperflow-ip --region=us-central1
```

**Delete storage bucket and all PDFs inside:**
```bash
gcloud storage rm -r gs://paperflow-pdfs-demo
```

**Delete OpenAI secret:**
```bash
gcloud secrets delete OPENAI_API_KEY
```

**Delete Postgres password secret:**
```bash
gcloud secrets delete POSTGRES_PASSWORD
```

**Delete firewall rules:**
```bash
gcloud compute firewall-rules delete allow-paperflow-frontend
```

```bash
gcloud compute firewall-rules delete allow-paperflow-api
```

**Verify nothing is left running (avoid surprise charges):**
```bash
gcloud compute instances list
```

```bash
gcloud compute addresses list
```

```bash
gcloud secrets list
```

---

## Troubleshooting

| Problem | Command to Diagnose | Fix |
|---|---|---|
| VM won't start | `gcloud compute instances describe paperflow-vm --zone=us-central1-a` | Check quota in us-central1 |
| Can't reach :3000 or :8000 | `gcloud compute firewall-rules list` | Re-run firewall-rules create commands |
| Container keeps restarting | `docker compose logs gateway --tail 50` | Check OPENAI_API_KEY is set correctly in .env |
| Secret not found | `gcloud secrets list` | Re-run secret create command |
| Permission denied on bucket | `gcloud projects get-iam-policy YOUR_PROJECT_ID` | Re-run storage IAM binding command |
| Static IP changed | `gcloud compute addresses describe paperflow-ip --region=us-central1` | You used `delete` instead of `stop` on the VM |
| Out of disk space | `df -h` on the VM | `docker system prune -a` to free space |
| Build takes too long | Normal on first run | Pre-build the night before your demo |

**Most useful debug commands (run on VM):**

**Check all container statuses:**
```bash
docker compose ps
```

**Follow live logs from all containers:**
```bash
docker compose logs -f
```

**Follow gateway logs only:**
```bash
docker compose logs gateway -f
```

**Restart only the gateway:**
```bash
docker compose restart gateway
```

**Full reset — stop and remove all containers and volumes:**
```bash
docker compose down -v
```

**Free disk space from old Docker images:**
```bash
docker system prune -a
```

---

## Quick Reference — All Commands at a Glance

### From Your Local Machine

| Action | Command |
|---|---|
| Login to GCP | `gcloud auth login` |
| Set project | `gcloud config set project YOUR_PROJECT_ID` |
| Create static IP | `gcloud compute addresses create paperflow-ip --region=us-central1` |
| Create VM | `gcloud compute instances create paperflow-vm --zone=us-central1-a --machine-type=e2-standard-2 --image-family=ubuntu-2204-lts --image-project=ubuntu-os-cloud --boot-disk-size=50GB --address=paperflow-ip --tags=paperflow-server --scopes=cloud-platform` |
| SSH into VM | `gcloud compute ssh paperflow-vm --zone=us-central1-a` |
| Start VM | `gcloud compute instances start paperflow-vm --zone=us-central1-a` |
| Stop VM | `gcloud compute instances stop paperflow-vm --zone=us-central1-a` |
| List VMs | `gcloud compute instances list` |

### Inside the VM

| Action | Command |
|---|---|
| Start all containers | `docker compose up -d` |
| Stop all containers | `docker compose down` |
| Check container health | `docker compose ps` |
| Watch logs live | `docker compose logs -f` |
| Restart gateway | `docker compose restart gateway` |
| Rebuild everything | `docker compose up --build -d` |
| Free disk space | `docker system prune -a` |
