#!/usr/bin/env python3
import os

import aws_cdk as cdk

from hello_world.stack import HelloWorld

# We are hardcoding us-west-2 because not all regions offer Bedrock, and model names are region-specific.
env = {"region": os.environ.get("CDK_DEFAULT_REGION", "us-west-2"), "account": os.environ.get("CDK_DEFAULT_ACCOUNT")}

app = cdk.App()
_ = HelloWorld(app, "HelloWorldStack", env=env)

app.synth()
