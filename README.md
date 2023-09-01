# Delta Sync

**This package is not ready to use, still in development**

This package will contain methods to sync delta table. It will use


### Example

```python
from delta import DeltaTable

from delta_sync.sync import sync_table

source_table = DeltaTable.forName("<source table name>")
output_table = DeltaTable.forPath("<output table name>")
status_table = DeltaTable.forPath("<status table name>")

sync_table(source_table, output_table, status_table)
```


### Install

##### pip
```shell
pip install delta-sync
```

##### poetry
```shell
poetry add delta-sync
```
