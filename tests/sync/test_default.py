from delta import DeltaTable
from pyspark.sql import SparkSession

from delta_sync import sync_table
from delta_sync.status import get_or_create_status_by_name


def test_init(spark: SparkSession, empty_spark_warehouse):
    status_table = get_or_create_status_by_name()
    spark.createDataFrame([["row1", "1"]], ["c1", "p"]).write.format("delta").partitionBy("p").saveAsTable("source")
    source_table = DeltaTable.forName(sparkSession=spark, tableOrViewName="source")

    sync_table(source_table=source_table, status_table=status_table, output_table_name="output")

    output_table = DeltaTable.forName(sparkSession=spark, tableOrViewName="output")

    assert source_table.toDF().collect() == output_table.toDF().collect()
    assert source_table.detail().first()["partitionColumns"] == output_table.detail().first()["partitionColumns"]
    assert source_table.toDF().schema == output_table.toDF().schema


# def test_append(spark: SparkSession, empty_spark_warehouse):
#     test_init(spark, empty_spark_warehouse)
#
#     spark.createDataFrame([["row2", "2"]], ["c1", "p"]).write.format("delta").mode("append").saveAsTable("source")
#
#     status_table = get_or_create_status_by_name()
#     source_table = DeltaTable.forName(sparkSession=spark, tableOrViewName="source")
#
#     sync_table(source_table=source_table, status_table=status_table, output_table_name="output")
#
#     output_table = DeltaTable.forName(sparkSession=spark, tableOrViewName="output")
#
#     assert source_table.toDF().collect() == output_table.toDF().collect()
