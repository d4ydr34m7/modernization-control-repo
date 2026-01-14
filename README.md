# Modernization Control Repo

Repository discovery tool for scanning GitHub organizations.

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
     - ✅ `read:org` - Required to read organization repositories
     - ✅ `repo` - Required if you want to access private repositories (optional but recommended)
   
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

## Usage

### Running Phase 1 Analysis

#### Local Execution

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

Run the analysis script:
```bash
source venv/bin/activate
python scripts/run_phase1_analysis.py
```

The script will:
1. Discover repositories from `config/repos.yaml`
2. Clone each repository to `tmp/`
3. Run AWS Transform analysis automatically
4. Copy Transform output to `repos/<repo-name>/analysis/`
5. Update the registry at `repos/analysis_registry.yaml`
6. Clean up cloned repositories

#### CI/CD Execution (GitHub Actions)

The repository includes a GitHub Actions workflow that runs Phase 1 analysis automatically.

**Setup:**
1. Add AWS credentials as GitHub Secrets:
   - Go to Repository → Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Add `AWS_ACCESS_KEY_ID` with your AWS access key
   - Add `AWS_SECRET_ACCESS_KEY` with your AWS secret key

2. Push code to GitHub (workflow file is already included)

**Triggers:**
- Manual trigger: Go to Actions tab → "Phase 1 Analysis" → "Run workflow"
- Weekly schedule: Runs every Sunday at midnight UTC
- Config changes: Automatically runs when `config/repos.yaml` is updated

**Results:**
- Analysis results are uploaded as artifacts (retained for 30 days)
- Registry updates are saved in the workflow run
