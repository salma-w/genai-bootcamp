#!/usr/bin/env python3
import aws_cdk as cdk
from weather.stack import Weather

app = cdk.App()
_ = Weather(app, 'weather')
app.synth()
