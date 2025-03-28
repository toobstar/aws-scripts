# Internal region lookup
regionLookup = {
    'NoRegion': 'Other',
    'global': 'Other',
    'af-south-1': 'Other',     # South Africa
    'me-south-1': 'Other',     # Bahrain
    'ap-northeast-1': 'Japan',
    'ap-southeast-1': 'Australia',
    'ap-southeast-2': 'Australia',
    'ap-southeast-3': 'Australia',
    'ap-southeast-4': 'Australia', #Melb
    'eu-west-2': 'UK',    
    'us-east-1': 'USA',
    'us-west-2': 'USA',
    'ap-south-1': 'Other',     # India
    'us-east-2': 'USA',
    'us-west-1': 'USA',
    'ap-northeast-2': 'Other', # Korea
    'ap-northeast-3': 'Japan',
    'ca-central-1': 'Other',   # Canada
    'eu-central-1': 'Other',   # Europe
    'eu-north-1': 'Other',     # Europe
    'eu-west-1': 'Other',      # Ireland
    'eu-west-3': 'Other',      # Paris
    'sa-east-1': 'Other',      # Brazil
}

#####################

# note: tax appears with region = "no region"
filter_ex_tax = {
    'Not': {
        'Dimensions': {
            'Key': 'SERVICE',            
            'Values': ['Tax'],
            'MatchOptions': ['EQUALS']}                              
    }                           
}

#####################


filter_services_Analysis1 = {                
    'Dimensions': {
    'Key': 'SERVICE',            
    'Values': ['Amazon Athena', 'Amazon WorkSpaces'],
    'MatchOptions': ['EQUALS']}                                          
}

filter_services_Analysis_Databricks = {
    'Tags': {
        'Key': 'Vendor',
        'Values': ['Databricks'],
        'MatchOptions': ['EQUALS']
    }                                
}

filter_services_Analysis = {
   'Or':[filter_services_Analysis1, filter_services_Analysis_Databricks],        
}

#####################

filter_services_Data_Processing2 = {                
    'Dimensions': {
    'Key': 'SERVICE',            
    'Values': ['AWS Glue'],
    'MatchOptions': ['EQUALS']}                                          
}

filter_services_Data_Processing = {
   'Or':[filter_services_Data_Processing1, filter_services_Data_Processing2],        
}


#####################

filter_variable = {
   'Or':[filter_services_Data_Processing, filter_services_Analysis],        
}

#####################

filter_services_DataWarehouse1 = {                
    'Dimensions': {
    'Key': 'SERVICE',            
    'Values': ['Amazon OpenSearch Service'],
    'MatchOptions': ['EQUALS']}                                          
}

filter_services_DataWarehouse2 = {                
    'Dimensions': {
    'Key': 'PLATFORM',            
    'Values': ['Red Hat Enterprise Linux'],
    'MatchOptions': ['EQUALS']}                                          
}

filter_services_DataWarehouse3 = {
    'Tags': {
        'Key': 'Purpose',
        'Values': ['ClickHouse'],
        'MatchOptions': ['EQUALS']
    }   
}

filter_services_DataWarehouse = {
   'Or':[filter_services_DataWarehouse1, filter_services_DataWarehouse2, filter_services_DataWarehouse3],        
}

#####################

filter_services_Workloads1 = {                
    'Dimensions': {
    'Key': 'SERVICE',            
    'Values': ['Amazon Elastic Compute Cloud - Compute', 
               'Amazon EC2 Container Registry (ECR)',
               'EC2 - Other', 
               'Amazon Elastic Load Balancing',
               'Amazon ElastiCache',
               'Amazon Elastic Container Service', 
               'Amazon Elastic Container Service for Kubernetes'],
    'MatchOptions': ['EQUALS']}                                          
}

# Exclude Databricks related ec2
filter_services_Workloads2 = {
    'Not': {
        'Tags': {
            'Key': 'Vendor',
            'Values': ['Databricks'],
            'MatchOptions': ['EQUALS']
        }                                
    }                           
}

filter_services_Workloads5 = {
    'Not': filter_services_DataWarehouse3                    
}

filter_services_Workloads = {
   'And':[filter_services_Workloads1, filter_services_Workloads2, filter_services_Workloads3, filter_services_Workloads4, filter_services_Workloads5],        
}

#####################

filter_services_AppStorage = {                
    'Dimensions': {
    'Key': 'SERVICE',            
    'Values': ['Amazon Relational Database Service', 'Amazon DynamoDB'],
    'MatchOptions': ['EQUALS']}                                          
}

#####################

filter_services_Storage = {                
    'Dimensions': {
    'Key': 'SERVICE',            
    'Values': ['Amazon Simple Storage Service'],
    'MatchOptions': ['EQUALS']}                                          
}

#####################

filter_fixed = {
   'Or':[filter_services_Storage, filter_services_AppStorage, filter_services_Workloads, filter_services_DataWarehouse2],        
}

#####################

filter_fixed_variable = {
   'Or':[filter_fixed, filter_variable],        
}

#####################

filter_services_Other = {
    'Not': {
        'Or':[filter_services_Storage, 
              filter_services_Analysis, 
              filter_services_Data_Processing, 
              filter_services_AppStorage, 
              filter_services_Workloads,
              filter_services_DataWarehouse] 
    }                              
}
