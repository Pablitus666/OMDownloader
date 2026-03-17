# ============================================================
# Firma automática de cualquier EXE con certificado único
# Walter Pablo Tellez Ayala – Software Developer
# pharmakoz@gmail.com | Bolivia
# ============================================================

param(
    [Parameter(Mandatory = $true)]
    [string]$ExePath
)

$ErrorActionPreference = "Stop"

# ================= CONFIGURACION CERTIFICADO =================

$certName = "Walter_Pablo_Tellez_Ayala_CodeSigning"
$pfxFile = "$PSScriptRoot\$certName.pfx"
$pfxPassword = "Ninibethhermosa789*#*?"   

# Subject profesional completo
$subject = "CN=Walter Pablo Tellez Ayala, O=Software Developer, E=pharmakoz@gmail.com, C=BO"

# ================= FUNCION BUSCAR SIGNTOOL =================

function Get-Signtool {
    Write-Host "[INFO] Buscando signtool.exe..." -ForegroundColor Cyan

    $searchFolders = @(
        "C:\Program Files (x86)\Windows Kits\10\bin",
        "C:\Program Files\Windows Kits\10\bin",
        "C:\Program Files (x86)\Microsoft SDKs\Windows"
    )

    foreach ($folder in $searchFolders) {
        if (Test-Path $folder) {
            $found = Get-ChildItem -Path $folder -Filter signtool.exe -Recurse -ErrorAction SilentlyContinue |
            Where-Object { $_.FullName -like "*\x64\*" } |
            Sort-Object LastWriteTime -Descending |
            Select-Object -First 1

            if ($found) {
                Write-Host "[OK] Signtool encontrado: $($found.FullName)" -ForegroundColor Green
                return $found.FullName
            }
        }
    }

    Write-Error "No se encontro signtool.exe. Instala Windows SDK."
}

# ================= CREAR CERTIFICADO SI NO EXISTE =================

if (-not (Test-Path $pfxFile)) {
    Write-Host "[INFO] Certificado no encontrado. Intentando crearlo..." -ForegroundColor Yellow
    
    try {
        $cert = New-SelfSignedCertificate `
            -Type CodeSigningCert `
            -Subject $subject `
            -KeyAlgorithm RSA `
            -KeyLength 2048 `
            -HashAlgorithm SHA256 `
            -KeyExportPolicy Exportable `
            -NotAfter (Get-Date).AddYears(10) `
            -FriendlyName "Walter_Pablo_Tellez_Ayala_CodeSigning" `
            -CertStoreLocation "Cert:\CurrentUser\My"

        $password = ConvertTo-SecureString -String $pfxPassword -Force -AsPlainText
        Export-PfxCertificate -Cert $cert -FilePath $pfxFile -Password $password | Out-Null
        
        Write-Host "[OK] Certificado creado y exportado: $pfxFile" -ForegroundColor Green
    }
    catch {
        Write-Error "Error creando el certificado: $_"
    }
}
else {
    Write-Host "[OK] Certificado existente encontrado." -ForegroundColor Green
}

# ================= VALIDAR EXE =================

if (-not (Test-Path $ExePath)) {
    Write-Error "EXE no encontrado: $ExePath"
}

# ================= FIRMA =================

$signtool = Get-Signtool
$exeName = Split-Path $ExePath -Leaf

Write-Host "[INFO] Firmando $exeName ..." -ForegroundColor Cyan

& $signtool sign `
    /f $pfxFile `
    /p $pfxPassword `
    /fd SHA256 `
    /tr http://timestamp.digicert.com `
    /td SHA256 `
    "$ExePath"

if ($LASTEXITCODE -ne 0) {
    Write-Error "Error en la firma. Codigo: $LASTEXITCODE"
}

Write-Host "[SUCCESS] $exeName firmado correctamente." -ForegroundColor Green
