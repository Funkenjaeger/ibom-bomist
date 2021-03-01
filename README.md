# IBOM-BOMIST
Integrating the BOMIST inventory/BOM management tool with InteractiveHtmlBom 

The primary purpose is to inject storage (inventory) location for each part to the table displayed in the InteractiveHtmlBom page to facilitate kitting for a build.
The tool can also replace part data like Manufacturer Part Number, Value, Package, etc. with the values from BOMIST, which tend to be more carefully curated than the defaults in Eagle built-in or third-party libraries.

*Note that this tool uses the BOMIST API to fetch BOM data, which is only available in the paid BOMIST plans*

## Installation:
A virtual environment is recommended.
From within the working directory, just run `pip install -r requirements.txt`

## Usage:
First, create a JSON representation of your Eagle/Fusion 360 Electronics board using **[brd2json.ulp](https://github.com/Funkenjaeger/brd2json)**

In BOMIST, you should have created a BOM for your board, a Build of that BOM and reserved inventory (which assigns a 'Source' inventory location) for each part.

To process the board and BOM information, just run:

`python main.py "<path_to.json>" --bomist <BOMIST_project>,<BOMIST_BOM_rev>,<BOMIST_build> --extra-fields Source`

example (with Fusion 360 Electronics):

`"C:/Users/<username>/AppData/Local/Temp/Neutron/ElectronFileOutput/26620/brd-60e2812b-8771-4b53-a0f8-f786d5fe48f9/MZMFC v8.json" --bomist test2,B,PRB615316087 --extra-fields Source`

![image](https://user-images.githubusercontent.com/24237058/109439143-2b96fe00-79fb-11eb-99ab-4196ade30493.png)

## TODO:
- CLI menu system to facilitate interactively selecting JSON and/or BOMIST build without having to pass explicitly
- Abstract away `--extra-fields Source` since that's implied (while still accepting other --extra-fields entries)
- More error checking (in case BOM doesn't match the board)
- GUI, maybe
