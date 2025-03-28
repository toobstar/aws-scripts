from filters_fixed_var import *
import boto3
from datetime import *
import dateutil.relativedelta
import locale
from prettytable import PrettyTable

# Regular monthly report is 1 month and should run shortly after month-end
month_count = 1
granularityMode = 'MONTHLY'
# For a one-off report could extend this out to 12 months or whatever is needed 

# Could also be switched to run a daily (e.g month to date) view
# month_count = 0
# granularityMode = 'DAILY'

# Info : https://docs.aws.amazon.com/cost-management/latest/userguide/ce-advanced.html
# Amortized cost reporting is best when there are pre-payment amounts (e.g. for Reserved Instances).  
# Otherwise you get a cashflow based view which is not helpful for cost allocation where you'd 
# prefer to assign the cost when you know what the service was used for
cost_metric = 'AmortizedCost'

# For this purpose we split by regions but lots of options of course 
group_by_type = [{'Type':'DIMENSION','Key':'REGION'}]

# For currency formatting
locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
floatFormatter = "{:.2f}"

# AWS Api client
client = boto3.client('ce')

# This is an internal model of fixed/variable cost drivers that was negotiated with the finance team
# Fixed: can change over time but are correlated to more stable cost drivers that are 
#        mostly continuous regardless of what the team are working on that month 
#        (e.g. storage & server capacity)
#
# Variable: costs are more highly correlated to the activity of the team (e.g. ad hoc analysis).  In theory
#           if no one worked in that time period the costs would be zero
#
typeFixed = 'Fixed'
typeVariable = 'Variable'
typeFixedAndVariable = 'F_V'

if month_count > 0:
    end_date = date.today().replace(day=1)
    start_date = end_date.replace(day=1) - dateutil.relativedelta.relativedelta(months=month_count)
    
else:
    end_date = date.today()
    start_date = end_date.replace(day=1)
    
# Expect for monthly to see the start of previous month and start of current month
# The end date is exclusive so this is intentional    
print(start_date)
print(end_date)

# Final output rows
rows = []

### The Various data maps that we keep track of as we loop through the results

# Map: date > region > cost
totalTracking = {}

# Map: date > region > multiplier
adjustmentTracking = {}

# Map: date > gap
otherTracking = {}

#####################

def processResult(response, seriesName, category, isTotal, isSumOfFixedVar, isRequiresScaleUp):
    
    for info in response['ResultsByTime']:
        if (granularityMode == 'MONTHLY'):
            resultDate = datetime.strptime(info['TimePeriod']['Start'], "%Y-%m-%d").strftime("%Y-%m")        
        if (granularityMode == 'DAILY'):
            resultDate = datetime.strptime(info['TimePeriod']['Start'], "%Y-%m-%d").strftime("%Y-%m-%d") 
        
        runningTotalThis = {}
        # Ensure there is an entry for every region because zero values will be skipped in API result
        runningTotalThis["Other"] = 0 
        runningTotalThis["Japan"] = 0
        runningTotalThis["USA"] = 0
        runningTotalThis["Australia"] = 0

        for rr in info['Groups']:                                    
            region_id = rr['Keys'][0]
            
            region_name = regionLookup.get(region_id, region_id)            
            rtThisRegion = runningTotalThis.get(region_name, 0)
            region_cost = float(rr['Metrics'][cost_metric]['Amount'])
            region_cost = region_cost
            rtThisRegion += region_cost
            runningTotalThis[region_name] = rtThisRegion

        for region_name, region_cost in runningTotalThis.items():
            adjustedCost = region_cost
            multiplierThis = 1
            if (isTotal):
                mapForDate = totalTracking.get(resultDate, {})
                mapForDate[region_name] = region_cost
                totalTracking[resultDate] = mapForDate
                # print('total:', seriesName, resultDate, region_name, region_cost)
            elif (isSumOfFixedVar):
                # this is needed to subtract from the total in initial loop to work out how to scale up for full amount 
                # only the Fixed-Variable splits are scaled up to the full amount 
                totalCostThis = totalTracking.get(resultDate).get(region_name)                
                multiplierThis = totalCostThis / region_cost
                mapForDate = adjustmentTracking.get(resultDate, {})
                mapForDate[region_name] = multiplierThis
                adjustmentTracking[resultDate] = mapForDate
                adjustedCost = region_cost * multiplierThis
            elif (isRequiresScaleUp):
                multiplierThis = adjustmentTracking[resultDate][region_name]
                adjustedCost = region_cost * multiplierThis 

            if (not isSumOfFixedVar):
                rows.append([resultDate, seriesName, category, region_name, floatFormatter.format(region_cost), floatFormatter.format(adjustedCost), multiplierThis])


#####################

def fetch_and_process(filter_param, series_name, category, is_total, is_sum_of_fixed_var, is_requires_scale_up):    
    response = client.get_cost_and_usage(
        TimePeriod={'Start': start_date.strftime("%Y-%m-%d"), 'End': end_date.strftime("%Y-%m-%d")},
        Granularity=granularityMode,
        Metrics=[cost_metric],
        GroupBy=group_by_type,
        Filter=filter_param
    )
    processResult(response, series_name, category, is_total, is_sum_of_fixed_var, is_requires_scale_up)

#####################

# Phase 1: get the total cost (ex tax)
fetch_and_process(filter_ex_tax, 'Total', 'Total', True, False, False)

# Phase 2: Get the cost we have allocated so we can work out the gap that should be accounted for
fetch_and_process(filter_fixed_variable, '', typeFixedAndVariable, False, True, False)
fetch_and_process(filter_variable, 'VARIABLE', typeVariable, False, False, True)
fetch_and_process(filter_fixed, 'FIXED', typeFixed, False, False, True)

# Phase 3: Run cost checks for each of the categories & then also "mark up" the gap so it still sums to the total
fetch_and_process(filter_services_Data_Processing, 'Data processing', typeVariable, False, False, False)
fetch_and_process(filter_services_Analysis, 'Analysis', typeVariable, False, False, False)
fetch_and_process(filter_services_DataWarehouse2, 'Data Warehouse', typeFixed, False, False, False)
fetch_and_process(filter_services_Workloads, 'Workloads', typeFixed, False, False, False)
fetch_and_process(filter_services_AppStorage, 'App Storage', typeFixed, False, False, False)
fetch_and_process(filter_services_Storage, 'Data Storage', typeFixed, False, False, False)

#####################

CONST_COL_HEADER = ['Date', 'Use', 'Category', 'Region', 'Raw', 'Amount', 'Multiplier']

resultTable = PrettyTable()
resultTable.field_names = CONST_COL_HEADER
resultTable.add_rows(rows)
print(resultTable.get_csv_string())
