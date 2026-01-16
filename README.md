# Modernization Control Repo

Automated AWS Transform analysis for codebase modernization. Discovers repositories and executes comprehensive codebase analysis using AWS Transform on stable execution environments.

## Architecture

**Control-Plane vs Execution-Plane Separation:**
- **Control-plane**: GitHub Actions workflow - orchestration and artifact management
- **Execution-plane**: Self-hosted runner (EC2 / long-lived machine) - Transform execution

**Execution Requirements:**
- Execution requires a self-hosted runner that is:
  - **Always on** (or automatically started before scheduled runs)
  - **Long-running** (not subject to CI timeout limits)
  - **Not subject to CI payload limits** (persistent storage for large outputs)
- AWS Transform is **NOT** executed in ephemeral CI/CD runners due to:
  - Large, stateful output requiring persistent storage
  - ATX early-access instability in ephemeral runners
  - Long execution times (1-2+ hours) requiring stable execution environment

**Status Tracking:**
- `pending`: Repository discovered, not started
- `running`: Transform execution started
- `analyzed`: Transform completed successfully (output-aware detection)
- `failed`: Transform execution failed

## Setup

### 1. Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. GitHub Token Setup (for org_scan mode)

To use `org_scan` mode, you need a GitHub Personal Access Token:

1. **Create a GitHub Token (Step-by-Step):**
   
   **Step 1:** Go to GitHub token settings
   - Open your web browser
   - Navigate to: https://github.com/settings/tokens
   - Or: GitHub → Your Profile (top right) → Settings → Developer settings → Personal access tokens → Tokens (classic)
   
   **Step 2:** Generate a new token
   - Click the "Generate new token" button
   - Select "Generate new token (classic)"
   - You may be prompted to enter your GitHub password for security
   
   **Step 3:** Configure the token
   - **Note:** Give it a descriptive name like "repo-scanner" or "modernization-control-repo"
   - **Expiration:** Choose an expiration (90 days, 1 year, or no expiration)
   - **Scopes:** Check the following permissions:
     - `read:org` - Required to read organization repositories
     - `repo` - Required if you want to access private repositories (optional but recommended)
   
   **Step 4:** Generate and copy
   - Scroll down and click the green "Generate token" button
   - **IMPORTANT:** Copy the token immediately (starts with `ghp_...`)
   - GitHub will only show it once - if you lose it, you'll need to create a new one
   - Store it securely (password manager, etc.)

2. **Configure GitHub Token:**

   **Option A: Using .env file (Recommended):**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your token
   # GITHUB_TOKEN=your_token_here
   ```
   
   The `.env` file is already in `.gitignore` and won't be committed.

   **Option B: Environment Variable (Alternative):**
   ```bash
   export GITHUB_TOKEN=your_token_here
   ```
   
   **Security Note:** 
   - Never commit your GitHub token to version control
   - The `.gitignore` file is configured to exclude `.env` files
   - The `.env` file is the recommended secure storage method

### 3. AWS Credentials Setup

**For Self-Hosted Runner (EC2 / Long-lived Machine):**

**Option A: AWS SSO (Recommended)**
```bash
# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip && sudo ./aws/install

# Configure SSO
aws configure sso
# Follow prompts: SSO start URL, region, profile name

# Login when needed
aws sso login
```

**Option B: Environment Variables**
1. Set environment variables on the self-hosted runner:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_DEFAULT_REGION`
2. Configure AWS CLI to use them:
```bash
mkdir -p ~/.aws
cat > ~/.aws/credentials << EOF
[default]
aws_access_key_id = ${AWS_ACCESS_KEY_ID}
aws_secret_access_key = ${AWS_SECRET_ACCESS_KEY}
EOF

cat > ~/.aws/config << EOF
[default]
region = ${AWS_DEFAULT_REGION:-us-east-1}
EOF
```

**For Local Development (Testing Only):**
```bash
# Use AWS SSO or configure credentials
aws configure
# Or use AWS SSO as shown above
```

### 4. Install AWS Transform CLI

```bash
# Install ATX CLI
curl -fsSL https://desktop-release.transform.us-east-1.api.aws/install.sh | bash

# Verify installation
atx --version
```

## Usage

### Running Phase 1 Analysis

**Important:** This script must run on a self-hosted runner (EC2 / long-lived machine). Local development (IDE) is for testing only. NOT for ephemeral CI/CD runners.

#### Configuration

Edit `config/repos.yaml` to configure which repositories to analyze:

**Single Mode:**
```yaml
mode: single

single:
  name: my-repo
  git_url: https://github.com/user/my-repo.git
```

**Org Scan Mode:**
```yaml
mode: org_scan

org_scan:
  github_org: your-org-name
  filters:
    language: java
    exclude_archived: true
    exclude_forks: true
  limits:
    max_repos_per_run: 3
```

#### Execution

**Basic usage (idempotent - skips already analyzed repos):**
```bash
source venv/bin/activate
python scripts/run_phase1_analysis.py
```

**Force re-analysis:**
```bash
python scripts/run_phase1_analysis.py --force
```

The script will:
1. Discover repositories from `config/repos.yaml`
2. **Skip repos already marked as `analyzed`** (idempotent by default)
3. Clone each repository to `tmp/`
4. Mark repo status as `running`
5. Run AWS Transform analysis (output-aware: preserves results even if process errors)
6. Detect success via multiple indicators (log messages + output folders)
7. Copy Transform output to `repos/<repo-name>/analysis/`
8. Update registry status (`analyzed` or `failed`)
9. Clean up cloned repositories

**Output Location:**
- Analysis results: `repos/<repo-name>/analysis/`
- Logs: `repos/<repo-name>_transform.log`
- Registry: `repos/analysis_registry.yaml`

#### Idempotent Behavior

- **Default**: Repos with `analysis_status: "analyzed"` are automatically skipped
- **Override**: Use `--force` flag to re-analyze already analyzed repos
- **Re-runs**: Repos with status `pending`, `running`, or `failed` are always included

#### Success Detection

The script uses **output-aware success detection** (not just exit codes):
- Checks log file for "successfully completed with all exit criteria met"
- Validates multiple output folders exist (Documentation, .aws, etc.)
- Preserves outputs even if Transform process exits with error
- Marks as `analyzed` if outputs/logs indicate success, regardless of exit code

### GitHub Actions Workflow (Self-Hosted Runner)

**Architecture:**
- **Control-plane**: GitHub Actions (orchestration, artifact upload)
- **Execution-plane**: Self-hosted runner (EC2 / long-lived machine)

The GitHub Actions workflow (`phase1-analysis.yml`) executes Phase 1 analysis on a **self-hosted runner** (EC2 / long-lived machine), then uploads results as artifacts.

The self-hosted runner must be:
- **Always on** (or automatically started before scheduled runs)
- **Long-running** (not subject to CI timeout limits)
- **Not subject to CI payload limits** (persistent storage for large outputs)

**Prerequisites on self-hosted runner:**
1. **Install AWS Transform CLI:**
   ```bash
   curl -fsSL https://desktop-release.transform.us-east-1.api.aws/install.sh | bash
   ```

2. **Configure AWS credentials** (choose one):
   - **AWS SSO** (recommended):
     ```bash
     aws configure sso
     aws sso login
     ```
   - **Environment variables**:
     - Set `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` on the runner
     - Configure AWS CLI to use them (see Setup section above)

3. **Install GitHub Actions runner:**
   ```bash
   # Download and install runner (follow GitHub's self-hosted runner setup guide)
   # Runner must be running and registered with your repository
   ```

4. **GitHub Token (for org_scan mode):**
   - Add `GITHUB_TOKEN_CUSTOM` secret to repository (PAT with `read:org` permission)
   - Or ensure default `GITHUB_TOKEN` has required permissions

**What the workflow does:**
- Executes `run_phase1_analysis.py` on the self-hosted runner
- Verifies AWS Transform CLI and credentials are configured
- Runs Transform analysis (scheduled or manual trigger)
- Uploads analysis results and logs as artifacts

**Triggers:**
- **Manual trigger**: Actions → "Phase 1 Analysis" → "Run workflow"
- **Scheduled**: Weekly on Sunday at midnight UTC (cron: `0 0 * * 0`)
- **Automatic**: When `config/repos.yaml` is updated

**Results:**
- Analysis results uploaded as artifacts (retained for 30 days)
- Logs available for download
- Registry updated with analysis status
