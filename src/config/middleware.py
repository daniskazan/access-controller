import logging
import uuid

from django.db import connection

logger = logging.getLogger()

sql_times = []


class SqlPrintingMiddleware(object):
    """
    Middleware which prints out a list of all SQL queries done
    for each view that is processed.  This is only useful for debugging.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if len(connection.queries) > 0:
            tag = uuid.uuid4()
            logging.info(f"[{tag}] SQL PROFILER")
            total_time = 0.0
            total_queries = 0
            for counter, query in enumerate(connection.queries, start=1):
                nice_sql = query["sql"].replace('"', "").replace(",", ", ")
                sql = "\033[1;31m[%s]\033[0m %s" % (query["time"], nice_sql)
                total_time = total_time + float(query["time"])

                if counter <= 20:
                    logger.info(f"[{tag}] {sql}\n")
                total_queries = counter

            sql_times.append(total_time)
            logger.info(
                f"[{tag}] \033[1;32m["
                f"TOTAL TIME: {total_time} seconds, QUERIES: {total_queries}"
                f"]\033[0m"
            )
            logger.info(f"\033[1;32m[{sql_times}]\033[0m")
            logger.info(
                f"\033[1;32mCount: {len(sql_times)}. Average = {sum(sql_times)/len(sql_times)}\033[0m"
            )
        return response
