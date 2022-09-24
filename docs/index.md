# Welcome to YesSQL

!!! caution
    This library is still in active development and is subject to change until we reach a stable
    version. Please report any bugs/issues/ideas or features to our [GitHub repo](https://github.com/mitchelllisle/yessql)

## What is YesSQL?
YesSQL is a Python database library that simplifies the way you connect to and interact with common
SQL databases.

## Why do we need another database library?
There are already some fantastic database libraries out there for Python. However I have always been 
disappointed by the amount of boiler plate that you have to write before you can start working with
data. This library aims to address a number of challenges in working with common SQL databases:

!!! info "Philosophy"
    - Reduce the amount of time and code I need to write before I can start working with my data 
    - Provide a common format and syntax for different databases 
    - Let me model my data and provide you the model so I know the data I'm getting is what I expect 
    - Provide me with async and non-async options

These are the principles I have adopted when writing this library. 

We try and keep a small footprint of dependencies. The main libraries we use are:

!!! info "Dependencies"
    - [Pydantic: An excellent data validation and modelling library](https://pydantic-docs.helpmanual.io/)
    - [aiomysql: An Async MySQL library](https://pydantic-docs.helpmanual.io/)
    - [asyncpg: An async Postgres library](https://magicstack.github.io/asyncpg/current/)
    - [pg8000: A non-async Postgres library](https://github.com/tlocke/pg8000)


## Just show me some code
Here is an example of the minimum you need to do before being able to access your data:

**Reading data**

```python
import asyncio
from yessql import AioPostgres, PostgresConfig # (1)

async def main():
    config = PostgresConfig(
        host="localhost",
        username="my_username",
        password="my_password",
        database="my_database"
    )
    
    async with AioPostgres(config) as pg:
        async for row in pg.read("SELECT * FROM table"):
            print(row)


if __name__ == '__main__':
    asyncio.run(main())

```

**Writing Data**

```python
import asyncio
from yessql import AioPostgres, PostgresConfig # (1)

async def main():
    config = PostgresConfig(
        host="localhost",
        username="my_username",
        password="my_password",
        database="my_database"
    )
    
    async with AioPostgres(config) as pg:
        await pg.write(
            stmt="INSERT INTO table (id, name) VALUES ($1, $2)",
            params=[("1", "john"), ("2", "paul")]
        )


if __name__ == '__main__':
    asyncio.run(main())
```


1. You can easily swap out the Postgres variants for MySQL or omit Aio for non-async variants

[Check out the examples page for more detail](https://mitchelllisle.github.io/yessql/examples/){ .md-button .md-button--primary }
