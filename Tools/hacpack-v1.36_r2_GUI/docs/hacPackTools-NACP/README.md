# hacPackTools-NACP - Docs

## Options

### View .nacp contents

```
*nix: hptnacp -a print -i ./control.nacp
Windows: hptnacp.exe -a print -i .\control.nacp
```

### Create NACP from XML

```
*nix: hptnacp -a createnacp -i ./control.xml -o ./control.nacp
Windows: hptnacp.exe -a createnacp -i .\control.xml -o .\control.nacp
```

### Create XML from NACP

```
*nix: hptnacp -a createxml -i ./control.nacp -o ./control.xml
Windows: hptnacp.exe -a createxml -i .\control.nacp -o .\control.xml
```

## XML Elements

### \<Title\>

##### \<Language\>

|          Value       |
|----------------------|
| AmericanEnglish      |
| BritishEnglish       |
| Japanese             |
| French               |
| German               |
| LatinAmericanSpanish |
| Spanish              |
| Italian              |
| Dutch                |
| CanadianFrench       |
| Portuguese           |
| Russian              |
| Korean               |
| Taiwanese            |

##### \<Name\>

Character, Max Size = 512

##### \<Publisher\>

Character, Max Size = 256

### \<Isbn\>

Character, Max Size = 37, Usually empty

### \<StartupUserAccount\>

| Value                                      |
|--------------------------------------------|
| None                                       |
| Required                                   |
| RequiredWithNetworkServiceAccountAvailable |

### \<ParentalControl\>

| Value             |
|-------------------|
| None              |
| FreeCommunication |

### \<SupportedLanguage\>

|          Value       |
|----------------------|
| AmericanEnglish      |
| BritishEnglish       |
| Japanese             |
| French               |
| German               |
| LatinAmericanSpanish |
| Spanish              |
| Italian              |
| Dutch                |
| CanadianFrench       |
| Portuguese           |
| Russian              |
| Korean               |
| Taiwanese            |

### \<Screenshot\>

| Value |
|-------|
| Allow |
| Deny  |

### \<VideoCapture\>

| Value   |
|---------|
| Disable |
| Manual  |
| Enable  |

### \<PresenceGroupId\>

8 Bytes hex characters, Usually Title ID

### \<DisplayVersion\>

Character, Max Size = 16

### \<DataLossConfirmation\>

| Value    |
|----------|
| None     |
| Required |

### \<Rating\>

##### \<Organization\>

| Value        |
|--------------|
| CERO         |
| GRACGCRB     |
| GSRMR        |
| ESRB         |
| ClassInd     |
| USK          |
| PEGI         |
| PEGIPortugal |
| PEGIBBFC     |
| Russian      |
| ACB          |
| OFLC         |

##### \<Age\>

Integer

### \<PlayLogPolicy\>

| Value   |
|---------|
| All     |
| LogOnly |
| None    |

### \<SaveDataOwnerId\>

8 Bytes hex characters, Usually Title ID

### \<UserAccountSaveDataJournalSize\>

8 Bytes hex characters

### \<DeviceSaveDataSize\>

8 Bytes hex characters

### \<DeviceSaveDataJournalSize\>

8 Bytes hex characters

### \<BcatDeliveryCacheStorageSize\>

8 Bytes hex characters

### \<ApplicationErrorCodeCategory\>

Character, Max Size = 8, Usually empty

### \<AddOnContentBaseId\>

8 Bytes hex characters, Usually Title ID + 0x1000

### \<LogoType\>

| Value              |
|--------------------|
| LicensedByNintendo |
| Nintendo           |

### \<LocalCommunicationId\>

8 Bytes hex characters, Usually Title ID

### \<LogoHandling\>

| Value  |
|--------|
| Auto   |
| Manual |

### \<SeedForPseudoDeviceId\>

8 Bytes hex characters, Usually Title ID

### \<BcatPassphrase\>

Character, Max Size = 65, Usually empty

### \<AddOnContentRegistrationType\>

| Value       |
|-------------|
| AllOnLaunch |
| OnDemand    |

### \<UserAccountSaveDataSizeMax\>

8 Bytes hex characters

### \<UserAccountSaveDataJournalSizeMax\>

8 Bytes hex characters

### \<DeviceSaveDataSizeMax\>

8 Bytes hex characters

### \<DeviceSaveDataJournalSizeMax\>

8 Bytes hex characters

### \<TemporaryStorageSize\>

8 Bytes hex characters

### \<CacheStorageSize\>

8 Bytes hex characters

### \<CacheStorageJournalSize\>

8 Bytes hex characters

### \<CacheStorageDataAndJournalSizeMax\>

8 Bytes hex characters

### \<CacheStorageIndexMax\>

8 Bytes hex characters

### \<Hdcp\>

| Value    |
|----------|
| None     |
| Required |

### \<CrashReport\>

| Value |
|-------|
| Deny  |
| Allow |

### \<RuntimeAddOnContentInstall\>

| Value       |
|-------------|
| Deny        |
| AllowAppend |

### \<PlayLogQueryCapability\>

8 Bytes hex characters, Usually 0

### \<Repair>

| Value                  |
|------------------------|
| None                   |
| SuppressGameCardAccess |
Usually none

### \<Attribute\>

| Value                    |
|--------------------------|
| None                     |
| Demo                     |
| RetailInteractiveDisplay |
Usually None

### \<ProgramIndex\>

Integer, Usually 0

### \<UserAccountSwitchLock>

| Value   |
|---------|
| Disable |
| Enable  |

### \<RequiredNetworkServiceLicenseOnLaunch\>

| Value  |
|--------|
| None   |
| Common |