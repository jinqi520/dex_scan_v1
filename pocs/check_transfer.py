import requests
from web3 import Web3
from eth_abi import encode_abi
from eth_utils import function_signature_to_4byte_selector
from time import sleep
from scan_util import scanutil


def checkTransfer(chain, contract_address, pair_contract):
    try:
        print("chain: ", chain, "   CheckTransfer scan :   ", contract_address)
        balance = scanutil.get_balance_eth(contract_address, pair_contract)
        pair_contract = Web3.toChecksumAddress(pair_contract)
        test_account = Web3.toChecksumAddress("0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266")
        if chain == "eth":
            fn_selector = function_signature_to_4byte_selector('transfer(address,uint256)')
            ms_data1 = encode_abi(["address", "uint256"],
                                 [test_account, balance])

            url = "https://eth-mainnet.g.alchemy.com/v2/StAa2btHY-EZ51fBC43uygY1HNybOYkR"
            payload1 = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "alchemy_simulateAssetChanges",
                "params": [
                    {
                        "from": pair_contract,
                        "to": Web3.toChecksumAddress(contract_address),
                        "value": "0x0",
                        "data": Web3.toHex(fn_selector + ms_data1)
                    }
                ]
            }
            headers = {
                "accept": "application/json",
                "content-type": "application/json"
            }
            response = requests.post(url, json=payload1, headers=headers).json()
            sleep(1)
            # 直接模拟转走所有的token，如果能成功 说明不存在漏洞 可能只是日志打印不正确导致的
            if response['result']['error'] != "execution reverted":
                return

            ms_data2 = encode_abi(["address", "uint256"],
                                  [test_account, balance // 2])
            payload2 = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "alchemy_simulateAssetChanges",
                "params": [
                    {
                        "from": pair_contract,
                        "to": Web3.toChecksumAddress(contract_address),
                        "value": "0x0",
                        "data": Web3.toHex(fn_selector + ms_data2)
                    }
                ]
            }
            response = requests.post(url, json=payload2, headers=headers).json()
            sleep(1)
            # 第二次模拟转一半的资产，判断是否成功且日志金额大于传入的金额
            if response['result']['error'] == "execution reverted":
                return
            asset_changes = response['result']['changes']
            if len(asset_changes) > 0:
                amount = 0
                for change in asset_changes:
                    if change['changeType'] == "TRANSFER" \
                            and change['from'].lower() == pair_contract.lower() \
                            and change['contractAddress'].lower() == contract_address.lower():
                        amount = amount + int(change['rawAmount'])
                if amount > balance//2:
                    print("%s链：  合约地址：%s   疑似存在转账收取额外手续费的安全问题，pair合约地址：%s" % (chain, contract_address, pair_contract))
                    scanutil.ding_send_text("[chain_poc]" + chain + "：  token合约疑似存在转账收取额外手续费的安全问题：" + contract_address + " pair合约地址：   " + pair_contract)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    checkTransfer("eth", "0x08756B33883Bd52e229a1518eE581488c7aA40E6", "0xC04c1F0eFcB4AE37c54869eE8825F1cD636911E1")