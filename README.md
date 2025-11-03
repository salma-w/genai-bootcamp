# GenAI Bootcamp: Production

# Getting Started

Please follow the [getting started guide](./getting-started.md) to get your machine configured.

# Opening code
 
Because this is a [monorepo](https://en.wikipedia.org/wiki/Monorepo), VS Code/Cursor and the like can be
slow to load, because it needs to run checks on the Python code for every single project.

Instead, load only the code for the task you're working on by navigating to `File -> Open Workspace from File...`
and selecting the workspace file (eg `week5/1-hello-world/1-hello-world.code-workspace`).

---

# Configuring Github Actions

You can deploy projects from GitHub actions. You must run from your
own fork to do so.

## Set up

1.  **Deploy the CloudFormation stack**

    This command will create the IAM role that GitHub Actions will use to deploy your stacks.
    Replace `<your-org>` and `<your-repo>` with your GitHub organization and repository name.
```bash
aws cloudformation deploy \
    --template-file github-actions.yaml \
    --stack-name github-actions-role \
    --parameter-overrides GitHubOrg=<your-org> GitHubRepo=<your-repo> \
    --capabilities CAPABILITY_NAMED_IAM
```

After deployment, get the `RoleArn` output from the stack.

```bash
aws cloudformation describe-stacks \
    --stack-name github-actions-role \
    --query "Stacks[0].Outputs[?OutputKey=='RoleArn'].OutputValue" \
    --output text
```

2.  **Set the `AWS_ROLE_ARN` in GitHub**

The `RoleArn` from the previous step needs to be configured as a repository variable in GitHub.

- Navigate to your repository on GitHub.
- Go to `Settings` > `Secrets and variables` > `Actions`.
- Click `New repository secret`.
- Name the variable `AWS_ROLE_ARN`.
- Paste the `RoleArn` value from the previous step.
- Click `Add variable`.

## Run a deployment from GitHub Actions

- Navigate to the `Actions` tab in your GitHub repository.
- In the left sidebar, select the workflow you want to run (e.g., `Deploy Hello World`).
- Click the `Run workflow` dropdown, and then click the `Run workflow` button to start the deployment.

---

# Topics

## Week 5

- Automated deployments and CI/CD with agentic workflows
- Building agentic applications with AWS CDK
- Creating and using tools in agentic applications
- Integrating MCP

## Week 6

- GenAI Security
- GenAI security techniques
- Creating and using AI Guardrails
- Beyond chat: Automated document processing workflows

# Week 7

- Automated document processing and embedding creation
- Effective RAG use

# Week 8

- Capstone project: Building a *real* production application

