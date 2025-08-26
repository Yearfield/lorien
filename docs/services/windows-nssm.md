# Windows Service Installation with NSSM

This guide shows how to install the Lorien API as a Windows service using NSSM (Non-Sucking Service Manager).

## Prerequisites

1. Download NSSM from: https://nssm.cc/download
2. Extract `nssm.exe` to a directory in your PATH (e.g., `C:\Windows\System32\`)

## Installation Steps

1. **Open Command Prompt as Administrator**

2. **Navigate to your Lorien directory**
   ```cmd
   cd C:\path\to\Lorien
   ```

3. **Install the service**
   ```cmd
   nssm install LorienAPI
   ```

4. **Configure the service**
   ```cmd
   nssm set LorienAPI Application "C:\path\to\Lorien\.venv\Scripts\python.exe"
   nssm set LorienAPI AppParameters "-m uvicorn api.server:app --host 127.0.0.1 --port 8000"
   nssm set LorienAPI AppDirectory "C:\path\to\Lorien"
   nssm set LorienAPI AppEnvironmentExtra "DB_PATH=%APPDATA%\lorien\app.db"
   ```

5. **Set startup type**
   ```cmd
   nssm set LorienAPI Start SERVICE_AUTO_START
   ```

6. **Start the service**
   ```cmd
   net start LorienAPI
   ```

## Service Management

- **Start**: `net start LorienAPI`
- **Stop**: `net stop LorienAPI`
- **Status**: `sc query LorienAPI`
- **Remove**: `nssm remove LorienAPI confirm`

## Troubleshooting

- Check Windows Event Viewer for service errors
- Verify the Python path and virtual environment exist
- Ensure the DB_PATH directory is writable
- Test the command manually before installing as service
