import boto3
from datetime import date, datetime
import dateutil.relativedelta
import locale
from prettytable import PrettyTable

# Regular monthly report is 1 month and should run shortly after month-end
MONTH_COUNT = 1
GRANULARITY_MODE = 'MONTHLY'
# For a one-off report could extend this out to 12 months or whatever is needed

# Could also be switched to run a daily (e.g., month-to-date) view
# MONTH_COUNT = 0
# GRANULARITY_MODE = 'DAILY'

# Info: https://docs.aws.amazon.com/cost-management/latest/userguide/ce-advanced.html
# Amortized cost reporting is best when there are pre-payment amounts (e.g., for Reserved Instances).
# Otherwise, you get a cashflow-based view which is not helpful for cost allocation where you'd
# prefer to assign the cost when you know what the service was used for
COST_METRIC = 'AmortizedCost'

# For this purpose, we split by regions but lots of options of course
GROUP_BY_TYPE = [{'Type': 'DIMENSION', 'Key': 'REGION'}]

# For currency formatting
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
FLOAT_FORMATTER = "{:.2f}"

# AWS API client
client = boto3.client('ce')

# Cost driver types
TYPE_FIXED = 'Fixed'
TYPE_VARIABLE = 'Variable'
TYPE_FIXED_AND_VARIABLE = 'F_V'

if MONTH_COUNT > 0:
  end_date = date.today().replace(day=1)
  start_date = end_date - dateutil.relativedelta.relativedelta(months=MONTH_COUNT)
else:
  end_date = date.today()
  start_date = end_date.replace(day=1)

# Expect for monthly to see the start of the previous month and start of the current month
# The end date is exclusive, so this is intentional
print(start_date)
print(end_date)

# Final output rows
rows = []

# Data maps for tracking results
total_tracking = {}
adjustment_tracking = {}

#####################


def process_result(response, series_name, category, is_total, is_sum_of_fixed_var, is_requires_scale_up):
  for info in response['ResultsByTime']:
    if GRANULARITY_MODE == 'MONTHLY':
      result_date = datetime.strptime(
        info['TimePeriod']['Start'], "%Y-%m-%d"
      ).strftime("%Y-%m")
    elif GRANULARITY_MODE == 'DAILY':
      result_date = datetime.strptime(
        info['TimePeriod']['Start'], "%Y-%m-%d"
      ).strftime("%Y-%m-%d")

    running_total_this = {
      "Other": 0,
      "Japan": 0,
      "USA": 0,
      "Australia": 0
    }

    for rr in info['Groups']:
      region_id = rr['Keys'][0]
      region_name = regionLookup.get(region_id, region_id)
      region_cost = float(rr['Metrics'][COST_METRIC]['Amount'])
      running_total_this[region_name] = running_total_this.get(region_name, 0) + region_cost

    for region_name, region_cost in running_total_this.items():
      adjusted_cost = region_cost
      multiplier_this = 1
      if is_total:
        map_for_date = total_tracking.get(result_date, {})
        map_for_date[region_name] = region_cost
        total_tracking[result_date] = map_for_date
      elif is_sum_of_fixed_var:
        total_cost_this = total_tracking.get(result_date, {}).get(region_name, 0)
        multiplier_this = total_cost_this / region_cost if region_cost != 0 else 1
        map_for_date = adjustment_tracking.get(result_date, {})
        map_for_date[region_name] = multiplier_this
        adjustment_tracking[result_date] = map_for_date
        adjusted_cost = region_cost * multiplier_this
      elif is_requires_scale_up:
        multiplier_this = adjustment_tracking.get(result_date, {}).get(region_name, 1)
        adjusted_cost = region_cost * multiplier_this

      if not is_sum_of_fixed_var:
        rows.append([
          result_date, series_name, category, region_name,
          FLOAT_FORMATTER.format(region_cost),
          FLOAT_FORMATTER.format(adjusted_cost),
          multiplier_this
        ])


#####################


def fetch_and_process(filter_param, series_name, category, is_total, is_sum_of_fixed_var, is_requires_scale_up):
  response = client.get_cost_and_usage(
    TimePeriod={
      'Start': start_date.strftime("%Y-%m-%d"),
      'End': end_date.strftime("%Y-%m-%d")
    },
    Granularity=GRANULARITY_MODE,
    Metrics=[COST_METRIC],
    GroupBy=GROUP_BY_TYPE,
    Filter=filter_param
  )
  process_result(response, series_name, category, is_total, is_sum_of_fixed_var, is_requires_scale_up)


#####################

# Phase 1: Get the total cost (ex tax)
fetch_and_process(filter_ex_tax, 'Total', 'Total', True, False, False)

# Phase 2: Get the cost we have allocated so we can work out the gap that should be accounted for
fetch_and_process(filter_fixed_variable, '', TYPE_FIXED_AND_VARIABLE, False, True, False)
fetch_and_process(filter_variable, 'VARIABLE', TYPE_VARIABLE, False, False, True)
fetch_and_process(filter_fixed, 'FIXED', TYPE_FIXED, False, False, True)

# Phase 3: Run cost checks for each of the categories & then also "mark up" the gap so it still sums to the total
fetch_and_process(filter_services_Data_Processing, 'Data processing', TYPE_VARIABLE, False, False, False)
fetch_and_process(filter_services_Analysis, 'Analysis', TYPE_VARIABLE, False, False, False)
fetch_and_process(filter_services_DataWarehouse2, 'Data Warehouse', TYPE_FIXED, False, False, False)
fetch_and_process(filter_services_Workloads, 'Workloads', TYPE_FIXED, False, False, False)
fetch_and_process(filter_services_AppStorage, 'App Storage', TYPE_FIXED, False, False, False)
fetch_and_process(filter_services_Storage, 'Data Storage', TYPE_FIXED, False, False, False)

#####################

CONST_COL_HEADER = ['Date', 'Use', 'Category', 'Region', 'Raw', 'Amount', 'Multiplier']

result_table = PrettyTable()
result_table.field_names = CONST_COL_HEADER
result_table.add_rows(rows)
print(result_table.get_csv_string())
