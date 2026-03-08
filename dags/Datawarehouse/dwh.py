from datawarehouse.data_utils import (
    get_conn_cursor,
    close_conn_cursor,
    create_schema,
    create_table,
    get_video_ids,
)
from datawarehouse.data_loading import load_data
from datawarehouse.data_modifications import insert_rows, update_rows, delete_rows
from datawarehouse.transformations import transform_data



import logging
from airflow.decorators import task

logger = logging.getLogger(__name__)
table = "yt_api"


@task
def staging_table():

    schema = "staging"
    conn, cur = None, None

    try:
        conn, cur = get_conn_cursor()

        YT_data = load_data()

        create_schema(schema)
        create_table(schema)

        table_ids = get_video_ids(cur, schema)

        for row in YT_data:
            if "videoId" not in row:
                logger.warning(f"Skipping bad row: {row}")
                continue

            if len(table_ids) == 0:
                insert_rows(cur, conn, schema, row)
            else:
                if row["videoId"] in table_ids:
                    update_rows(cur, conn, schema, row)
                else:
                    insert_rows(cur, conn, schema, row)

        ids_in_json = {row["videoId"] for row in YT_data if "videoId" in row}
        ids_to_delete = set(table_ids) - ids_in_json

        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)

        logger.info(f"{schema} table update completed")

    except Exception as e:
        logger.error(f"An error occurred during the update of {schema} table: {e}")
        raise

    finally:
        if conn and cur:
            close_conn_cursor(conn, cur)


@task
def core_table():

    schema = "core"

    conn, cur = None, None  # initialize connection and cursor variables to None to ensure they are defined in the scope of the try block and can be properly closed in the finally block, even if an error occurs before they are assigned a value.

    try:
        conn, cur = get_conn_cursor()

        create_schema(schema)
        create_table(schema)

        table_ids = get_video_ids(cur, schema)

        current_video_ids = set()  # to keep track of video IDs that are currently in the staging table, which will be used to determine which records in the core table need to be deleted because they are no longer present in the staging table (i.e., they have been removed from the latest API data).

        cur.execute(f"SELECT * FROM staging.{table};") # could be millions of data, se we could use batch in production, but for this project we can assume the data is not too large to handle in memory. We will read all rows from the staging table to compare with the core table and determine which records need to be inserted, updated,
        #or deleted in the core table based on the latest data in the staging table.
        rows = cur.fetchall()

        for row in rows:
           # as we iterate through each row in the staging table, 
           # we add the video ID to the current_video_ids set to keep track of which video IDs are present in the staging table. 
           # This allows us to later identify any records in the core table that have video IDs not present in the staging table and should be deleted from the core table.
            current_video_ids.add(row["Video_ID"]) 

            if len(table_ids) == 0:
                # if the core table is empty, we can simply transform and insert all 
                # rows from the staging table into the core table without 
                # needing to check for updates or deletions, 
                # since there are no existing records in the core table to 
                # compare against.
                transformed_row = transform_data(row)
                insert_rows(cur, conn, schema, transformed_row)

            else:
                # if the core table already has data, 
                # we need to check each row from the 
                # staging table against the existing records in the 
                # core table to determine whether to insert new records, 
                # update existing records, or delete records that are 
                # no longer present in the staging table.
                transformed_row = transform_data(row)

                if transformed_row["Video_ID"] in table_ids:

                    # if the video ID from the staging table is already present 
                    # in the core table, we will update the existing record 
                    # in the core table with the new data from the 
                    # staging table (after transformation). 
                    # This ensures that any changes in video metrics
                    #  or title are reflected in the core table for existing videos.
                    update_rows(cur, conn, schema, transformed_row)

                else:
                    # if the video ID from the staging table is not present 
                    # in the core table,
                    # we will insert it as a new record into the core table.
                    insert_rows(cur, conn, schema, transformed_row)

        ids_to_delete = set(table_ids) - current_video_ids

        if ids_to_delete:
            delete_rows(cur, conn, schema, ids_to_delete)

        logger.info(f"{schema} table update completed")

    except Exception as e:
        # Log any exceptions that occur
        logger.error(f"An error occurred during the update of {schema} table: {e}")
        raise e

    finally:
        # Ensure the connection and cursor are closed
        if conn and cur:
            close_conn_cursor(conn, cur)