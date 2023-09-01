from typing import Optional

from delta import DeltaTable
from delta.tables import DeltaTableBuilder
from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, StringType, TimestampType


def _get_or_create_status_table(builder: DeltaTableBuilder) -> DeltaTable:
    return (
        builder.addColumn("source_table", StringType())
        .addColumn("output_table", StringType())
        .addColumn("source_version", IntegerType())
        .addColumn("source_timestamp", TimestampType())
        .partitionedBy("output_table")
        .execute()
    )


def get_or_create_status_by_name(name: str = "delta_sync_status", spark: Optional[SparkSession] = None) -> DeltaTable:
    builder = DeltaTable.createIfNotExists(sparkSession=spark).tableName(name)
    return _get_or_create_status_table(builder)


def get_or_create_status_by_path(path: str, spark: Optional[SparkSession] = None) -> DeltaTable:
    builder = DeltaTable.createIfNotExists(sparkSession=spark).location(path)
    return _get_or_create_status_table(builder)
