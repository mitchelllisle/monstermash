# Usage

1. [Creating a database config object](#creating-a-database-config-object)
2. [Reading data using the async generator method `read`](#reading-data-using-the-async-generator-method-read)
3. [Reading all results using `read_all`](#reading-all-results-using-read_all)

## Creating a database config object 
There are three config objects provided for connecting to a database. We use [Pydantic's 
`BaseSettings`](https://pydantic-docs.helpmanual.io/usage/settings/) for this since it already has
excellent functionality for reading values from the environment as well as being able to override 
them or provide defaults when necessary. 

 - `DatabaseConfig`: A parent class providing common fields such as host, port, username and password
 - `MySQLConfig`: A MySQL specific config
 - `PostgresConfig`: A Postgres specific config



---

!!! note 
    The following examples will all use the Postgres variants of the library. All examples will work
    for MySQL as well. Simply import the MySQL objects instead.

## Sourcing config values from the environment

Assuming you have an environment with the following variables
```shell
export HOST=localhost
export USER=admin
export PASSWORD=admin
export DATABASE=yessql
```

Then, creating a config object is as simple as 
```python
from yessql import PostgresConfig

config = PostgresConfig() # (1)
```

1. This config object provides a default port of 5432 but can be overridden by your environment if necessary


You can also provide values directly 
```python
from yessql import PostgresConfig

config = PostgresConfig(host="127.0.0.1")
```

Or extend them with more information 
```python
from yessql import PostgresConfig

class MyPGConfig(PostgresConfig):
    table: str

config = MyPGConfig(table="my_table")
```

---

## Reading data using the async generator method `read`
When reading data from a database you often will query for large datasets. Loading an entire table or
query results into memory is not ideal. For these situations the `read` method is useful as it is an async
generator. This means we yield each row one at a time without loading everything into memory.

```python
import asyncio
from yessql import AioPostgres, PostgresConfig

async def main():
    config = PostgresConfig(database="my_database")
    
    async with AioPostgres(config) as pg:
        async for row in pg.read("SELECT * FROM table"):
            print(row)


if __name__ == '__main__':
    asyncio.run(main())

```

## Reading all results using `read_all`
In cases where there isn't alot of data, or you need everything in memory to do some processing on an
entire query set / table - you can use the `read_all` method which will return a list of rows.

```python
import asyncio
from typing import List, Dict
from yessql import AioPostgres, PostgresConfig

async def main() -> List[Dict]:
    config = PostgresConfig(database="my_database")
    
    async with AioPostgres(config) as pg:
        data = pg.read_all("SELECT * FROM table")
        return data

if __name__ == '__main__':
    asyncio.run(main())
```