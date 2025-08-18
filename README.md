# RGB Transfer Toolkit

—— A comprehensive toolkit for RGB protocol token transfers on Bitcoin


## 🌟 Overview

The RGB Transfer Toolkit is a production-ready automation tool for executing RGB token transfers on Bitcoin. It demonstrates the complete integration of RGB protocol with Bitcoin's PSBT (Partially Signed Bitcoin Transactions) system, enabling secure, efficient, and automated token transfers.

### ✨ Key Features

- 🤖 **Full Automation** - Complete RGB transfer workflow from invoice to confirmation
- 🔐 **PSBT Integration** - Automated Bitcoin transaction signing and broadcasting
- 🛡️ **Security First** - BIP32 key derivation and secure private key management
- 🔄 **Error Recovery** - Intelligent error handling and transaction verification
- 📊 **State Validation** - Professional RGB state analysis and verification
- 🐳 **Docker Ready** - Seamless integration with Bitcoin Core and RGB infrastructure

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│     Application Layer (Python)     │  ← Business Logic & Automation
├─────────────────────────────────────┤
│      RGB Protocol Layer (CLI)      │  ← State Management & Validation
├─────────────────────────────────────┤
│    Commitment Layer (Tapret)       │  ← Cryptographic Commitments
├─────────────────────────────────────┤
│   Bitcoin Layer (Bitcoin Core)     │  ← UTXO Management & Consensus
└─────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **RGB CLI** - [Installation Guide](https://rgb.tech/)
- **Bitcoin Core** (via Docker recommended)
- **Docker & Docker Compose**

### Installation

```bash
# Clone the repository
git clone https://github.com/aaron-recompile/rgb-transfer-toolkit.git
cd rgb-transfer-toolkit

# Install Python dependencies
pip install -r requirements.txt

# Copy and customize configuration
cp examples/config_example.json config.json
# Edit config.json with your wallet paths and contract details
```

### Basic Usage

```bash
# Execute a complete RGB transfer
python complete_rgb_transfer.py

# Or use the modular approach
python tools/rgb_transfer_manager.py --amount 500 --contract-id your_contract_id
```

## 📋 Configuration

Edit the `CONFIG` dictionary in `complete_rgb_transfer.py`:

```python
CONFIG = {
    "alice_dir": "/path/to/.alice",           # Alice's RGB wallet
    "bob_dir": "/path/to/.bob",               # Bob's RGB wallet  
    "contract_id": "rgb:YOUR_CONTRACT_ID",    # Your RGB contract
    "amount": "500",                          # Transfer amount
    "network": "regtest",                     # Bitcoin network
    "alice_tprv": "tprv8...",                # Alice's private key
}
```

⚠️ **Security Note**: Never commit real private keys to version control!

## 🔧 Technical Implementation

### PSBT Workflow

The toolkit implements a sophisticated PSBT (Partially Signed Bitcoin Transaction) workflow:

1. **Key Derivation** - BIP32 hierarchical deterministic key generation
2. **PSBT Creation** - RGB protocol generates unsigned transaction
3. **Signature** - Bitcoin Core signs using imported private keys
4. **Broadcasting** - Transaction broadcast to Bitcoin network
5. **Verification** - RGB state validation and confirmation

### RGB Integration

- **Invoice Generation** - Automated RGB invoice creation
- **State Transitions** - Secure RGB contract state management
- **Client-Side Validation** - Complete RGB consensus rule verification
- **Commitment Schemes** - Tapret commitment analysis and validation

## 📁 Project Structure

```
rgb-transfer-toolkit/
├── complete_rgb_transfer.py    # Main transfer tool
├── tools/                      # Additional utilities
│   ├── rgb_state_analyzer.py   # State analysis tools
│   └── psbt_manager.py         # PSBT handling utilities
├── examples/                   # Configuration examples
│   ├── config_example.json     # Sample configuration
│   └── docker-compose.yml      # Docker setup
├── tests/                      # Test suite
├── docs/                       # Documentation
└── README.md                   # This file
```

## 🧪 Testing

```bash
# Run the test suite
python -m pytest tests/ -v

# Run specific test categories
python -m pytest tests/test_psbt.py -v
python -m pytest tests/test_rgb_integration.py -v
```

## 🐳 Docker Support

Use the provided Docker configuration for a complete RGB development environment:

```bash
# Start Bitcoin Core and RGB infrastructure
docker-compose up -d

# Run transfers in the containerized environment
python complete_rgb_transfer.py
```


## 🤝 Development Setup

```bash
# Fork the repository and clone your fork
git clone https://github.com/your-username/rgb-transfer-toolkit.git

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -r requirements.txt
pip install -e .

# Run tests
python -m pytest
```

## 🔗 Related Projects

- [RGB Protocol](https://rgb.tech/) - Official RGB protocol implementation
- [Bitcoin Core](https://bitcoincore.org/) - Bitcoin reference implementation  
- [Bitlight Labs](https://bitlightlabs.com/) - RGB wallet and infrastructure
- [BitMask](https://bitmask.app/) - RGB browser wallet

## ⚖️ License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/aaron-recompile/rgb-transfer-toolkit/issues)
- **Discussions**: [GitHub Discussions](https://github.com/aaron-recompile/rgb-transfer-toolkit/discussions)

---

**Built with ❤️ for the Bitcoin and RGB communities**

*Enabling programmable Bitcoin while preserving its core values of security and decentralization. We welcome contributions! *