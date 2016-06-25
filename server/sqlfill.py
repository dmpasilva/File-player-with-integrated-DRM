import base64
from Crypto.Hash import SHA256
import config

# Init tables
config.insertRows('crypto.db', 'files', (None, 'IEDCSTEST1', 'test.epub'), 1)
config.insertRows('crypto.db', 'files', (None, 'Goethe (Faust)', 'Faust_Goethe.epub'), 1)
config.insertRows('crypto.db', 'files', (None, 'Antichrist (Nietzsche)', 'Nietzsche_Antichrist.epub'), 1)
config.insertRows('crypto.db', 'files', (None, 'Moby Dick (Herman Melville)', 'Herman_Melville_Moby_Dick.epub'), 1)
config.insertRows('crypto.db', 'files', (None, 'Grimms Fairy Tales by Jacob Grimm and Wilhelm Grimm', 'Grimms_Fairy_Tales_Jacob_Grimm_Wilhelm_Grimm.epub'), 1)