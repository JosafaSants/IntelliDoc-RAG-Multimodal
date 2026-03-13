import ssl, certifi, subprocess, os, base64

# Exporta certs da store do Windows
subprocess.run(
    ['powershell', '-Command',
     'Get-ChildItem Cert:\\LocalMachine\\Root | ForEach-Object { [System.IO.File]::WriteAllBytes(("cert_" + $_.Thumbprint + ".cer"), $_.Export("Cert")) }'],
    capture_output=True, text=True
)

# Adiciona ao bundle do certifi
certs_adicionados = 0
with open(certifi.where(), 'a') as bundle:
    for arquivo in os.listdir('.'):
        if arquivo.startswith('cert_') and arquivo.endswith('.cer'):
            with open(arquivo, 'rb') as f:
                dados = f.read()
            if len(dados) > 0:
                pem = '\n-----BEGIN CERTIFICATE-----\n'
                pem += base64.b64encode(dados).decode('ascii')
                pem += '\n-----END CERTIFICATE-----\n'
                bundle.write(pem)
                certs_adicionados += 1
            os.remove(arquivo)

print(f'{certs_adicionados} certificados adicionados!')