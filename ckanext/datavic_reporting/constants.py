import os
class States:
    Active = "active"
    Deleted = "deleted"

class Frequencies:
    if os.getenv("LAGOON_GIT_SAFE_BRANCH") is 'master':
        Monthly = "monthly"
        Yearly = "yearly"
        List = [Monthly, Yearly]
    else:
        Hourly = "hourly"
        Daily = "daily"    
        List = [Hourly, Daily]  

class Statuses:
    Processing = "Processing"
    Generated = "Generated"
    EmailsSent = "Emails sent"
    NoEmails = "No emails sent"
    Failed = "Failed"