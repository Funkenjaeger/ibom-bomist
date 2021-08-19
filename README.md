# IBOM-BOMIST
Interactive CLI tool which integrates the BOMIST inventory/BOM management tool with InteractiveHtmlBom 

The primary purpose is to inject storage (inventory) location for each part to the table displayed in the InteractiveHtmlBom page to facilitate kitting for a build.
The tool also replaces part data like Manufacturer Part Number, Value, Package, etc. with the values from BOMIST, which tend to be more carefully curated than the defaults in Eagle/Fusion 360 built-in or third-party libraries.

## Installation:
A virtual environment is recommended.
From within the working directory, just run `pip install -r requirements.txt`

## Usage:
First, create a JSON representation of your Eagle/Fusion 360 Electronics board using **[brd2json.ulp](https://github.com/Funkenjaeger/brd2json)**

In BOMIST, you should have created a BOM for your board, a Build of that BOM and reserved inventory (which assigns a 'Source' inventory location), or marked DNP, for each part.
Then, with the Builds tab selected, right-click in the BOM table and select "Export":
![image](https://user-images.githubusercontent.com/24237058/130111325-5a676d83-d2a0-4a8e-991c-7076da793fe5.png)
Then configure it to export in JSON format without IDs:
![image](https://user-images.githubusercontent.com/24237058/130111692-53c7aaef-ac1f-45cc-bbb8-6c38d265fa70.png)

To process the board and BOM information, just run this script (main.py) and work through the interactive menus.  Enter the command `help` for... help.

The script will auto-detect any JSON board files in the directories used by Fusion 360 and display them in a list.
The command `board 1` will select the first auto-detected board file, for example.  If you enter `board` with no argument, it will open a file browse dialog for you to pick a board JSON file.
The command `build` will open a file browse dialog for you to pick your build file (JSON exported from BOMIST)

Once you've selected files for the Board and the Build, enter `run` to process them and generate the Interactive BOM.

![image](https://user-images.githubusercontent.com/24237058/109439143-2b96fe00-79fb-11eb-99ab-4196ade30493.png)

## TODO:
- More error checking (in case BOM doesn't match the board)
