@echo File       = %1
@echo Output dir = %2
@"C:\Program Files\LibreOffice\program\soffice.exe" --convert-to pdf --outdir %2 %1
