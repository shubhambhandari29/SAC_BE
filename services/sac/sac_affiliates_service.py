from db import conn
import pandas as pd
from fastapi import HTTPException
import logging
 
logger = logging.getLogger(__name__)
 
async def get_affiliates(query_params: dict):
    """
    Fetch account(s) from tblAffiliates.
    If query_params is provided, filters by given key/value.
    Returns a list of dicts (records).
    """
 
    try:
        base_query = "SELECT * FROM tblAffiliates"
        filters = []
        params = []
        for key, value in query_params.items():
            filters.append(f"{key} = ?")
            params.append(value)
        where_clause = " WHERE " + " AND ".join(filters)
        query = base_query + where_clause
 
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
        logger.warning(f"Error fetching Loss Run frequency List - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})
   
 
async def upsert_affiliates(data_list):
    """
    Takes an array of maps as data
    Update row if already exists, else insert row into tblAffiliates
    """
 
    try:
        cursor = conn.cursor()
 
        for data in data_list:
            # print('**********************************', data)
            if 'PK_Number' not in data:
                data['PK_Number'] = None
            non_identity_cols = [col for col in data.keys() if col != 'PK_Number']
 
            # Assuming PK_Number is the primary key / unique identifier
            merge_query = f"""
            MERGE INTO tblAffiliates AS target
            USING (SELECT {", ".join(['? AS ' + col for col in data.keys()])}) AS source
            ON target.PK_Number = source.PK_Number
            WHEN MATCHED THEN
                UPDATE SET {", ".join([f"{col} = source.{col}" for col in non_identity_cols if col != 'PK_Number'])}
            WHEN NOT MATCHED THEN
                INSERT ({", ".join(non_identity_cols)})
                VALUES ({", ".join(['source.' + col for col in non_identity_cols])});
            """
 
            # print('**********************************', merge_query)
            values = list(data.values())
            cursor.execute(merge_query, values)
 
        conn.commit()
        return {"message": "Transaction successful", "count": len(data_list)}
    except Exception as e:
        conn.rollback()
        logger.warning(f"Insert/Update failed - {str(e)}")
        raise HTTPException(status_code=500, detail={"error": str(e)})