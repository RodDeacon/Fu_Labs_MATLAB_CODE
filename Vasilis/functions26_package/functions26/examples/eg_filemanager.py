from functions26.FilenameManager import FileNumberManager

fnm = FileNumberManager([23, 24, 25, 26,27, 28], 'sif', folder_name='data/NWXPLE')

# print(fnm.filenames)
# print(fnm.multi_file_info) # a dictionary of the fields we fill in (sample name, laser power, etc) when taking data
# print(fnm.multi_data) # list difference in the fields btw each imported file

# print(fnm.__dict__.keys())
#
# print(fnm.size)


print(fnm._get_file_info(fnm.filenames[0]))
# from functions26.DataDictXXX import DataDictFilenameInfo
#
# dict = DataDictFilenameInfo()
# dict.get_info(fnm.filenames[0])
# print(dict)