[CmdletBinding()]
param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$NspdPath,

    [string]$BaseUnpacked,
    [string]$ProjectRoot,
    [string]$WorkflowRoot,
    [string]$TitleId = '0100b00b51230000',
    [string]$Hacpack,
    [string]$Hactool,
    [string]$Keys,
    [switch]$NoVerify
)

$ErrorActionPreference = 'Stop'

# Resolve defaults relative to the checkout so the workflow works after moving
# the RepackWorkflow folder to another drive or user profile.
$scriptWorkflowRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($WorkflowRoot)) {
    $WorkflowRoot = $scriptWorkflowRoot
}
if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $ProjectRoot = Split-Path -Parent $WorkflowRoot
}
if ([string]::IsNullOrWhiteSpace($Hacpack)) {
    $Hacpack = Join-Path $WorkflowRoot 'Tools\hacpack-v1.36_r2_GUI\hacpack.exe'
}
if ([string]::IsNullOrWhiteSpace($Hactool)) {
    $Hactool = Join-Path $WorkflowRoot 'Tools\hactool.exe'
}
if ([string]::IsNullOrWhiteSpace($Keys)) {
    $Keys = Join-Path $WorkflowRoot 'Tools\keys 21.2.0\prod.keys'
}

function Resolve-ExistingItem {
    param(
        [Parameter(Mandatory = $true)]
        [string]$LiteralPath,
        [Parameter(Mandatory = $true)]
        [string]$Label
    )

    if (-not (Test-Path -LiteralPath $LiteralPath)) {
        throw "$Label not found: $LiteralPath"
    }

    return Get-Item -LiteralPath $LiteralPath
}

function Resolve-NspdRoot {
    param([Parameter(Mandatory = $true)][string]$Path)

    $item = Resolve-ExistingItem -LiteralPath $Path -Label 'NSPD path'
    if (-not $item.PSIsContainer) {
        throw "NSPD path must be a directory: $Path"
    }

    $directCode = Join-Path $item.FullName 'program0.ncd\code'
    if (Test-Path -LiteralPath $directCode) {
        return $item.FullName
    }

    $children = Get-ChildItem -LiteralPath $item.FullName -Directory -Filter '*.nspd' |
        Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'program0.ncd\code') }

    if ($children.Count -eq 1) {
        return $children[0].FullName
    }

    throw "Could not find exactly one NSPD directory with program0.ncd\code under: $Path"
}

function New-SafeName {
    param([string]$Name)
    return ($Name -replace '[\\/:*?"<>| ]', '_')
}

function Invoke-Logged {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name,
        [Parameter(Mandatory = $true)]
        [scriptblock]$Command,
        [Parameter(Mandatory = $true)]
        [string]$LogDir
    )

    $log = Join-Path $LogDir "$Name.log"
    Write-Host "RUN=$Name"
    $previousErrorActionPreference = $ErrorActionPreference
    $previousNativeCommandPreference = $null
    $hasNativeCommandPreference = Test-Path Variable:\PSNativeCommandUseErrorPreference

    if ($hasNativeCommandPreference) {
        $previousNativeCommandPreference = $PSNativeCommandUseErrorPreference
        $PSNativeCommandUseErrorPreference = $false
    }

    try {
        $ErrorActionPreference = 'Continue'
        & $Command 2>&1 | ForEach-Object { $_.ToString() } | Tee-Object -FilePath $log | Out-Null
        $exitCode = $LASTEXITCODE
    }
    finally {
        $ErrorActionPreference = $previousErrorActionPreference
        if ($hasNativeCommandPreference) {
            $PSNativeCommandUseErrorPreference = $previousNativeCommandPreference
        }
    }

    if ($exitCode -ne 0) {
        throw "$Name failed with exit code $exitCode. See $log"
    }
}

$hacpackItem = Resolve-ExistingItem -LiteralPath $Hacpack -Label 'hacpack.exe'
$hactoolItem = Resolve-ExistingItem -LiteralPath $Hactool -Label 'hactool.exe'
$keysItem = Resolve-ExistingItem -LiteralPath $Keys -Label 'prod.keys'

$nspdRoot = Resolve-NspdRoot -Path $NspdPath
$codeDir = Join-Path $nspdRoot 'program0.ncd\code'
$logoSrcDir = Join-Path $nspdRoot 'program0.ncd\logo'
$controlSrcDir = Join-Path $nspdRoot 'control0.ncd\data'
$requiredCodeFiles = @('main', 'main.npdm', 'rtld', 'sdk', 'subsdk0', 'subsdk1', 'subsdk2', 'subsdk3')
foreach ($file in $requiredCodeFiles) {
    $path = Join-Path $codeDir $file
    if (-not (Test-Path -LiteralPath $path)) {
        Write-Warning "Optional code file missing (will continue): $path"
    }
}
if (-not (Test-Path -LiteralPath $logoSrcDir)) {
    Write-Warning "NSPD logo directory missing (will skip logo replacement): $logoSrcDir"
}
if (-not (Test-Path -LiteralPath $controlSrcDir)) {
    Write-Warning "NSPD control data directory missing (will skip control replacement): $controlSrcDir"
}

$workRoot = Join-Path $WorkflowRoot 'work'
$outputRoot = Join-Path $WorkflowRoot 'outputs'
New-Item -ItemType Directory -Path $workRoot, $outputRoot -Force | Out-Null

$nspdParentName = Split-Path (Split-Path $nspdRoot -Parent) -Leaf
$nspdLeafName = Split-Path $nspdRoot -Leaf
$stamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$runName = New-SafeName "$nspdParentName-$nspdLeafName-$stamp"
$workDir = Join-Path $workRoot $runName
$outputDir = Join-Path $outputRoot $runName
$ncaOut = Join-Path $outputDir 'ncas'
$nspOut = Join-Path $outputDir 'nsp'
$logOut = Join-Path $outputDir 'logs'
New-Item -ItemType Directory -Path $ncaOut, $nspOut, $logOut -Force | Out-Null

Write-Host "NSPD=$nspdRoot"
Write-Host "WORK=$workDir"
Write-Host "OUT=$outputDir"

# Create fresh work directory structure (no base template needed)
$exefsDir = Join-Path $workDir 'program\exefs'
$romfsDir = Join-Path $workDir 'program\romfs'
$logoDir = Join-Path $workDir 'program\section2_pfs0'
$controlRomfsDir = Join-Path $workDir 'control\romfs'
foreach ($d in @($exefsDir, $romfsDir, $logoDir, $controlRomfsDir)) {
    New-Item -ItemType Directory -Path $d -Force | Out-Null
}

# Populate ExeFS from NSPD code
Get-ChildItem -LiteralPath $codeDir -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination $exefsDir -Force
}

$srcNames = Get-ChildItem -LiteralPath $codeDir -File | Sort-Object Name | Select-Object -ExpandProperty Name
$dstNames = Get-ChildItem -LiteralPath $exefsDir -File | Sort-Object Name | Select-Object -ExpandProperty Name
$diff = Compare-Object -ReferenceObject $srcNames -DifferenceObject $dstNames
if ($diff) {
    Write-Warning "ExeFS file list mismatch (will continue)."
}

# Populate logo (section2_pfs0) from NSPD if exists
if (Test-Path -LiteralPath $logoSrcDir) {
    Get-ChildItem -LiteralPath $logoSrcDir -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $logoDir -Force
    }
}
$srcNames = if (Test-Path -LiteralPath $logoSrcDir) { Get-ChildItem -LiteralPath $logoSrcDir -File | Sort-Object Name | Select-Object -ExpandProperty Name } else { @() }
$dstNames = Get-ChildItem -LiteralPath $logoDir -File | Sort-Object Name | Select-Object -ExpandProperty Name
$diff = Compare-Object -ReferenceObject $srcNames -DifferenceObject $dstNames
if ($diff) {
    Write-Warning "Logo file list mismatch (will continue)."
}

# Populate control romfs from NSPD if exists
if (Test-Path -LiteralPath $controlSrcDir) {
    Get-ChildItem -LiteralPath $controlSrcDir -File | ForEach-Object {
        Copy-Item -LiteralPath $_.FullName -Destination $controlRomfsDir -Force
    }
}
$srcNames = if (Test-Path -LiteralPath $controlSrcDir) { Get-ChildItem -LiteralPath $controlSrcDir -File | Sort-Object Name | Select-Object -ExpandProperty Name } else { @() }
$dstNames = Get-ChildItem -LiteralPath $controlRomfsDir -File | Sort-Object Name | Select-Object -ExpandProperty Name
$diff = Compare-Object -ReferenceObject $srcNames -DifferenceObject $dstNames
if ($diff) {
    Write-Warning "Control romfs file list mismatch (will continue)."
}

Invoke-Logged -Name '01_program_nca' -LogDir $logOut -Command {
    & $hacpackItem.FullName -k $keysItem.FullName -o $ncaOut `
        --tempdir (Join-Path $outputDir 'temp_program') `
        --backupdir (Join-Path $outputDir 'backup_program') `
        --type nca --ncatype program `
        --titleid $TitleId --keygeneration 1 --sdkversion 000C1100 `
        --exefsdir $exefsDir --romfsdir $romfsDir --logodir $logoDir
}

Invoke-Logged -Name '02_control_nca' -LogDir $logOut -Command {
    & $hacpackItem.FullName -k $keysItem.FullName -o $ncaOut `
        --tempdir (Join-Path $outputDir 'temp_control') `
        --backupdir (Join-Path $outputDir 'backup_control') `
        --type nca --ncatype control `
        --titleid $TitleId --keygeneration 1 --sdkversion 000C1100 `
        --romfsdir $controlRomfsDir
}

$programNca = Get-ChildItem -File -LiteralPath $ncaOut -Filter '*.nca' |
    Where-Object { $_.Length -gt 1MB -and $_.Name -notlike '*.cnmt.nca' } |
    Sort-Object Length -Descending |
    Select-Object -First 1
$controlNca = Get-ChildItem -File -LiteralPath $ncaOut -Filter '*.nca' |
    Where-Object { $_.Length -lt 1MB -and $_.Name -notlike '*.cnmt.nca' } |
    Sort-Object Length -Descending |
    Select-Object -First 1
if (-not $programNca) { throw 'Program NCA not found after packing.' }
if (-not $controlNca) { throw 'Control NCA not found after packing.' }

Invoke-Logged -Name '03_meta_nca' -LogDir $logOut -Command {
    & $hacpackItem.FullName -k $keysItem.FullName -o $ncaOut `
        --tempdir (Join-Path $outputDir 'temp_meta') `
        --backupdir (Join-Path $outputDir 'backup_meta') `
        --type nca --ncatype meta --titletype application `
        --titleid $TitleId --titleversion 00000000 `
        --keygeneration 1 --sdkversion 000C1100 `
        --programnca $programNca.FullName --controlnca $controlNca.FullName
}

Invoke-Logged -Name '04_nsp' -LogDir $logOut -Command {
    & $hacpackItem.FullName -k $keysItem.FullName -o $nspOut `
        --tempdir (Join-Path $outputDir 'temp_nsp') `
        --backupdir (Join-Path $outputDir 'backup_nsp') `
        --type nsp --titleid $TitleId --ncadir $ncaOut
}

$nspPath = Join-Path $nspOut "$TitleId.nsp"
if (-not (Test-Path -LiteralPath $nspPath)) {
    throw "NSP not created: $nspPath"
}

$metaNca = Get-ChildItem -File -LiteralPath $ncaOut -Filter '*.cnmt.nca' | Select-Object -First 1

if (-not $NoVerify) {
    Invoke-Logged -Name '05_verify_nsp_pfs0' -LogDir $logOut -Command {
        & $hactoolItem.FullName --disablekeywarns -k $keysItem.FullName -t pfs0 -i $nspPath
    }

    $programVerifyLog = Join-Path $logOut "06_verify_program_$($programNca.BaseName).log"
    $programInfo = & $hactoolItem.FullName --disablekeywarns -k $keysItem.FullName -t nca -i $programNca.FullName 2>&1
    $programInfo | Tee-Object -FilePath $programVerifyLog | Out-Null
    $programText = $programInfo -join "`n"
    if ($programText -notmatch 'Content Type:\s+Program') { throw "Program NCA verification failed: missing Program content type." }
    if ($programText -notmatch 'Partition Type:\s+ExeFS') { throw "Program NCA verification failed: missing ExeFS section." }
    if ($programText -notmatch 'Partition Type:\s+RomFS') { throw "Program NCA verification failed: missing RomFS section." }
    if ($programText -notmatch 'Partition Type:\s+PFS0') { throw "Program NCA verification failed: missing Logo/PFS0 section." }

    foreach ($nca in @($controlNca, $metaNca)) {
        if (-not $nca) { continue }
        $verifyLog = Join-Path $logOut "06_verify_$($nca.BaseName).log"
        & $hactoolItem.FullName --disablekeywarns -k $keysItem.FullName -t nca -i $nca.FullName 2>&1 |
            Tee-Object -FilePath $verifyLog |
            Out-Null
        if ($LASTEXITCODE -ne 0) {
            throw "NCA verification failed for $($nca.Name). See $verifyLog"
        }
    }
}

$manifest = [ordered]@{
    method = 'nspd-direct'
    createdAt = (Get-Date).ToString('s')
    titleId = $TitleId
    nspdRoot = $nspdRoot
    sourceCodeDir = $codeDir
    sourceLogoDir = $logoSrcDir
    sourceControlDir = $controlSrcDir
    workDir = $workDir
    outputDir = $outputDir
    nspPath = $nspPath
    programNca = $programNca.FullName
    controlNca = $controlNca.FullName
    metaNca = if ($metaNca) { $metaNca.FullName } else { $null }
}
$manifestPath = Join-Path $outputDir 'manifest.json'
$manifest | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $manifestPath -Encoding UTF8

Write-Host '--- RESULT ---'
Write-Host "NSP=$nspPath"
Write-Host "OUTPUT=$outputDir"
Write-Host "WORK=$workDir"
Write-Host "MANIFEST=$manifestPath"
