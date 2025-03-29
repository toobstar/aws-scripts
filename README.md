# AWS Scripts

### [AWS: Cost Reporter](cost-reporter.py)
A simple pattern for extracting cost information from AWS using the [boto3 SDK](https://aws.amazon.com/sdk-for-python/).

The [AWS Cost explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) is extremely useful for ad hoc cost reporting but it has limitations for ongoing cost tracking.

- There is limited history in Cost Explorer.  This [has been extended recently](https://aws.amazon.com/about-aws/whats-new/2023/11/aws-cost-explorer-provides-historical-granular-data/) but is still limited. 
