# EC2 + RDS + Vercel Deployment

This is the deliberately small showcase deployment:

```text
Vercel frontend -> /api rewrite -> EC2 Caddy -> FastAPI -> private ML container -> RDS PostgreSQL
```

The ML runtime has no public port. Only Caddy publishes port 80 on the EC2
host. Vercel is the browser-facing HTTPS endpoint; Caddy is intentionally HTTP
because this deployment does not use a custom domain. Caddy allows a 12 MB
request to accommodate multipart metadata; FastAPI still limits the file itself
to 10 MB.

## AWS resources

1. Create RDS PostgreSQL in the same VPC as the EC2 instance. Set it to not
   publicly accessible and allow port 5432 only from the EC2 security group.
2. Create an EC2 Ubuntu instance with at least 4 GB RAM. The ML runtime loads
   TensorFlow and multiple models at startup.
3. Attach an Elastic IP if the instance may be stopped and restarted.
4. EC2 security group inbound rules: TCP 22 from the operator's IP, TCP 80
   from anywhere. Do not open 8000 or 5432.

## Host setup

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker $USER
```

Reconnect, clone the repository, then create the untracked environment file:

```bash
git clone YOUR_REPOSITORY_URL scamsigurado
cd scamsigurado
cp deploy/ec2/.env.production.example deploy/ec2/.env.production
chmod 600 deploy/ec2/.env.production
```

Set the RDS endpoint, password, and Vercel project URL in
`deploy/ec2/.env.production`.

## Deploy

```bash
docker compose -f deploy/ec2/docker-compose.yml build
docker compose -f deploy/ec2/docker-compose.yml run --rm api alembic upgrade head
docker compose -f deploy/ec2/docker-compose.yml up -d
docker compose -f deploy/ec2/docker-compose.yml ps
curl http://127.0.0.1/health
```

## Vercel

Set the Vercel project root directory to `apps/web`, then configure:

```text
NEXT_PUBLIC_API_URL=/api
API_PROXY_TARGET=http://YOUR_EC2_ELASTIC_IP
```

Redeploy after saving the values. The Next.js rewrite forwards `/api/*` to EC2
without exposing the EC2 URL to browser-side application code.

## Update and rollback

```bash
git pull
docker compose -f deploy/ec2/docker-compose.yml build
docker compose -f deploy/ec2/docker-compose.yml run --rm api alembic upgrade head
docker compose -f deploy/ec2/docker-compose.yml up -d
```

To roll back, check out the last working Git commit and run the same commands.
