#!/usr/bin/env python3
"""
实验2: Bob → Dave 完整转账流程
"""

import os
import sys
from datetime import datetime

# 添加tools目录到路径  
sys.path.insert(0, "tools")

def rgb_cmd(wallet_dir, args, network="regtest", esplora="http://localhost:3002"):
    """执行 RGB 命令"""
    import subprocess
    cmd = ["rgb", "-d", wallet_dir, "-n", network] + args + [f"--esplora={esplora}"]
    try:
        print(f"🎨 执行 RGB 命令: {' '.join(args)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print(f"✅ RGB 命令成功")
            return {"success": True, "output": result.stdout.strip()}
        else:
            print(f"❌ RGB 命令失败: {result.stderr}")
            return {"success": False, "error": result.stderr}
    except Exception as e:
        print(f"❌ RGB 命令异常: {e}")
        return {"success": False, "error": str(e)}

def main():
    print("🎯 实验2: Bob → Dave 转账500代币")
    print("=" * 50)
    
    config = {
        "bob_dir": "/Volumes/MAC_Programs/bitlight-rgb20/bitlight-local-env-public/.bob",
        "dave_dir": "/Volumes/MAC_Programs/bitlight-rgb20/bitlight-local-env-public/.dave",
        "contract_id": "rgb:BppYGUUL-Qboz3UD-czwAaVV-!!Jkr1a-SE1!m1f-Cz$b0xs",
        "amount": "500",
        "bob_tprv": "tprv8ZgxMBicQKsPeEP6QyHbs7W2pfW5FJisXLcX93h2AnH5Kx8fuhKz7FYm4kw46SUgXJd3zUKwNoTqxtpLw7vmtLeFUGJb6XSeom45hQjeXxJ",
        "proj": "bitlight-local-env",
        "wallet": "bob_legacy"
    }
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    try:
        # 步骤1: Dave生成发票
        print("\n📋 步骤1: Dave生成发票")
        invoice_result = rgb_cmd(config["dave_dir"], ["invoice", config["contract_id"], "--amount", config["amount"]])
        
        if not invoice_result["success"]:
            raise Exception(f"Dave发票生成失败: {invoice_result['error']}")
        
        invoice = invoice_result["output"]
        print(f"✅ Dave发票: {invoice}")
        
        # 步骤2: Bob创建转账
        print("\n📤 步骤2: Bob创建转账")
        transfer_files = {
            "consignment": f"bob_to_dave_{timestamp}.consignment",
            "psbt": f"bob_to_dave_{timestamp}.psbt"
        }
        
        transfer_result = rgb_cmd(
            config["bob_dir"],
            ["transfer", invoice, transfer_files["consignment"], transfer_files["psbt"]]
        )
        
        if not transfer_result["success"]:
            raise Exception(f"Bob转账创建失败: {transfer_result['error']}")
        
        print(f"✅ 转账文件生成成功")
        print(f"   PSBT: {transfer_files['psbt']}")
        print(f"   Consignment: {transfer_files['consignment']}")
        
        # 步骤3: Dave验证并接受
        print("\n✅ 步骤3: Dave验证并接受")
        validate_result = rgb_cmd(config["dave_dir"], ["validate", transfer_files["consignment"]])
        if not validate_result["success"]:
            raise Exception(f"Dave验证失败: {validate_result['error']}")
        
        accept_result = rgb_cmd(config["dave_dir"], ["accept", "-f", transfer_files["consignment"]])
        if not accept_result["success"]:
            raise Exception(f"Dave接受失败: {accept_result['error']}")
        
        print(f"✅ Dave已验证并接受转账")
        
        print(f"\n🎉 实验2 RGB部分完成！")
        print(f"💡 下一步需要Bob签名PSBT并广播")
        print(f"📁 PSBT文件: {transfer_files['psbt']}")
        
        return True
        
    except Exception as e:
        print(f"❌ 实验2失败: {e}")
        return False

if __name__ == "__main__":
    main()
