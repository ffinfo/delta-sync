import tempfile

import pytest
from delta import configure_spark_with_delta_pip
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark_warehouse_dir():
    return tempfile.mkdtemp()


@pytest.fixture(scope="session")
def spark(spark_warehouse_dir: str) -> SparkSession:

    builder = (
        SparkSession.builder.config("spark.driver.memory", "2g")
        .config("spark.sql.autoBroadcastJoinThreshold", -1)
        .config("spark.sql.shuffle.partitions", "1")  # increase test speed
        .config("spark.default.parallelism", 1)  # increase test speed
        .config("spark.rdd.compress", False)  # increase test speed
        .config("spark.shuffle.compress", False)  # increase test speed
        .config("spark.sql.session.timeZone", "UTC")
        .config("spark.driver.extraJavaOptions", "-Duser.timezone=GMT")
        .config("spark.executor.extraJavaOptions", "-Duser.timezone=GMT")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.warehouse.dir", spark_warehouse_dir)
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
    )
    return configure_spark_with_delta_pip(builder).getOrCreate()


@pytest.fixture
def empty_spark_warehouse(spark: SparkSession):
    for db in spark.catalog.listDatabases():
        for table in spark.catalog.listTables(db.name):
            if not table.isTemporary:
                spark.sql(f"DROP TABLE {table.database}.{table.name}")
