from db import conn
import pandas as pd
from fastapi import HTTPException
import logging
import re
 
logger = logging.getLogger(__name__)
 
async def get_sac_account(query_params: dict):
    """
    Fetch account(s) from tblAcctSpecial.
    If query_params is provided, filters by given key/value.
    Returns a list of dicts (records).
    """
 
    try:
        base_query = "SELECT * FROM tblAcctSpecial"
        filters = []
        params = []
        for key, value in query_params.items():
            if key == 'BranchName':
                branch_terms = re.split(r'[ ,&]+', value)
                branch_terms = [term for term in branch_terms if term]
                if branch_terms:
                    term_conditions = []
                    for _ in branch_terms:
                        term_conditions.append("BranchName LIKE ?")
 
                    branch_filter_clause = "(" + " OR ".join(term_conditions) + ")"
                    filters.append(branch_filter_clause)
                   
                    for term in branch_terms:
                        params.append(f"{term}%")
            else:
                filters.append(f"{key} = ?")
                params.append(value)
 
        if filters:
            where_clause = " WHERE " + " AND ".join(filters)
            query = base_query + where_clause
        else:
            query = base_query
 
        df = pd.read_sql(query, conn, params=params)
       
        df = df.astype(object).where(pd.notna(df), None)   # replacing NaN with null
        result = df.to_dict(orient="records")
        return result
    except Exception as e:
        logger.warning(f"EError fetching SAC account List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
   
   
 
async def upsert_sac_account(data):
    """
    Update row if already exists, else insert row into tblAcctSpecial
    """
 
    try:
        cursor = conn.cursor()
 
        # Assuming `CustomerNum` is the primary key / unique identifier
        merge_query = f"""
        MERGE INTO tblAcctSpecial AS target
        USING (SELECT {", ".join(['? AS ' + col for col in data.keys()])}) AS source
        ON target.CustomerNum = source.CustomerNum
        WHEN MATCHED THEN
            UPDATE SET {", ".join([f"{col} = source.{col}" for col in data.keys() if col != 'CustomerNum'])}
        WHEN NOT MATCHED THEN
            INSERT ({", ".join(data.keys())})
            VALUES ({", ".join(['source.' + col for col in data.keys()])});
        """
 
        values = list(data.values())
        cursor.execute(merge_query, values)
        conn.commit()
 
        return {"message": "Transaction successful"}
    except Exception as e:
        conn.rollback()
        logger.warning(f"Insert/Update failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})