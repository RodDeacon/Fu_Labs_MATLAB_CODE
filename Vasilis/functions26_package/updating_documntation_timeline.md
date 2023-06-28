# Documenting functions26: A timeline

1. FilenameManager (Done)
   1. FilenameManager (Done)
   2. FilenumberManager (Done)
2. Dict26 (Done)
3. DataDictXXX
4. DataFrame26
5. constants
6. units
   1. UnitClass
   2. ...
7. DataXXX
   1. DataXXX
   2. DataSpectrum
      1. DataSIF
   3. DataOP
   4. DataT1
   5. ...
   
# Want to modify while documenting

1. Rewrite UnitClass with pint. Make sure to accommodate all dependencies in instruments, unit conversions and more.
2. Change the folder/file addition in every instance, from DataXX to QDLFiling to use the os.path.join() method.
3. Fix refractive index issues in all related files (DataSpectrum, DataDictFilenameInfo and everything around them).
4. 