from pprint import pprint


def skip_logs_from_certain_modules(record):
    modules_to_skip = {
        'celery.app.trace',
        'celery.apps.worker',
        'celery.beat',
        'celery.worker.consumer.connection',
        'celery.worker.consumer.mingle',
        'celery.worker.strategy',
    }

    if record.name in modules_to_skip:
        return False
    else:
        pprint(vars(record))

        return True
