import json
import pulumi
import pulumi_aws as aws
import pulumi_aws_native as aws_native

# Create a class that encapsulates the functionality while subclassing the ComponentResource class (using the ComponentResource class as a template).
class OurBucketComponent(pulumi.ComponentResource):
    def __init__(self, name_me, policy_name='default', opts=None):
        # By calling super(), we ensure any instantiation of this class inherits from the ComponentResource class so we don't have to declare all the same things all over again.
        super().__init__('pkg:index:OurBucketComponent', name_me, None, opts)
        # This definition ensures the new component resource acts like anything else in the Pulumi ecosystem when being called in code.
        child_opts = pulumi.ResourceOptions(parent=self)
        self.name_me = name_me
        self.policy_name = policy_name
        self.bucket = aws_native.s3.Bucket(f"{self.name_me}")
        self.policy_list = {
            'default': {
                'Effect': 'Allow',
                'Principal': {"AWS": "arn:aws:iam::241810645744:root"},
                'Action': ["s3:GetObject"],
            },
            'locked': {
                'Effect': 'Allow',
                # ...
            },
            'permissive': {
                'Effect': 'Allow',
                # ...
            },
        }

        # We also need to register all the expected outputs for this component resource that will get returned by default.
        self.register_outputs({
            "bucket_name": self.bucket.bucket_name
        })

    def define_policy(self):
        try:
            statement = self.policy_list[self.policy_name]

            def build_policy(bucket_arn):
                policy_doc = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            **statement,
                            "Resource": f"{bucket_arn}/*"
                        }
                    ]
                }
                return json.dumps(policy_doc)

            return self.bucket.arn.apply(build_policy)

        except KeyError:
            raise ValueError(
                "Policy name must be 'default', 'locked', or 'permissive'"
            )

    def set_policy(self):
        bucket_policy = aws.s3.BucketPolicy(
            f"{self.name_me}-policy",
            bucket=self.bucket.id,
            policy=self.define_policy(),
            opts=pulumi.ResourceOptions(parent=self.bucket)
        )
        return bucket_policy


bucket1 = OurBucketComponent('jnash-bucket-1', 'default')
bucket1.set_policy()

pulumi.export("bucket_name", bucket1.bucket.id) 