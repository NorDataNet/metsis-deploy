# Drupal7

This container is used to set-up a demo istance of DRUPAL-7 which can use the available PostgreSQL container for its installation.
The service by default will use the following database settings:

```bash
      POSTGRES_DB: metsis_test
      POSTGRES_USER: metsis_user
      POSTGRES_PASSWORD: metsis_password
```
Note:
During the installation process, use `postgres` as hostname (which refers to the service network name used internally by the docker-compose environment)

Once the Drupal installation is complete, to test the Drupal module that consumes the Plotting API available from the FastAPI service, follow the [relative documentation](../volumes/drupal/sites/all/modules/metsis_ts_bokeh/README.md).