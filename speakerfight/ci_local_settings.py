from django.db.backends.signals import connection_created


def enable_legacy_sqlite_alter_table(sender, connection, **kwargs):
    """Enable compatibility for old migrations using SQLite."""
    if connection.vendor == 'sqlite':
        connection.connection.execute(
            'PRAGMA legacy_alter_table = ON'
        )


connection_created.connect(
    enable_legacy_sqlite_alter_table,
    dispatch_uid='speakerfight_ci_enable_legacy_sqlite_alter_table',
)