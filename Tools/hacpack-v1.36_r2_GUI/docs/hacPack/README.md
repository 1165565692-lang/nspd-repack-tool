# hacPack - Docs

## General Options

### TitleID: --titleid

Title id is 8-bytes hex value which connects ncas to each other.  
Valid Title id range is: 0100000000000000 - ffffffffffffffff  
It's not recommended to use a TitleID higher than 01ffffffffffffff.  
If you are repacking a nca, make sure to use the original title id of that nca.  

##### Switch TitleID template:

Application: 01xxxxxxxxxxxxxx000  
Patch(Update): Application + 0x800  
AddOn(DLC): Application + 0x1000 + 0x01-0xff

### Type: --type

If you want to create a NCA, use --type nca, Otherwise if you want to create a NSP, use --type nsp.  

## NCA Options

### NCA signature: --ncasig

By default, hacPack fills nca signature with zero, you can use --ncasig random to fill it with random bytes or --ncasig static to fill it with 0x4.  

### NCA distribution type: --disttype

Default nca distribution type is download, you can change it to gamecard with --disttype gamecard if you want to pack nca in xci.  

### Key area key 2: --keyareakey

This is 16-bytes key which hacPack use to encrypt sections.  
There's a default key area key 2 in hacPack and you can change it by --keyareakey option.  

### Crypto type: --titlekey

Titlekey size is 16 bytes  
If no titlekey is specified, hacPack creates standard crypto nca and uses key area key 2 to encrypt sections.  
Otherwise, hacPack creates titlekey crypto nca and use titlekey to encrypt sections.  
Titlekey is only supported on Program, Manual(HtmlDocument) and PublicData ncas.  

### Section encryption type: --plaintext

hacPack uses AES-CTR encryption for section by default.  
You can use --plaintext to change section encryption type to unencrypted (plaintext).  
Logo section in program nca is always plaintext.

### Key generation: --keygeneration

Keygeneration is a key that hacPack uses to encrypt key area in ncas.  
It is a number between 1-32 and it describes the 'key_area_key_application' key that hacPack uses in encryption.  
Firmwares always support applications with keygenerations up to the keygeneration they ship with.  

Keygeneration | Firmware
--------------| --------
1 | 1.0.0 - 2.3.0
2 | 3.0.0
3 | 3.0.1 - 3.0.2
4 | 4.0.0 - 4.1.0
5 | 5.0.0 - 5.1.0
6 | 6.0.0 - 6.0.1
7 | 6.2.0

### SDK Version: --sdkverison

There's a field in ncas which describes the version of sdk that is used to make nca.  
Overall, it's not an important field but it must be greater than 000B0000 (0.11.0.0).  
Valid SDK Version range is: 000B0000 - 00FFFFFF

## Creating NCA

### Program NCA: --ncatype program

Program NCA contains 3 sections  
Section 0 (known as exefs) contains main and main.npdm, it also may contain rtld and subsdks  
Section 1 (known as romfs) contains romfs data  
Section 2 (known as logo) contains logo data including "NintendoLogo.png" and "StartupMovie.gif"  
You can use --nologo to skip logo and --noromfs to skip romfs section in program nca  
hacPack zeros ACID signature and key in NPDM, You can use --nozeroacidsig and --nozeroacidkey to skip zeroing of acid signature and key  

```
*nix: hacpack -o ./out/ --type nca --ncatype program --titleid 0104444444444000 --exefsdir ./exefs/ --romfsdir ./romfs/ --logodir ./logo/  
Windows: hacpack.exe -o .\out\ --type nca --ncatype program --titleid 0104444444444000 --exefsdir .\exefs\ --romfsdir .\romfs\ --logodir .\logo\
```

### Control NCA: --ncatype control

Control NCA contains 1 section  
Section 0 (known as romfs) contains control.nacp and icons with icon_{lang}.dat  

```
*nix: hacpack -o ./out/ --type nca --ncatype control --titleid 0104444444444000 --romfsdir ./control/
Windows: hacpack.exe -o .\out\ --type nca --ncatype control --titleid 0104444444444000 --romfsdir .\control\
```

### Manual NCA: --ncatype manual

Manual NCA contains 1 section  
It contains "Legal Information" or "Offline-Manual" html documents  

```
*nix: hacpack -o ./out/ --type nca --ncatype manual --titleid 0104444444444000 --romfsdir ./manual/
Windows: hacpack.exe -o .\out\ --type nca --ncatype manual --titleid 0104444444444000 --romfsdir .\manual\
```

### Data NCA: --ncatype data

Data NCA contains 1 section  

```
*nix: hacpack -o ./out/ --type nca --ncatype data --titleid 0104444444444000 --romfsdir ./data/
Windows: hacpack.exe -o .\out\ --type nca --ncatype data --titleid 0104444444444000 --romfsdir .\data\
```

### PublicData NCA: --ncatype publicdata

PublicData NCA contains 1 section  

```
*nix: hacpack -o ./out/ --type nca --ncatype publicdata --titleid 0104444444444001 --romfsdir ./publicdata/
Windows: hacpack.exe -o .\out\ --type nca --ncatype publicdata --titleid 0104444444444001 --romfsdir .\publicdata\
```

### Metadata NCA: --ncatype meta

Metadata NCA contains 1 section  
There's a file called cnmt in metadata nca which contains information about other ncas  
You can build metadata nca from ncas or you can make it directly from cnmt  
You must specify --titletype option for creating metadata nca.  
Title type  "application" is for apps and games, "addon" is for dlcs, "systemprogram" is for firmware programs, "systemdata" is for firmware datas.  
"application" contains program and control ncas, it may also contain manual(legal information, offline-manual html) and data ncas.  
"addon" only contains publicdata nca  
"systemprogram" only contains program nca  
"systemdata" only contains data nca  

```
*nix: hacpack -o ./out/ --type nca --ncatype meta --titleid 0104444444444000 --programnca ./nca/00000000000000000000000000000001.nca
  --controlnca ./nca/00000000000000000000000000000002.nca --legalnca ./nca/00000000000000000000000000000003.nca
  --htmldocnca ./nca/00000000000000000000000000000004.nca --datanca ./nca/00000000000000000000000000000005.nca  
Windows: hacpack.exe -o .\out\ --type nca --ncatype meta --titleid 0104444444444000 --programnca .\nca\00000000000000000000000000000001.nca
  --controlnca .\nca\00000000000000000000000000000002.nca --legalnca .\nca\00000000000000000000000000000003.nca
  --htmldocnca .\nca\00000000000000000000000000000004.nca --datanca .\nca\00000000000000000000000000000005.nca  
```

```
*nix: hacpack -o ./out/ --type nca --ncatype meta --titleid 0104444444444000 --cnmt ./cnmt/Application_0104444444444000.cnmt  
Windows: hacpack.exe -o .\out\ --type nca --ncatype meta --titleid 0104444444444000 --cnmt .\cnmt\Application_0104444444444000.cnmt  
```

## Creating NSP

### NSP: --type nsp

NSP is a container for ncas  
You must set your ncas folder with --ncadir option  

```
*nix: hacpack -o ./nsp/ --type nsp --ncadir ./ncas/ --titleid 0104444444444000
Windows: hacpack.exe -o .\nsp\ --type nsp --ncadir .\ncas\ --titleid 0104444444444000
```
