# PostgreSQL Partition Proof-of-Concept

This project is a sample implementation of a partitioned time-series database table using PostgreSQL's [partitions](https://www.postgresql.org/docs/current/ddl-partitioning.html).

This project's DB has one table `log` with the schema:

```sql
CREATE TABLE log (
    id SERIAL,
    created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    message TEXT NOT NULL
) PARTITION BY RANGE (created);
```

This project aggressively creates minute-level partitions for all record insertions (in the `log_YYYYMMDDhhmm` format), but queries the top-level collection `log` only. As records age out; older partitions can be dropped with the `DELETE /tables` endpoint, reducing `GET /log` retrieval sizes.

## Requirements

* Docker

## How to Run

In the project root, run `docker compose up -d`.

This brings up a server with 3 endpoints:

* `GET /logs` - Retrieve a list of log messages
* `GET /tables` - Retrive a list of all database tables
* `DELETE /tables` - Drop all tables but the youngest and the original `log` table
  * NOTE: All server activity appends to the `log` table; so it's possible a new partition is created immediately after dropping tables

### GET /logs Example

```shell
$ curl localhost:8080/logs
{
  "logs": [
    "2022-04-26 14:38:16 - Server started."
  ]
}
```

### GET /tables Example

```shell
$ curl localhost:8080/tables
{
  "tables": [
    "log",
    "log_202204261815"
  ]
}
```

### DELETE /tables Example

```shell
$ curl -X DELETE localhost:8080/tables
{
  "dropped_tables": [
    "log_202204261433",
    "log_202204261438"
  ]
}
```