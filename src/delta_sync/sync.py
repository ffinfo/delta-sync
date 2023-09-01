from typing import Optional, Tuple

from delta.tables import DeltaTable
from pyspark.sql import SparkSession
from pyspark.sql import functions as sf


def _get_output_table(
    source_table: DeltaTable,
    name: Optional[str] = None,
    path: Optional[str] = None,
    spark: Optional[SparkSession] = None,
) -> Tuple[DeltaTable, str]:
    if name is None and path is None:
        raise AttributeError("output_table_name or output_table_path should be given")
    elif name is not None and path is not None:
        raise AttributeError("output_table_name and output_table_path can not be given both")
    elif name is not None:
        builder = DeltaTable.createIfNotExists(sparkSession=spark).tableName(name)
        table_id = name
    else:
        builder = DeltaTable.createIfNotExists(sparkSession=spark).location(path)
        table_id = path
    partition_columns = source_table.detail().first()["partitionColumns"] or []
    builder = builder.addColumns(source_table.toDF().schema).partitionedBy(*partition_columns)
    return builder.execute(), table_id


def _full_sync(
    source_table: DeltaTable,
    status_table: DeltaTable,
    name: Optional[str] = None,
    path: Optional[str] = None,
    spark: Optional[SparkSession] = None,
):
    if spark is None:
        spark = SparkSession.getActiveSession()
    writer = source_table.toDF().write.format("delta").mode("overwrite")
    if name is not None:
        writer.saveAsTable(name)
    else:
        writer.save(path)
    current_status = source_table.history().sort(sf.col("version").desc()).first()
    detail = source_table.detail().first()
    status_line = spark.createDataFrame(
        [
            {
                "source_table": detail["name"] or detail["location"],
                "output_table": name or path,
                "source_version": current_status["version"],
                "source_timestamp": current_status["timestamp"],
            }
        ]
    )
    status_table.alias("status").merge(
        status_line.alias("updates"), "updates.output_table = status.output_table"
    ).whenNotMatchedInsertAll().execute()


def sync_table(
    source_table: DeltaTable,
    status_table: DeltaTable,
    output_table_name: Optional[str] = None,
    output_table_path: Optional[str] = None,
    spark: Optional[SparkSession] = None,
):
    """
    This will sync 2 tables based on the history of the source table
    :param source_table: Source of the data
    :param output_table: Table to write update to
    :param status_table: Table to store the status of the sync
    """
    output_table, table_id = _get_output_table(source_table, output_table_name, output_table_path, spark)
    status_lines = status_table.toDF().filter(f"output_table = '{table_id}'").first()
    if status_lines is None:
        # new sync table
        _full_sync(source_table, status_table, name=output_table_name, path=output_table_path)
    else:
        raise NotImplementedError
