# pulumi_tut
Pulumi tutorial apps

### my-first-app
A simple webstore application using mongodb
#### Lessons learned:
- How to install Pulumi and initialize a new project
- How to add resource providers via the CLI
- How to create containers with Pulumi
- How to configure environment variables via Pulumi CLI and Pulumi.{stack}.yaml
- How to provision infrastructure using 'pulumi preview' and 'pulumi up'
- How to inspect deployment diffs in app.pulumi.com
- How to properly destroy resources
***

### my-second-app
A simple application that uses stack references to configure a new project
#### Lessons learned:
- How to create and switch between stacks via CLI
- How to utilize stack outputs (exporting and viewing)
- How to store and utilize encrypted secrets within a project
- How to utilize stack references to create a new project
***

### my-third-app
A simple project to create S3 buckets, define policies, and assign those policies to the related buckets
#### Lessons learned:
- How to use Python classes to provision resources
- How to use Pulumi's Component Resources to provision resources in a cleaner manner:    
``` python
bucket1 = OurBucketComponent('jnash-bucket-1', 'default')
bucket1.set_policy()
```
