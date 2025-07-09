#!/usr/bin/env python3
import os

import aws_cdk as cdk

from csbot.stack import CSBot


env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'), region='us-west-2')
app = cdk.App()
_ = CSBot(app, "CSBot", env=env)
app.synth()
