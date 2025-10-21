from neo4j import GraphDatabase


# 定义Neo4j连接池类
class Neo4jPool:
    _driver = None

    def __init__(self, url, user, password, database, pool_size=20):
        self.url = url
        self.user = user
        self.password = password
        self.database = database
        self.pool_size = pool_size

    # Neo4j驱动创建
    def create_driver(self):
        if self._driver is None:
            self._driver = GraphDatabase.driver(
                self.url,
                auth=(self.user, self.password),
                database=self.database,
                max_connection_pool_size=self.pool_size
            )
        return self._driver

    def close_driver(self):
        if self._driver is not None:
            self._driver.close()
