# Halcyon India Technosys – Inventory ERP Starter

A local Windows desktop inventory application built with Python, PySide6/Qt WebEngine, HTML, CSS, JavaScript and SQLite.

## Included modules
- Command Centre: product count, stock units, estimated stock value and low-stock alerts
- Company Master: company name, address, GSTIN and MSME
- Product Master: SKU, product name, category, unit, purchase price and reorder level
- Stock In / Stock Out: movement records with negative-stock prevention
- Stock Report: current balances and recent movement history

## Requirements
- Windows 10/11, 64-bit
- Python 3.10 or later (64-bit recommended)
- Internet only for initial Python package installation and GitHub operations; daily local inventory use does not require internet

## Run from source
1. Install Python and Git.
2. Clone your GitHub repository or extract this project.
3. Open Command Prompt in the project folder.
4. Create and activate a virtual environment:

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   ```

5. Install packages:

   ```bat
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start the application:

   ```bat
   python app.py
   ```

## Database location
The app creates its database automatically at:

`%LOCALAPPDATA%\HalcyonIndiaTechnosys\halcyon_inventory.db`

This keeps business data outside the program folder and outside the packaged EXE.

## Run tests
From the project folder, run:

```bat
python -m unittest discover -s tests -v
```

## Build Windows EXE
Double-click `build_exe.bat`, or run it from Command Prompt.

The first build is an onedir distribution. Launch:

`dist\Halcyon_India_Technosys_ERP\Halcyon_India_Technosys_ERP.exe`

Copy the entire `Halcyon_India_Technosys_ERP` folder from `dist` to the target PC. Do not copy only the EXE; Qt runtime files are alongside it.

## GitHub setup
Create an empty repository on GitHub, then from this folder run:

```bat
git init
git add .
git commit -m "Initial inventory ERP starter"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/Halcyon_India_Technosys_ERP.git
git push -u origin main
```

Replace YOUR-USERNAME with your GitHub account name.

To publish later changes:

```bat
git add .
git commit -m "Describe your change"
git push
```

## Important limitations
This is a functional learning starter, not a finished accounting/ERP product. It currently does not include purchase invoices, sales invoices, GST calculations, user roles, audit-grade logs, barcode devices, multi-user/network operation, or installer signing. Validate business rules and take database backups before production use.

For production, add authenticated users, permissions, database migration/versioning, audit logs, backup/restore verification, automated installer testing and a signed Windows installer.
