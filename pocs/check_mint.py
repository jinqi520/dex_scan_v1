import requests
from web3 import Web3
from eth_abi import encode_abi
from eth_utils import function_signature_to_4byte_selector
from time import sleep
from scan_util import scanutil


def checkMint(chain, contract_address, pair_contract):
    try:
        print("chain: ", chain, "   CheckMint scan :   ", contract_address)
        test_account = Web3.toChecksumAddress("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
        if chain == "eth":
            url = "https://eth-mainnet.g.alchemy.com/v2/StAa2btHY-EZ51fBC43uygY1HNybOYkR"
            fn_selector = function_signature_to_4byte_selector('mint(address,uint256)')
            ms_data = encode_abi(["address", "uint256"],
                                 [test_account, 1000000])
            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "alchemy_simulateAssetChanges",
                "params": [
                    {
                        "from": test_account,
                        "to": Web3.toChecksumAddress(contract_address),
                        "value": "0x0",
                        "data": Web3.toHex(fn_selector + ms_data)
                    }
                ]
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }
            response = requests.post(url, json=payload, headers=headers).json()
            sleep(1)
            # print(response)
            if response['result']['error'] == "execution reverted":
                return
            asset_changes = response['result']['changes']
            if len(asset_changes) > 0:
                for change in asset_changes:
                    if change['changeType'] == "TRANSFER" \
                            and change['to'].lower() == test_account.lower() \
                            and change['contractAddress'].lower() == contract_address.lower():
                        print("%s链：  合约地址：%s   存在免费mint漏洞，pair合约地址：%s" % (chain, contract_address, pair_contract))
                        scanutil.ding_send_text("[chain_poc]" + chain + "：  token合约疑似存在mint方法未鉴权的安全问题：" + contract_address + " pair合约地址：   " + pair_contract)
                        return
    except Exception as e:
        print(e)


if __name__ == "__main__":
    checkMint("eth", "0x0F67A226c385500c68fFa8bb7Fbe0DB15fE65E24", "999")
