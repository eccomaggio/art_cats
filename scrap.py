from dataclasses import dataclass, field
# from collections import defaultdict
from typing import List, Any, DefaultDict, Optional

@dataclass
class Sheet:
    """
    Represents a valid excel worksheet; as such, no further validation is made.
    """
    rows: List[List[Any]] = field(default_factory=list)

    def add_row(self, row_data: List[Any]):
        self.rows.append(row_data)

    def get_row(self, row_index: int) -> List[Any]:
        """ Retrieves a row by its index.  """
        if not (0 <= row_index < len(self.rows)):
            raise IndexError("Row index out of bounds.")
        return self.rows[row_index]

    def __len__(self) -> int:
        """ Returns the number of rows in the sheet.  """
        return len(self.rows)



records = [
["ARTBL", "French/English", "", "Hotel Bauer Palazzo", "", "4200 meubles et objets d'art - sélection", "", "", "", "", "", "France", "Paris", "Artcurial SAS", "2023?", "", "102", "28cm", "", "", "7 vacations dont 3 Online Only; The catalogue presents a selection of furniture and works of art from the 4200 lots of the upcoming Hotel Bauer Palazzo sale. Not all lots are illustrated in the catalogue. Find all lots with their complete and detailed description on our website: artcurial.com", "4366, 4367,4368,4369, IT4370, IT4371, IT4372", "20230424, 20230425, 20230426, 20230427", "", "Donated by Jeremy Warren", "308241150"],
["ARTBL", "English", "", "Auction: international art before 1900", "", "three illuminated books of hours from a private collection: rediscovery of three fine codices", "", "", "", "", "", "Switzerland", "Basel", "Beurret & Bailly Auktionen Galerie Widmer", "2022?", "", "40", "28cm", "", "", "", "", "20220323", "", "Donated by Jeremy Warren", "308241189"],
["ARTBL", "English/Chinese", "", "Sale of Fine Chinese Art", "", "", "", "中國書畫、陶瓷及藝術品拍賣會 ", "Zhongguo shu hua, tao ci ji yi shu pin pai mai hui", "", "", "China", "Hongkong", "Rong Bao Zhai (HK) Company Ltc and Associate Fine Arts Auctioneers Limited", "1995?", "", "220?", "29", "", "", "", "", "19951204", "", "Donated by the Ashmolean Museum.", "308241295"],
["ARTBL", "Chinese/English", "", "朵雲軒‘95春季近代字畫拍賣 ", "Duo Yun Xuan ‘95 chun ji jin dai zi hua pai mai", "", "", "’95 spring auction of Duo Yun Xuan contemporary calligraphy and painting", "", "", "", "China", "Shanghai", "Duo Yun Xuan Art Auctioneers", "1995?", "", "230?", "29", "", "", "", "", "19950618", "", "Donated by the Ashmolean Museum.", "308241294"],
["ARTBL", "Chinese", "", "‘94中國藝術品（書畫）拍賣會", "‘94 Zhongguo yi shu pin (shu hua) pai mai hui", "", "", "", "", "", "", "China", "Guangzhou", "Guangzhou Fine Arts Auctioneers", "1994?", "", "200?", "29", "", "", "", "", "19941127", "", "Donated by the Ashmolean Museum.", "308241293"],
["ARTBL", "English / Dutch", "", "Rugs and carpets", "", "From the collection of the late Mr. P. Otten, Amsterdam.", "", "Tapijten ", "", "Uit de verzameling van wijlen de heer Mr. P. Otten te Amsterdam", "", "ne", "Amsterdam", "Sotheby Mak Van Waay B.V.", "[1987?]", "© 1987", "12 pages", "27cm", "", "", "", "461", "19870706", "", "Donated by the Ashmolean Museum.", "308241036", "", ""],
["ARTBL", "English / Chinese", "", "Southeby's Hong Kong autumn sales 2013", "", "40: Sotheby's 40 years in Asia", "", "香港蘇富比2013秋李拍賣", "Xianggang Sufubi 2013 qiu ji pai mai", "40: 蘇富比亞洲四十年", "", "cc", "Hong Kong", "Southeby's Hong Kong", "[2013?]", "", "approximately 42 pages", "27cm", "", "", "", "", "20131004, 20131005, 20131006, 20131007, 20131008", "", "Donated by the Ashmolean Museum.", "308241086", "", ""],
]