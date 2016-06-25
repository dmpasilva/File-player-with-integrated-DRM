# Functions to read .epub files

from ebooklib.epub import *

def read_epub(name, options = None):
    reader = EPub_b(name, options)

    book = reader.load()
    reader.process()

    return book

# rewrite _load() function
class EPub_b(EpubReader):
    def _load(self):
        try:
            temp_file = io.BytesIO(self.file_name)
            self.zf = zipfile.ZipFile(temp_file, 'r', compression = zipfile.ZIP_DEFLATED, allowZip64 = True)
        except zipfile.BadZipfile as bz:
            raise EpubException(0, 'Bad Zip file')
        except zipfile.LargeZipFile as bz:
            raise EpubException(1, 'Large Zip file')

        # 1st check metadata
        self._load_container()
        self._load_opf_file()

        self.zf.close()