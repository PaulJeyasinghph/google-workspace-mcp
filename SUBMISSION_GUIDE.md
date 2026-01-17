# Docker MCP Registry Submission Guide

This document provides step-by-step instructions for submitting the Google Workspace MCP Server to the Docker MCP registry.

## Prerequisites Checklist

Before submitting, ensure you have:

- [x] Created all required files (Dockerfile, server.yaml, tools.json, README.md, LICENSE)
- [x] MIT License applied
- [ ] GitHub repository created and code pushed
- [ ] Docker image built and tested locally
- [ ] Docker Hub account created
- [ ] Docker image pushed to Docker Hub

## Step 1: Create GitHub Repository

1. Go to [GitHub](https://github.com) and create a new repository:
   - **Name**: `google-workspace-mcp`
   - **Description**: "Comprehensive MCP server for Google Workspace APIs"
   - **Visibility**: Public
   - **License**: MIT

2. Initialize the repository locally:

```bash
cd google-workspace-mcp
git init
git add .
git commit -m "Initial commit: Google Workspace MCP Server"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/google-workspace-mcp.git
git push -u origin main
```

3. Note the commit hash:

```bash
git rev-parse HEAD
```

## Step 2: Build and Test Docker Image

1. Build the Docker image:

```bash
docker build -t google-workspace-mcp:latest .
```

2. Test the image locally:

```bash
# Create a test credentials directory
mkdir -p test-credentials

# Run the container interactively
docker run -i --rm \
  -v $(pwd)/test-credentials:/data/credentials \
  google-workspace-mcp:latest
```

3. Verify all tools are available and authentication works.

## Step 3: Push to Docker Hub

1. Create a Docker Hub account at [hub.docker.com](https://hub.docker.com)

2. Log in to Docker Hub:

```bash
docker login
```

3. Tag your image:

```bash
docker tag google-workspace-mcp:latest YOUR_DOCKERHUB_USERNAME/google-workspace-mcp:latest
```

4. Push to Docker Hub:

```bash
docker push YOUR_DOCKERHUB_USERNAME/google-workspace-mcp:latest
```

## Step 4: Fork Docker MCP Registry

1. Go to the [Docker MCP Registry](https://github.com/docker/mcp-registry)

2. Click "Fork" to create your fork

3. Clone your fork:

```bash
git clone https://github.com/YOUR_USERNAME/mcp-registry.git
cd mcp-registry
```

## Step 5: Add Your Server to the Registry

### Option A: Using the Wizard (Recommended)

```bash
# Install Task if not already installed
brew install go-task/tap/go-task  # macOS
# or
sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d  # Linux

# Run the wizard
task wizard
```

Follow the prompts:
- **Server name**: `google-workspace`
- **Type**: `server` (local/containerized)
- **Category**: `productivity`
- **Title**: `Google Workspace MCP Server`
- **Description**: (paste from server.yaml)
- **Icon URL**: `https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png`
- **Source project URL**: `https://github.com/YOUR_USERNAME/google-workspace-mcp`
- **Commit hash**: (from Step 1.3)
- **Tags**: `google, workspace, gmail, drive, sheets, calendar, docs, forms, chat`

### Option B: Manual Configuration

1. Create the server directory:

```bash
mkdir -p servers/google-workspace
```

2. Copy your files:

```bash
cp /path/to/google-workspace-mcp/server.yaml servers/google-workspace/
cp /path/to/google-workspace-mcp/tools.json servers/google-workspace/
cp /path/to/google-workspace-mcp/README.md servers/google-workspace/readme.md
```

3. Update `server.yaml` with your GitHub repo URL and commit hash.

## Step 6: Test the Registry Entry

1. Build and test locally:

```bash
task build -- --tools google-workspace
```

2. Import the catalog:

```bash
docker mcp catalog import catalog.yaml
```

3. Verify in Docker Desktop:
   - Open Docker Desktop
   - Go to MCP Toolkit
   - Find "Google Workspace MCP Server"
   - Test the connection

4. Clean up:

```bash
docker mcp catalog reset
```

## Step 7: Submit Pull Request

1. Commit your changes:

```bash
git add servers/google-workspace/
git commit -m "Add Google Workspace MCP Server

Comprehensive MCP server providing unified access to:
- Gmail (read, send, search emails)
- Google Drive (file management)
- Google Sheets (spreadsheet operations)
- Google Calendar (event management)
- Google Docs (document editing)
- Google Forms (form creation and responses)
- Google Chat (messaging)

25+ tools across 7 Google Workspace services with OAuth 2.0 authentication."
```

2. Push to your fork:

```bash
git push origin main
```

3. Create a Pull Request:
   - Go to your fork on GitHub
   - Click "Contribute" → "Open pull request"
   - **Title**: "Add Google Workspace MCP Server"
   - **Description**:

```markdown
## Summary

This PR adds a comprehensive MCP server for Google Workspace APIs, providing unified access to 7 major Google services through a single Docker container.

## Features

- **25+ Tools** across Gmail, Drive, Sheets, Calendar, Docs, Forms, and Chat
- **OAuth 2.0 Authentication** with automatic token refresh
- **Production-Ready** with secure credential handling
- **MIT Licensed** for community use

## Testing

- [x] Built and tested locally
- [x] All tools verified
- [x] Docker image published to Docker Hub
- [x] Documentation complete
- [x] CI passes

## Related Links

- GitHub: https://github.com/YOUR_USERNAME/google-workspace-mcp
- Docker Hub: https://hub.docker.com/r/YOUR_DOCKERHUB_USERNAME/google-workspace-mcp
```

4. Wait for Docker team review

## Step 8: Respond to Review Feedback

The Docker team will review your submission and may request changes:

1. Monitor your PR for comments
2. Make requested changes
3. Push updates to your fork
4. The PR will automatically update

## Step 9: Post-Approval

Once approved:

1. Your server will be added to the registry within 24 hours
2. It will appear in:
   - Docker Desktop MCP Toolkit
   - Docker Hub `mcp` namespace
   - MCP catalog

3. Update your README badges to point to the official Docker Hub image

## Troubleshooting

### Build Failures

If `task build` fails:
- Ensure `tools.json` is valid JSON
- Verify all required fields in `server.yaml`
- Check Dockerfile syntax

### Authentication Issues

If OAuth doesn't work in testing:
- Verify Google Cloud APIs are enabled
- Check OAuth consent screen configuration
- Ensure credentials are properly mounted

### CI Failures

If the GitHub Actions CI fails:
- Review the error messages in the PR
- Fix issues locally
- Push updates

## Maintenance

After approval, maintain your server by:

1. Fixing bugs reported in issues
2. Adding new features
3. Updating documentation
4. Keeping dependencies up to date

## Support

- **Docker MCP Registry**: [Issues](https://github.com/docker/mcp-registry/issues)
- **Your Server**: [Issues](https://github.com/YOUR_USERNAME/google-workspace-mcp/issues)
- **MCP Documentation**: [modelcontextprotocol.io](https://modelcontextprotocol.io)

## Resources

- [Docker MCP Registry Contributing Guide](https://github.com/docker/mcp-registry/blob/main/CONTRIBUTING.md)
- [Google Workspace APIs](https://developers.google.com/workspace)
- [Model Context Protocol Specification](https://spec.modelcontextprotocol.io)

---

Good luck with your submission! 🚀
