# AWS Scripts

### [AWS: Cost Reporter](cost-reporter.py)
A simple pattern for extracting cost information from AWS using the [boto3 SDK](https://aws.amazon.com/sdk-for-python/).

The [AWS Cost explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) is extremely useful for ad hoc cost reporting but it has limitations for ongoing cost tracking.

- There is limited history in Cost Explorer.  This [has been extended recently](https://aws.amazon.com/about-aws/whats-new/2023/11/aws-cost-explorer-provides-historical-granular-data/) but is still limited. By extracting the data yourself you can manage it within your own control.

- The filters & grouping capabilities of the Cost Explorer UI are powerful, but lack the ability to be combined (using boolean logic) for more advanced tracking.  When using the API and simple object modelling this is quite easy to achieve.

## General Comments on AWS Cost Tracking

1. Use AWS accounts to delineate cost centres as much as possible.  Being able to filter by account is a full-proof separator that will capture all costs.

2. Invariably tagging & tracking services by name will locate most but not all of the cost in your bill. The gaps will be hard to allocate and where you aren't using a multi-account approach as in point (1) these will be present.

3. Each business will have different requirements for how to track cost.  In this example the [filters](cost_filters.py) define the type of activity, and then each activity type is tagged as either a fixed or variable cost.

    **Fixed**: can change over time but are correlated to more stable cost drivers that are 
               mostly continuous regardless of what the team are working on that month 
               (e.g. storage & server capacity)
  
    **Variable**: costs are more highly correlated to the activity of the team (e.g. ad hoc analysis).  In theory
               if no one worked in that time period the costs would be zero



## How to use the script
- The goal 
