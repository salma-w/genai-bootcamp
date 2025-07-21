from constructs import Construct
from aws_cdk import Stack, aws_bedrock as bedrock

class Guardrails(Construct):
    airline_safety: bedrock.CfnGuardrail

    def __init__(self, scope: Construct, id: str) -> None:
        super().__init__(scope, id)

        topic_policy_config = bedrock.CfnGuardrail.TopicPolicyConfigProperty(
            topics_config=[bedrock.CfnGuardrail.TopicConfigProperty(
                name="Airline Safety",
                definition="Provide information about airline safety, including statistics and safety records, or details of specific incidents.",
                type="DENY",
                examples=[
                    "Which airlines have the worst safety records?",
                    "Tell me about the details of Flight 447 crash",
                    "What are the most dangerous airlines to fly with?",
                    "Can you provide statistics on airline accidents last year?"
                ],
            )],
            topics_tier_config=bedrock.CfnGuardrail.TopicsTierConfigProperty(tier_name="STANDARD")
        )
        self.airline_safety = bedrock.CfnGuardrail(
            self, "Guardrail",
            name="cs-bot-guardrail",
            topic_policy_config=topic_policy_config,
            blocked_input_messaging="I can't help with that topic.",
            blocked_outputs_messaging="I can't provide that information.",
            cross_region_config=bedrock.CfnGuardrail.GuardrailCrossRegionConfigProperty(
                guardrail_profile_arn=f"arn:aws:bedrock:{Stack.of(self).region}:{Stack.of(self).account}:guardrail-profile/us.guardrail.v1:0",
            ),
        )
    
