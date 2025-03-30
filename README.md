# AWS Scripts

## [AWS: Cost Reporter](cost-reporter.py)
A simple pattern for extracting cost information from AWS using the [boto3 SDK](https://aws.amazon.com/sdk-for-python/).  The [AWS Cost explorer](https://aws.amazon.com/aws-cost-management/aws-cost-explorer/) is extremely useful for ad hoc cost reporting but it has constraints for ongoing cost tracking.

- There is limited history in Cost Explorer although this [has been extended recently](https://aws.amazon.com/about-aws/whats-new/2023/11/aws-cost-explorer-provides-historical-granular-data/). By extracting the data yourself you can manage it fully.

- The filters & grouping capabilities of the Cost Explorer UI are powerful, but lack the ability to be combined (using boolean logic) for more advanced tracking.  When using the API and simple object modelling this is quite easy to achieve.

- The reporting and export to S3 capabilities of the Cost Explorer are tricky to work with.  Yes, there are [solutions that plug proper reporting platforms into this](https://grafana.com/grafana/dashboards/139-aws-billing/) but you need to be prepared for the effort to setup and maintain these. 

### General Comments on AWS Cost Tracking

1. Use AWS accounts to delineate cost centres as much as possible.  Being able to filter by account is a full-proof separator that will capture all costs.

2. Invariably tagging & tracking services by name will locate most but not all of the cost in your bill. The gaps will be hard to allocate and where you aren't using a multi-account approach as in point (1) these will be present.  This script attempts resolve that by firstly determining the total cost for the month.  After doing the filter based reporting, it then determines the gap to the total and uses that to scale up the results so they match.  This approach is not 100% correct obviously, but is a low effort solution, and based on the % adjustment you can decide whether it's acceptable.  Obviously tinkering with the filters can improve this outcome if that's needed. 

3. Each business will have different requirements for how to track cost.  In this example the [filters](cost_filters.py) define the type of activity, and then each activity type is tagged as either a fixed or variable cost.

    **Fixed**: can change over time but are correlated to more stable cost drivers that are 
               mostly continuous regardless of what the team are working on that month 
               (e.g. storage & server capacity)
  
    **Variable**: costs are more highly correlated to the activity of the team (e.g. ad hoc analysis).  In theory
               if no one worked in that time period the costs would be zero

4. By using a solution outside of AWS it's easier to merge with the cost of other vendors

### How to use the script

- Consider the right [filters](cost_filters.py) for your needs.  Some examples are included.  Also note that I've translated the AWS zones into friendly regional groupings that were appropriate for this. 
- The script is setup for monthly reporting to be run at the start of the next month.  You can work out when to run it because AWS will send the invoice as soon as they have closed out costs for the previous month or it could be scheduled with some buffer to ensure all costs have arrived.
- For an initial setup you would want to collect all history available so could extend the time period manually.
- The output is in a CSV format suitable for pushing to a spreadsheet.  This could be run in [Lambda](https://aws.amazon.com/lambda/) or from a point external to AWS.
- An approach that worked well for me is to then use this data-source in a BI Dashboard like [PowerBI](https://www.microsoft.com/en-us/power-platform/products/power-bi) or [Looker Studio](https://cloud.google.com/looker).
- In order to be able to run the script you need to [get credentials for API access in the environment that the Python script will run in](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-sso.html#sso-configure-profile-token-auto-sso).

```
export AWS_ACCESS_KEY_ID="??"
export AWS_SECRET_ACCESS_KEY="??"
export AWS_SESSION_TOKEN="??"
python cost-reporter.py
```
