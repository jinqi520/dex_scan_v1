import sqlite3
from scan_util import scanutil
from time import sleep


# 该脚本作为第一步，用于持续保存新增的token合约
if __name__ == "__main__":
    cx = sqlite3.connect("./token.db")
    c = cx.cursor()
    tables = c.execute("select name from sqlite_master where type = 'table'").fetchall()
    if not tables:
        c.execute(
            '''CREATE TABLE token (ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, contract_address TEXT NOT NULL, chain TEXT NOT NULL, pair_index INT NOT NULL, done INT NOT NULL, pair_contract TEXT NOT NULL)''')
    eth_index = 0
    eth_tokens = c.execute(
        "select ID, contract_address, chain, pair_index, done from token where chain = 'eth' order by pair_index DESC").fetchone()
    if eth_tokens is not None:
        eth_index = eth_tokens[3] + 1
    c.close()
    cx.close()
    while True:
        try:
            eth_index = scanutil.scan_uniswap(eth_index)
        except Exception as e:
            print(e)
