Hi everyone!

I hope you're excited to cast off your Python notebooks and depart for the next phase of using LLMs: building for production.
We're going to be building everything using AWS, so for my four weeks of the bootcamp you will need an AWS account.
Total expected spend is under $50 US, including all model usage.

It can take a few days to get your account set up if you're unlucky and your account gets flagged, so I would
strongly recommend getting an account set up now if you haven't already. Please visit https://aws.amazon.com/
and click the 'Create Account' button at the top right.

Your can [use the CloudWolf guide to creating an AWS account](https://www.dropbox.com/scl/fi/nbwph7yjzvzqcai5qm1ut/Getting-Started-with-AWS-Beginner-Handbook-v3.7.pdf?rlkey=tjvloyxjecl0fjbcinrcttmhi&dl=0), 
but please note that some of the UI may have changed since that document was created.
I would also suggest create a billing alert using the process detailed in the CloudWolf document.

If your AWS account is brand new please verify that you can launch an EC2 instance by following the 
[launch my first EC2 instance directions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/tutorial-launch-my-first-ec2-instance.html).

It can take up to 24 hours from account creation before you're able to launch an instance.
You can terminate it once it reaches 'running' state.

Once you have confirmed you can use EC2, please enable access to the LLMs we will be using for this section
of the course.

To do this:

- Open the Bedrock console: https://console.aws.amazon.com/bedrock/
- Ensure that you are in the `us-west-2` region. Because not all features are in all regions, we will be using
  `us-west-2` for all examples
- Select **Chat / Text playground** (under Test) from the sidebar
- Click **Select Model** and then *Anthropic* and then **Claude Haiku 4.5  v1**
- If you haven't used an Anthropic model before, you'll be asked to answer some questions on your 'use case'. Keep it brief, and just put your use case as 'Learning'.

There are also some pre-requisites you'll want on your machines. Note that we'll be setting everything up so you can deploy from Github

- Python + uv (I assume everyone has this already)
- Node - https://nodejs.org/ and copy and paste the instructions at the terminal (don't use pkg installer on macos)
- WSL2 for Windows users
- Docker https://www.docker.com/products/docker-desktop/ or Podman https://podman.io/
  - Windows users see https://docs.docker.com/desktop/features/wsl/ and check you can run containers
- AWS CLI - see  https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- AWS CDK - see https://docs.aws.amazon.com/cdk/v2/guide/getting-started.html

You'll need to configure AWS credentials to use the AWS CLI.
You can either configure IAM Identity Center or create an IAM user (see the CloudWolf guide mentioned above).
IAM Identity Center is overkill for the purposes of this course, so unless you already have it configured I suggest following the IAM user set up guide at https://docs.aws.amazon.com/cli/latest/userguide/cli-authentication-user.html
Please set `us-west-2` as your default region when running `aws configure`.

# Testing the environment

If you're running on Windows, run these commands under WSL2.
For Mac and Linux, use your normal terminal or install [ghostty](https://ghostty.org/) for a better experience.

## AWS

You can test your AWS session by running

```bash
aws sts get-caller-identity
```

If this returns a JSON object with a `UserId`, an `Account` and an `Arn`, your AWS credentials are correctly configured.

### Bedrock

Verify you have AWS Bedrock access by asking Claude Haiku a question:

```bash
aws bedrock-runtime converse --model-id global.anthropic.claude-haiku-4-5-20251001-v1:0 --messages '[{"role": "user", "content": [{"text": "Describe the purpose of a \"hello world\" program in one line."}]}]'
```


## CDK

```bash
cd week5/1-hello-world
uv run cdk bootstrap
```

This will create the base resources you need to use [AWS CDK](https://docs.aws.amazon.com/cdk/v2/guide/home.html)

---

# Background reading

All of this is optional, but will assist you in hitting the ground running.
I've ordered by importance.

1. [Getting started building your first serverless web application](https://www.youtube.com/watch?v=-WYBOuP1Y6E)
2. [Strands Agents SDK](https://strandsagents.com/latest/), in particular the [Agent Loop](https://strandsagents.com/latest/user-guide/concepts/agents/agent-loop/) and the Safety & Security section.
3. [AWS CDK Core concepts](https://docs.aws.amazon.com/cdk/v2/guide/core-concepts.html)
4. [What is AWS Lambda?](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
