# TeleSysControl

TeleSysControl is a Windows system management project that uses a Telegram bot to remotely manage essential system features from anywhere.

---

## Features

<div align="center">

| Action |
|--------|
| System Monitoring (CPU, RAM, GPU, drives, processes, battery, charging status) |
| Show System Uptime |
| Capture Screenshot |
| Speed Test |
| Volume Control (increase, decrease, mute, max) |
| Power Control (shutdown, sleep, hibernate, restart) |
| Windows Command line |
| Auto Connect to Telegram bot on internet availability |

</div>

---

## Requirements

- Windows 10 or Windows 11  
- Administrator access (recommended for full functionality)

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Prashant64bit/TeleSysControl.git
cd TeleSysControl
```

2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Configure the Project

Edit `config.py` and update your:

- `apiID`
- `apiHASH`
- `botToken`
- `ownerId`

### Run the Application

```bash
python main.py
```

---

## License

This project is licensed under the [MIT License](LICENSE).
