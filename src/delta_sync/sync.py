from delta.tables import DeltaTable


def sync_table(source_table: DeltaTable, output_table: DeltaTable, status_table: DeltaTable):
    """
    This will sync 2 tables based on the history of the source table
    :param source_table: Source of the data
    :param output_table: Table to write update to
    :param status_table: Table to store the status of the sync
    """
    raise NotImplementedError
