import pyodbc
# import pandas as pd

# Parameters
# server = "devucepipclaimsanalytics.database.windows.net"
# database = "dev_ucep_ip_claims_analytics"
# username = "SqlAdminUser"
# password = "Admin@2025"

# Connection string for EXL sandbox
# conn_str = (
#     "DRIVER={SQL Server};"
#     f"SERVER={server};"
#     f"DATABASE={database};"
#     f"UID={username};"
#     f"PWD={password}"
# )

# Connection string for Hanover Preprod
conn_str = (
    "Driver={ODBC Driver 17 for SQL Server};"
    "Server=clms-preprd-sqlmanagedinstance.3b98dc354c37.database.windows.net;"
    "Database=CLMAA_SpecialAccounts;"
    "Authentication=ActiveDirectoryIntegrated;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
)

# Connect to SQL Server
conn = pyodbc.connect(conn_str)

# Read only the specific table
# query = "SELECT * FROM dbo.tblUsers"
# df_tblAcctSpecial = pd.read_sql(query, conn)

# # Close connection
# conn.close()

# # Show first few rows
# print(df_tblAcctSpecial.head())