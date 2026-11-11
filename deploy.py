# Cloudflare Workers deployment script for Houdini Fire
# Usage: python deploy.py

import os
import subprocess
import sys
from pathlib import Path

APP_DIR = Path(__file__).parent.resolve()
WRANGLER_TOML = APP_DIR / "wrangler.toml"

def run(cmd, **kwargs):
    """Run a shell command and print output."""
    print(f"$ {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=str(APP_DIR), **kwargs)
    if result.returncode != 0:
        print(f"Error: command failed with code {result.returncode}")
        sys.exit(1)
    return result

def check_prerequisites():
    """Verify wrangler is installed."""
    try:
        run("wrangler --version")
    except SystemExit:
        print("Wrangler not found. Install with: npm install -g wrangler")
        sys.exit(1)

def build():
    """Build the Workers project (if any build step is needed)."""
    print("\n=== Building Workers project ===")
    if (APP_DIR / "package.json").exists():
        run("npm install")
        run("npm run build")
    else:
        print("No build step required – serving static files directly.")

def deploy():
    """Deploy to Cloudflare Workers."""
    print("\n=== Deploying to Cloudflare Workers ===")
    run("wrangler deploy --env production")

def get_deployment_url():
    """Fetch the deployment URL after successful deploy."""
    print("\n=== Fetching deployment URL ===")
    try:
        result = subprocess.run(
            "wrangler deployments list --limit 1 --json",
            shell=True,
            capture_output=True,
            text=True,
            cwd=str(APP_DIR),
        )
        import json
        deployments = json.loads(result.stdout)
        if deployments:
            url = deployments[0].get("url", "unknown")
            print(f"Deployment URL: {url}")
            return url
    except Exception:
        pass
    return "https://bonsai-pyro.workers.dev"

def main():
    print("=== Houdini Fire Cloudflare Workers Deploy ===")
    check_prerequisites()
    build()
    deploy()
    url = get_deployment_url()
    
    # Write the address to a file
    adr_path = APP_DIR / "adr"
    with open(adr_path, "w") as f:
        f.write(f"{url}\n")
    print(f"\nDeployment address written to: {adr_path}")
    print(f"Open your browser at: {url}")

if __name__ == "__main__":
    main()