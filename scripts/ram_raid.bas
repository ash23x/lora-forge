' ==========================================================
' RAM RAID — Sovereign Asset Extractor
' lora-forge pipeline — Phase 1: Image Extraction
' ==========================================================
' PURPOSE:  Bulk export all images/shapes from ALL PowerPoint
'           slides as 1024x1024 PNGs for LoRA training
'
' USAGE:    1. Drag images from Pinterest/browser onto slides
'           2. Alt+F11 → Insert Module → Paste this
'           3. F5 to run
'           4. All images land as PNGs in the target folder
'
' HOW IT WORKS:
'   .Export forces the GPU render buffer to materialise the
'   actual pixels, not the compressed XML thumbnails that
'   PowerPoint stores internally. That's the trick — you get
'   the full-resolution image data, not a preview.
'
' WHY POWERPOINT:
'   PowerPoint is the most reliable cross-platform visual
'   clipboard. Drag from any browser, any app, any source.
'   No scraping libraries, no API keys, no CORS, no CSP
'   blocking. If you can see it, you can drag it.
' ==========================================================

Sub RAMRaid()
    Dim sld As Slide
    Dim shp As Shape
    Dim i As Integer
    Dim exported As Integer
    Dim skipped As Integer
    Dim savePath As String
    
    ' ═══════════════════════════════════════════════
    ' CONFIGURE: Set your output folder here
    ' ═══════════════════════════════════════════════
    savePath = "D:\lora-forge\raw_images\"
    
    On Error Resume Next
    MkDir Left(savePath, InStrRev(savePath, "\") - 1)
    MkDir savePath
    On Error GoTo 0
    
    i = 1
    exported = 0
    skipped = 0
    
    For Each sld In ActivePresentation.Slides
        For Each shp In sld.Shapes
            
            On Error Resume Next
            shp.Export savePath & "img_" & Format(i, "000") & ".png", ppShapeFormatPNG, 1024, 1024
            
            If Err.Number = 0 Then
                exported = exported + 1
                i = i + 1
            Else
                skipped = skipped + 1
                Err.Clear
            End If
            On Error GoTo 0
            
        Next shp
    Next sld

    MsgBox "RAM RAID COMPLETE" & vbCrLf & vbCrLf & _
           "Exported: " & exported & " images" & vbCrLf & _
           "Skipped:  " & skipped & " non-image shapes" & vbCrLf & _
           "Slides:   " & ActivePresentation.Slides.Count & vbCrLf & vbCrLf & _
           "Output:   " & savePath, _
           vbInformation, "lora-forge — RAM RAID"
End Sub
