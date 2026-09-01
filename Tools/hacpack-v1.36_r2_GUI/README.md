# hacPack

[![License: GPL v2](https://img.shields.io/badge/License-GPL%20v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

hacPack is a tool for creating Nintendo Switch NCAs (Nintendo Content Archive) and packing them into NSPs (Nintendo Submission Package)  
You can use hacPack to make your custom ncas and nsps, repack your modded games, and etc...
  
Thanks: SciresM, yellows8, Adubbz, SwitchBrew

## Usage

### Keys

You should place your keyset file with "keys.dat" filename in the same folder as hacPack  
Alternatively, You can use -k or --keyset option to load your keyset file  
Required keys are:  

Key Name | Description
-------- | -----------
header_key | NCA Header Key
key_area_key_application_xx | Application key area encryption keys
titlekek_xx | Title key encryption key

### CLI Options  

```
*nix: ./hacpack [options...]  
Windows: .\hacpack.exe [options...]  
  
Options:
General options:  
-k, --keyset             Set keyset filepath, default filepath is ./keys.dat  
-h, --help               Display usage  
--tempdir                Set temp directory filepath, default filepath is ./hacpack_temp/  
--backupdir              Set backup directory filepath, default filepath is ./hacbpack_backup/  
--keygeneration          Set keygeneration for encrypting key area, default keygeneration is 1  
--plaintext              Skip encrypting sections and set section header block crypto type to plaintext  
--sdkversion             Set SDK version in hex, default SDK version is 000C1100  
--keyareakey             Set key area key 2 in hex with 16 bytes length  
--ncasig                 Set nca signature type [zero, static, random]. Default is zero  
Required options:  
-o, --output             Set output directory  
--type                   Set file type [nca, nsp]  
--ncatype                Set nca type if file type is nca [program, control, manual, data, publicdata, meta]  
--titleid                Set titleid  
Program NCA options:  
--exefsdir               Set program exefs directory path  
--romfsdir               Set program romfs directory path  
--logodir                Set program logo directory path  
--titlekey               Set Titlekey for encrypting nca  
--nozeronpdmsig          Leave npdm signature and doesn't 0 it  
--nozeronpdmkey          Leave npdm nca key and doesn't 0 it  
--disttype               Set nca distribution type [download, gamecard]. Default is download  
Control NCA options:  
--romfsdir               Set control romfs directory path  
Manual NCA options:  
--romfsdir               Set manual romfs directory path  
--titlekey               Set Titlekey for encrypting nca  
Data NCA options:  
--romfsdir               Set data romfs directory path  
PublicData NCA options:  
--romfsdir               Set publicdata romfs directory path  
--titlekey               Set Titlekey for encrypting nca  
Metadata NCA options:  
--titletype              Set cnmt title type [application, addon, systemprogram, systemdata]  
--titleversion           Set title-version in hex with 4 bytes length, default value is 0x0  
--programnca             Set program nca path  
--controlnca             Set control nca path  
--legalnca               Set legal information nca path  
--htmldocnca             Set offline manual nca path  
--datanca                Set data nca path  
--cnmt                   Set cnmt path  
--digest                 Set cnmt digest  
NSP options:  
--ncadir                 Set input nca directory path  
```

### GUI

hacPack GUI is just an interface for CLI. It's just available for Microsoft Windows and it requires .NetFramework 4.5 or higher  
Currently, all options are not implemented in GUI and it's recommended to use CLI  

### Tools

hacPackTools are tools aiming for modifying and parsing the files in ncas. make sure to check hacPackTools folder  
  
Also Check docs for more info  

## Licensing

This software is licensed under the terms of the GNU General Public License, version 2.  
You can find a copy of the license in the LICENSE file.  
Portions of project hacPack are parts of other projects, make sure to check LICENSES folder
