import threading
import sqlite3
from pocs import check_mint, check_burn, check_transfer


def checkIsVul(chain, contract_address, pair_contract):
    try:
        check_mint.checkMint(chain, contract_address, pair_contract)
        check_burn.checkBurn(chain, contract_address, pair_contract)
        check_transfer.checkTransfer(chain, contract_address, pair_contract)
    except Exception as e:
        print(e)


def get_token_to_scan(chain):
    while True:
        cx = sqlite3.connect("./token.db")
        c = cx.cursor()
        tokens = c.execute("select contract_address, pair_index from token where chain = '" + chain + "' and done = 0 limit 50").fetchall()
        for token_info in tokens:
            contract_address = token_info[0]
            pair_contract = token_info[5]
            checkIsVul(chain.lower(), contract_address, pair_contract)
            c.execute(
                "update token set done = 1 where contract_address = '" + contract_address + "' and chain = '" + chain + "'")
            cx.commit()
        c.close()
        cx.close()


if __name__ == "__main__":
    get_token_to_scan("eth")
    # t1 = threading.Thread(target=get_token_to_scan, args=("eth",))
    # t2 = threading.Thread(target=get_2_token_to_scan, args=("eth",))
    # t1.start()
    # t2.start()
    # get_2_token_to_scan("bsc")