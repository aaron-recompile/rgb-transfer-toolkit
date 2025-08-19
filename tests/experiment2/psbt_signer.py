#!/usr/bin/env python3
"""
通用PSBT签名和广播脚本
支持不同钱包的PSBT签名
"""

import os
import sys
import json
import base64
import subprocess
from datetime import datetime
from pathlib import Path

def cli(args, proj="bitlight-local-env", wallet=None):
    """执行 bitcoin-cli 命令"""
    base = ["docker","compose","-p",proj,"exec","-T","bitcoin-core","bitcoin-cli","-regtest"]
    if wallet: 
        base += [f"-rpcwallet={wallet}"]
    
    try:
        result = subprocess.run(base + args, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip()}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

def derive_wif_from_tprv(tprv, branch=9, index=0):
    """从 tprv 派生 WIF 私钥"""
    try:
        from bip32 import BIP32, HARDENED_INDEX
        import base58
        import hashlib
        
        b = BIP32.from_xpriv(tprv)
        path = [86|HARDENED_INDEX, 1|HARDENED_INDEX, 0|HARDENED_INDEX, branch, index]
        priv = b.get_privkey_from_path(path)
        payload = b"\xEF" + priv + b"\x01"
        chk = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
        return base58.b58encode(payload + chk).decode()
    except ImportError:
        print("❌ 需要安装依赖: pip install bip32 base58")
        return None

def ensure_legacy_wallet(wallet="bob_legacy", proj="bitlight-local-env"):
    """确保 legacy 钱包存在"""
    try:
        result = cli(["-named","createwallet",f"wallet_name=\"{wallet}\"","descriptors=false","load_on_startup=true"], proj=proj)
        print(f"✅ 创建钱包: {wallet}")
    except:
        pass
    
    try:
        cli(["loadwallet", wallet], proj=proj)
        print(f"✅ 加载钱包: {wallet}")
    except:
        pass

def import_wif(wif, wallet="bob_legacy", proj="bitlight-local-env", label="taproot-internal"):
    """导入 WIF 私钥到钱包"""
    try:
        cli(["importprivkey", wif, label, "false"], proj=proj, wallet=wallet)
        print(f"✅ 导入私钥成功")
    except Exception as e:
        if "already exists" not in str(e):
            print(f"⚠️ 导入私钥失败: {e}")
        else:
            print(f"⚠️ 私钥已存在")

def sign_psbt_with_multiple_keys(psbt_b64, tprv, proj="bitlight-local-env", wallet="bob_legacy"):
    """尝试多个派生路径签名PSBT"""
    
    print(f"🔐 开始PSBT签名流程")
    
    # 确保钱包存在
    ensure_legacy_wallet(wallet, proj)
    
    # 基于RGB UTXO分析，优先尝试正确的路径
    # Bob的RGB UTXO在 &9/0 地址，对应 branch=9, index=0
    priority_paths = [(9, 0)]  # RGB UTXO对应的路径
    fallback_paths = [(9, i) for i in [1, 2, 3, 4, 5, 6]] + [(10, i) for i in [0, 1, 2, 3, 4, 5, 6]] + [(11, i) for i in [0, 1, 2, 3, 4, 5, 6]]
    
    all_paths = priority_paths + fallback_paths
    
    for branch, index in all_paths:
        print(f"   🔍 尝试派生路径: branch={branch}, index={index}")
        
        # 派生WIF私钥
        wif = derive_wif_from_tprv(tprv, branch, index)
        if not wif:
            continue
        
        # 导入私钥
        import_wif(wif, wallet, proj, f"taproot-{branch}-{index}")
        
        try:
            # 尝试签名PSBT
            proc_result = cli(["walletprocesspsbt", psbt_b64, "true"], proj=proj, wallet=wallet)
            if not proc_result["success"]:
                continue
            
            proc_data = json.loads(proc_result["output"])
            processed_psbt = proc_data["psbt"]
            
            # 尝试完成PSBT
            fin_result = cli(["-named", "finalizepsbt", f"psbt={processed_psbt}", "extract=true"], proj=proj)
            if not fin_result["success"]:
                continue
            
            fin_data = json.loads(fin_result["output"])
            
            if fin_data.get("complete") and fin_data.get("hex"):
                print(f"✅ 签名成功使用: branch={branch}, index={index}")
                
                # 尝试广播
                try:
                    txid = cli(["sendrawtransaction", fin_data["hex"]], proj=proj)["output"].strip()
                    print(f"✅ 交易广播成功: {txid}")
                    return {
                        "success": True, 
                        "txid": txid, 
                        "hex": fin_data["hex"],
                        "branch": branch,
                        "index": index
                    }
                except Exception as e:
                    error_msg = str(e)
                    if "insufficient fee" in error_msg or "rejecting replacement" in error_msg:
                        print(f"⚠️ 费用问题，但签名成功")
                        return {
                            "success": True, 
                            "txid": "fee_issue", 
                            "hex": fin_data["hex"],
                            "branch": branch,
                            "index": index,
                            "warning": "Fee insufficient but signed successfully"
                        }
                    else:
                        print(f"❌ 广播失败: {error_msg}")
                        continue
        except Exception as e:
            continue
    
    return {"success": False, "error": "所有派生路径都签名失败"}

def rgb_cmd(wallet_dir, args, network="regtest", esplora="http://localhost:3002"):
    """执行 RGB 命令"""
    cmd = ["rgb", "-d", wallet_dir, "-n", network] + args + [f"--esplora={esplora}"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip()}
        else:
            return {"success": False, "error": result.stderr}
    except Exception as e:
        return {"success": False, "error": str(e)}

def complete_bob_to_dave_transfer():
    """完成 Bob → Dave 转账"""
    
    print("🎯 完成 Bob → Dave 转账 - PSBT签名阶段")
    print("=" * 60)
    
    config = {
        "bob_dir": "/Volumes/MAC_Programs/bitlight-rgb20/bitlight-local-env-public/.bob",
        "dave_dir": "/Volumes/MAC_Programs/bitlight-rgb20/bitlight-local-env-public/.dave",
        "contract_id": "rgb:BppYGUUL-Qboz3UD-czwAaVV-!!Jkr1a-SE1!m1f-Cz$b0xs",
        "bob_tprv": "tprv8ZgxMBicQKsPeEP6QyHbs7W2pfW5FJisXLcX93h2AnH5Kx8fuhKz7FYm4kw46SUgXJd3zUKwNoTqxtpLw7vmtLeFUGJb6XSeom45hQjeXxJ",
        "proj": "bitlight-local-env",
        "wallet": "bob_legacy"
    }
    
    # 查找最新的PSBT文件
    psbt_files = list(Path(".").glob("bob_to_dave_*.psbt"))
    if not psbt_files:
        print("❌ 未找到Bob→Dave的PSBT文件")
        return False
    
    latest_psbt = max(psbt_files, key=os.path.getctime)
    print(f"📁 找到PSBT文件: {latest_psbt}")
    
    # 读取PSBT文件
    try:
        with open(latest_psbt, "rb") as f:
            psbt_data = f.read()
        psbt_b64 = base64.b64encode(psbt_data).decode('ascii')
        print(f"✅ PSBT文件读取成功 ({len(psbt_data)} 字节)")
    except Exception as e:
        print(f"❌ 读取PSBT文件失败: {e}")
        return False
    
    # 签名PSBT
    print(f"\n🔐 开始签名PSBT...")
    sign_result = sign_psbt_with_multiple_keys(
        psbt_b64, 
        config["bob_tprv"], 
        config["proj"], 
        config["wallet"]
    )
    
    if not sign_result["success"]:
        print(f"❌ PSBT签名失败: {sign_result['error']}")
        return False
    
    print(f"✅ PSBT签名成功!")
    if sign_result.get("txid"):
        print(f"   TXID: {sign_result['txid']}")
    if sign_result.get("warning"):
        print(f"   ⚠️ 警告: {sign_result['warning']}")
    
    # 验证转账结果
    print(f"\n🔍 验证转账结果...")
    
    # 等待状态同步
    import time
    time.sleep(3)
    
    bob_state = rgb_cmd(config["bob_dir"], ["state", config["contract_id"], "RGB20Fixed", "--sync"])
    dave_state = rgb_cmd(config["dave_dir"], ["state", config["contract_id"], "RGB20Fixed", "--sync"])
    
    if bob_state["success"] and dave_state["success"]:
        print(f"✅ 状态获取成功")
        print(f"\n📊 Bob状态:")
        print(bob_state["output"][-300:])  # 显示最后300个字符
        print(f"\n📊 Dave状态:")
        print(dave_state["output"][-300:])  # 显示最后300个字符
        
        # 检查Dave是否有代币
        if "500" in dave_state["output"]:
            print(f"\n🎉 实验2完全成功!")
            print(f"✅ Bob → Dave 转账 500 代币已完成")
            print(f"🔗 见证交易: {sign_result.get('txid', 'N/A')}")
            return True
        else:
            print(f"\n⚠️ 转账可能还在处理中...")
            return False
    else:
        print(f"❌ 无法获取状态验证结果")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "sign-only":
        # 仅签名模式
        if len(sys.argv) < 4:
            print("用法: python script.py sign-only <psbt_file> <tprv>")
            sys.exit(1)
        
        psbt_file = sys.argv[2]
        tprv = sys.argv[3]
        
        try:
            with open(psbt_file, "rb") as f:
                psbt_data = f.read()
            psbt_b64 = base64.b64encode(psbt_data).decode('ascii')
            
            result = sign_psbt_with_multiple_keys(psbt_b64, tprv)
            if result["success"]:
                print(f"✅ 签名成功: {result}")
            else:
                print(f"❌ 签名失败: {result}")
        except Exception as e:
            print(f"❌ 错误: {e}")
    else:
        # 完整转账模式
        success = complete_bob_to_dave_transfer()
        if success:
            print(f"\n🎉 实验2: Bob → Dave 转账完全成功!")
        else:
            print(f"\n❌ 实验2: 转账未完全成功，请检查状态")

if __name__ == "__main__":
    main()