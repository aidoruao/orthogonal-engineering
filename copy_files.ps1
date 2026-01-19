# Copy all files from UNSAFE_FILES_BACKUP to PROOF_PACKAGE
Copy-Item "C:\Users\Aidor\Downloads\UNSAFE_FILES_BACKUP\refined_inventory.csv" -Destination "C:\Users\Aidor\Downloads\PROOF_PACKAGE\"
Copy-Item "C:\Users\Aidor\Downloads\UNSAFE_FILES_BACKUP\canal_refiner.py" -Destination "C:\Users\Aidor\Downloads\PROOF_PACKAGE\"
Write-Host "Files copied successfully!"
