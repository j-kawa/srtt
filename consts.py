BASE_MAP_POINTS = frozenset([
    "Baranówka",
    "Będzin",
    "Będzin Ksawera",
    "Będzin Miasto",
    "Biała Rawska",
    "Brwinów",
    "Bukowno",
    "Bukowno Przymiarki",
    "Charsznica",
    "Chruszczobród",
    "Chrząstowice Olkuskie",
    "Dąbr.Gór.Strzem. R75",
    "Dąbrowa Górn. Ząbkowice DZA R.4/7",
    "Dąbrowa Górnicza",
    "Dąbrowa Górnicza Gołonóg",
    "Dąbrowa Górnicza Huta Katowice",
    "Dąbrowa Górnicza Huta Katowice R7",
    "Dąbrowa Górnicza Pogoria",
    "Dąbrowa Górnicza Południowa",
    "Dąbrowa Górnicza Sikorka",
    "Dąbrowa Górnicza Strzemieszyce",
    "Dąbrowa Górnicza Towarowa DTA R5",
    "Dąbrowa Górnicza Wschodnia",
    "Dąbrowa Górnicza Ząbkowice",
    "Dąbrowa Górnicza Ząbkowice DZA",
    "Dąbrowa Górnicza Ząbkowice GTB",
    "Dorota",
    "Dziadówki",
    "Gajówka",
    "Gajówka APO",
    "Gniewiecin",
    "Goszcza",
    "Góra Włodowska",
    "Grodzisk Maz. R58",
    "Grodzisk Mazowiecki",
    "Grodzisk Mazowiecki R64",
    "Idzikowice",
    "Idzikowice Roz.12",
    "Idzikowice Roz.18",
    "Jaktorów",
    "Jaroszowiec Olkuski",
    "Jeżówka",
    "Józefinów",
    "Józefinów Roz.2",
    "Juliusz",
    "Kamieńczyce",
    "Katowice",
    "Katowice Janów",
    "Katowice M. Kmb R234",
    "Katowice M. Roz. 233",
    "Katowice Much. KMB",
    "KATOWICE MUCHOWIEC STASZIC",
    "Katowice Szopienice Południowe",
    "Katowice Zawodzie",
    "Klimontów",
    "Knapówka",
    "Knapówka R2",
    "Korytów",
    "Kozioł",
    "Kozioł R12",
    "Kozłów",
    "Kraków Batowice",
    "Kraków Główny",
    "Kraków Przedmieście",
    "Łazy",
    "Łazy Grupa Węglarkowa ŁGW",
    "Łazy Ła",
    "Łazy Łc",
    "Łazy R52",
    "Łuczyce",
    "Miechów",
    "Milanówek",
    "Niedźwiedź",
    "Olkusz",
    "Olszamowice",
    "Opoczno Południe",
    "Parzniew",
    "Piastów",
    "Pilichowice",
    "Pruszków",
    "Przemiarki",
    "Psary",
    "Psary Roz.40",
    "Raciborowice",
    "Sędziszów",
    "Sławków",
    "Słomniki",
    "Słomniki Miasto",
    "Smroków",
    "Sosnowiec Dańdówka",
    "Sosnowiec Gł. pzs R52",
    "Sosnowiec Główny",
    "Sosnowiec Kazimierz",
    "Sosnowiec Kazimierz PZS SKZ1",
    "Sosnowiec Kazimierz PZS SKZ2",
    "Sosnowiec Południowy",
    "Sosnowiec Porąbka",
    "Sprowa",
    "Starzyny",
    "Starzyny R5",
    "Staszic",
    "Stawiska",
    "Strzałki",
    "Szczepanowice",
    "Szeligi",
    "Tunel",
    "Tunel R13",
    "Warszawa Centralna",
    "Warszawa Ochota",
    "Warszawa Ursus",
    "Warszawa Ursus Niedźwiadek",
    "Warszawa Włochy",
    "Warszawa Wschodnia",
    "Warszawa Zach. R10",
    "Warszawa Zach. R19",
    "Warszawa Zachodnia",
    "Wiesiółka",
    "Włoszczowa Północ",
    "Wolbrom",
    "Zarzecze",
    "Zarzecze APO",
    "Zastów",
    "Zawiercie",
    "Zawiercie Borowe Pole",
    "Zawiercie GT",
])

LODZ_DLC_POINTS = frozenset([
    "Bedoń",
    "Dąbrowice Skierniewickie",
    "Gałkówek",
    "Jesionka",
    "Justynów",
    "Koluszki",
    "Koluszki Bęzel.R154",
    "Koluszki PZS R145",
    "Koluszki PZS R154",
    "Koluszki R121",
    "Koluszki R122",
    "Koluszki R59",
    "Krosnowa",
    "Lipce Reymontowskie",
    "Łódź Andrzejów",
    "Łódź Olechów Łoc",
    "Łódź Widzew",
    "Łódź Widzew PZS R3",
    "Łódź Widzew R9",
    "Maków",
    "Międzyborów",
    "Płyćwia",
    "Płyćwia GT",
    "Przyłęk Duży",
    "Puszcza Mariańska",
    "Radziwiłłów Mazowiecki",
    "Rogów",
    "Skierniewice",
    "Skierniewice GT 201-208",
    "Skierniewice M PZS",
    "Skierniewice P PZS",
    "Skierniewice Rawka",
    "Skierniewice S PZS",
    "Sucha Żyrardowska",
    "Wągry",
    "Żakow. Płd Zieleń R7",
    "Żakowice",
    "Żakowice Płd Roz.5",
    "Żakowice Południowe",
    "Żyrardów",
])

INGAME_POINTS = frozenset.union(
    BASE_MAP_POINTS,
    LODZ_DLC_POINTS,
)

MAIN_UNITS = {
    "E186 (Traxx)": "Traxx",
    "E6ACTa (Dragon2)": "Dragon2",
    "E6ACTadb (Dragon2)": "Dragon2",
    "ED250 (Pendolino)": "ED250",
    "EN57 (5B+6B+5B)": "EN57",
    "EN71 (5B+6B+6B+5B)": "EN71",
    "EN76 (22WE)": "Elf",
    "EN96 (34WE)": "Elf",
    "EP07 (4E)": "EP07",
    "EP08 (102E)": "EP08",
    "ET22 (201E)": "ET22",
    "ET25 (Dragon2)": "Dragon2",
    "EU07 (4E)": "EU07",
    "?": "?",
}

BASE_MAP_CONTROLLABLE_POINTS = {
    "Będzin": "B",
    "Biała Rawska": "BR",
    "Bukowno": "Bo",
    "Dąbrowa Górnicza": "DG",
    "Dąbrowa Górnicza Huta Katowice": "DGHK",
    "Dąbrowa Górnicza Wschodnia": "DW",
    "Dąbrowa Górnicza Ząbkowice": "DZ",
    "Dorota": "Dra",
    "Góra Włodowska": "GW",
    "Grodzisk Mazowiecki": "Gr",
    "Idzikowice": "Id",
    "Józefinów": "Jz",
    "Juliusz": "Ju",
    "Katowice": "KO",
    "Katowice Zawodzie": "KZ",
    "Knapówka": "Kn",
    "Korytów": "Kr",
    "Kozłów": "Kz",
    "Kraków Batowice": "BT",
    "Kraków Przedmieście": "KPm",
    "Łazy": "ŁB",
    "Łazy Ła": "ŁA",
    "Łazy Łc": "ŁC",
    "Miechów": "Mi",
    "Niedźwiedź": "Nd",
    "Olszamowice": "Ol",
    "Opoczno Południe": "Op",
    "Pilichowice": "Pi",
    "Pruszków": "Pr",
    "Psary": "Ps",
    "Raciborowice": "Rc",
    "Sławków": "Sl",
    "Słomniki": "Sm",
    "Sosnowiec Gł. pzs R52": "SG5",
    "Sosnowiec Główny": "SG",
    "Sosnowiec Kazimierz": "SKz",
    "Sosnowiec Południowy": "Spł1",
    "Sprowa": "Sp",
    "Starzyny": "Str",
    "Strzałki": "St",
    "Szeligi": "Se",
    "Tunel": "Tl",
    "Warszawa Włochy": "Wł",
    "Włoszczowa Północ": "WP",
    "Zastów": "Zs",
    "Zawiercie": "Zw",
}

LODZ_DLC_CONTROLLABLE_POINTS = {
    "Gałkówek": "G",
    "Koluszki": "Kl",
    "Łódź Andrzejów": "ŁAn",
    "Łódź Widzew": "ŁW",
    "Płyćwia": "Pł",
    "Radziwiłłów Mazowiecki": "RM",
    "Rogów": "Rg",
    "Skierniewice": "Sk",
    "Żakowice Południowe": "ZP",
    "Żyrardów": "Zr",
}

CONTROLLABLE_POINTS = {
    **BASE_MAP_CONTROLLABLE_POINTS,
    **LODZ_DLC_CONTROLLABLE_POINTS,
}

VEHICLE_FAMILIES = {
    "4E": {"length": 15.79, "weight": 79.99, "type": "loco"},
    "E186": {"length": 18.66, "weight": 83.78, "type": "loco"},
    "E6ACTa": {"length": 20.56, "weight": 119.92, "type": "loco"},
    "Ty2": {"length": 22.90, "weight": 105.00, "type": "loco"},
    "201E": {"length": 19.23, "weight": 119.92, "type": "loco"},
    "34WE": {"length": 42.00, "weight": 83.00, "type": "emu"},
    "22WE": {"length": 74.00, "weight": 135.00, "type": "emu"},
    "EN57": {"length": 64.32, "weight": 126.62, "type": "emu"},
    "EN71": {"length": 86.39, "weight": 181.96, "type": "emu"},
    "ED250": {"length": 187.00, "weight": 414.00, "type": "emu"},
    "406Ra": {"length": 12.32, "weight": 23.00, "type": "freight-car"},
    "406Rb": {"length": 12.33, "weight": 23.00, "type": "freight-car"},
    "412W": {"length": 14.03, "weight": 20.00, "type": "freight-car"},
    "408S": {"length": 14.07, "weight": 24.00, "type": "freight-car"},
    "424Z": {"length": 19.91, "weight": 23.52, "type": "freight-car"},
    "441V": {"length": 13.48, "weight": 24.00, "type": "freight-car"},
    "629Z": {"length": 26.65, "weight": 28.52, "type": "freight-car"},
    "434Z": {"length": 19.72, "weight": 18.87, "type": "freight-car"},
    "230-01": {"length": 13.48, "weight": 16.51, "type": "freight-car"},
    "111A": {"length": 24.44, "weight": 40.01, "type": "passenger-car"},
    "112A": {"length": 24.49, "weight": 40.08, "type": "passenger-car"},
    "156A": {"length": 26.55, "weight": 45.53, "type": "passenger-car"},
    "B91": {"length": 26.14, "weight": 45.57, "type": "passenger-car"},
    "G90": {"length": 26.43, "weight": 46.31, "type": "passenger-car"},
    "406A": {"length": 26.40, "weight": 46.10, "type": "passenger-car"},
    "110Ac": {"length": 24.46, "weight": 39.88, "type": "passenger-car"},
}

VEHICLES = {
    "4E/EU07-005": {"family": "4E", "name": "EU07"},
    "4E/EU07-068": {"family": "4E", "name": "EU07"},
    "4E/EU07-070": {"family": "4E", "name": "EU07"},
    "4E/EU07-085": {"family": "4E", "name": "EU07"},
    "4E/EU07-092": {"family": "4E", "name": "EU07"},
    "4E/EU07-096": {"family": "4E", "name": "EU07"},
    "4E/EU07-153": {"family": "4E", "name": "EU07"},
    "4E/EU07-193": {"family": "4E", "name": "EU07"},
    "4E/EU07-241": {"family": "4E", "name": "EU07"},
    "4E/EP07-135": {"family": "4E", "name": "EP07"},
    "4E/EP07-174": {"family": "4E", "name": "EP07"},
    "4E/EP08-001": {"family": "4E", "name": "EP08"},
    "4E/EP08-008": {"family": "4E", "name": "EP08"},
    "4E/EP08-013": {"family": "4E", "name": "EP08"},
    "Traxx/E186-134": {"family": "E186", "name": "Traxx"},
    "Traxx/E186-929": {"family": "E186", "name": "Traxx"},
    "Dragon2/E6ACTa-014": {"family": "E6ACTa", "name": "Dragon2"},
    "Dragon2/E6ACTa-016": {"family": "E6ACTa", "name": "Dragon2"},
    "Dragon2/E6ACTadb-027": {"family": "E6ACTa", "name": "Dragon2"},
    "Dragon2/ET25-002": {"family": "E6ACTa", "name": "Dragon2"},
    "Ty2/Ty2-70": {"family": "Ty2", "name": "Ty2"},
    "Ty2/Ty2-347": {"family": "Ty2", "name": "Ty2"},
    "Ty2/Ty2-477": {"family": "Ty2", "name": "Ty2"},
    "Ty2/Ty2-540": {"family": "Ty2", "name": "Ty2"},
    "201E/ET22-1163": {"family": "201E", "name": "ET22"},
    "201E/ET22-243": {"family": "201E", "name": "ET22"},
    "201E/ET22-256": {"family": "201E", "name": "ET22"},
    "201E/ET22-644": {"family": "201E", "name": "ET22"},
    "201E/ET22-836": {"family": "201E", "name": "ET22"},
    "201E/ET22-911": {"family": "201E", "name": "ET22"},
    "Elf/EN96-001": {"family": "34WE", "name": "Elf"},
    "Elf/EN76-006": {"family": "22WE", "name": "Elf"},
    "Elf/EN76-022": {"family": "22WE", "name": "Elf"},
    "EN57/EN57-009": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-038": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-047": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-206": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-612": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-650": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-919": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1000": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1003": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1051": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1181": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1219": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1316": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1331": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1458": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1567": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1571": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1752": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1755": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1796": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-1821": {"family": "EN57", "name": "EN57"},
    "EN57/EN57-614": {"family": "EN57", "name": "EN57"},
    "EN57/EN71-002": {"family": "EN71", "name": "EN71"},
    "EN57/EN71-004": {"family": "EN71", "name": "EN71"},
    "EN57/EN71-005": {"family": "EN71", "name": "EN71"},
    "EN57/EN71-011": {"family": "EN71", "name": "EN71"},
    "EN57/EN71-015": {"family": "EN71", "name": "EN71"},
    "Pendolino/ED250-001 Variant": {"family": "ED250", "name": "ED250"},
    "Pendolino/ED250-009 Variant": {"family": "ED250", "name": "ED250"},
    "Pendolino/ED250-015 Variant": {"family": "ED250", "name": "ED250"},
    "Pendolino/ED250-018 Variant": {"family": "ED250", "name": "ED250"},
    "406Ra/406Ra_33510079375-1": {"family": "406Ra", "name": "406Ra"},
    "406Ra/406Ra_33517881520-5": {"family": "406Ra", "name": "406Ra"},
    "406Ra/406Ra_33517980031-3": {"family": "406Ra", "name": "406Ra"},
    "406Ra/406Ra_33517982861-1": {"family": "406Ra", "name": "406Ra"},
    "406Ra/406Ra_34517981215-0": {"family": "406Ra", "name": "406Ra"},
    "406Ra/406Rb_84517862699-8": {"family": "406Rb", "name": "406Rb"},
    "412W/412W_v4_364-9 Variant": {"family": "412W", "name": "412W"},
    "412W/412W_v4_364-9_b Variant": {"family": "412W", "name": "412W"},
    "412W/412W_33515356394-5": {"family": "412W", "name": "412W"},
    "412W/412W_33565300118-0": {"family": "412W", "name": "412W"},
    "412W/412W_33565300177-6": {"family": "412W", "name": "412W"},
    "408S/408S": {"family": "408S", "name": "408S"},
    "424Z/424Z": {"family": "424Z", "name": "424Z"},
    "424Z/424Z_brazowy": {"family": "424Z", "name": "424Z"},
    "441V/441V_31516635283-3": {"family": "441V", "name": "441V"},
    "441V/441V_31516635512-5": {"family": "441V", "name": "441V"},
    "629Z/230-01_31514508558-7": {"family": "230-01", "name": "230-01"},
    "629Z/629Z_31514960133-0": {"family": "629Z", "name": "629Z"},
    "629Z/434Z_31514553133-5": {"family": "434Z", "name": "434Z"},
    "11xa/80s/110Ac_50 51 59-78 003-8 Variant": {"family": "110Ac", "name": "PASS"},
    "11xa/80s/110Ac_50 51 59-78 003-8 Variant 80s": {"family": "110Ac", "name": "PASS"},
    "11xa/80s/110Ac_51 51 59-70 048-0 Variant 80s": {"family": "110Ac", "name": "PASS"},
    "11xa/80s/110Ac_51 51 59-80 271-6 Variant 80s": {"family": "110Ac", "name": "PASS"},
    "11xa/111A_50 51 20-00 608-3 Variant": {"family": "111A", "name": "PASS"},
    "11xa/80s/111A_50 51 20-00 608-3 Variant 80s": {"family": "111A", "name": "PASS"},
    "11xa/111A_50 51 20-08 607-7 Variant": {"family": "111A", "name": "PASS"},
    "11xa/80s/111A_50 51 20-08 607-7 Variant 80s": {"family": "111A", "name": "PASS"},
    "11xa/111A_51 51 20-70 829-9 Variant": {"family": "111A", "name": "PASS"},
    "11xa/111A_51 51 20-71 102-0 Variant": {"family": "111A", "name": "PASS"},
    "11xa/112A_50 51 19-00 189-7 Variant": {"family": "112A", "name": "PASS"},
    "11xa/80s/112A_50 51 19-00 189-7 Variant 80s": {"family": "112A", "name": "PASS"},
    "11xa/112A_50 51 19-08 095-8 Variant": {"family": "112A", "name": "PASS"},
    "11xa/80s/112A_50 51 19-08 095-8 Variant 80s": {"family": "112A", "name": "PASS"},
    "11xa/112A_50 51 19-08 136-0 Variant": {"family": "112A", "name": "PASS"},
    "11xa/112A_51 51 19-70 003-4 Variant": {"family": "112A", "name": "PASS"},
    "Z2/b10bmnouz_61512071105_1": {"family": "156A", "name": "PASS"},
    "Z2/b11gmnouz_61512170107-7": {"family": "B91", "name": "PASS"},
    "Z2/a9emnouz_61511970214-5": {"family": "B91", "name": "PASS"},
    "Z2/a9mnouz_61511970234-3": {"family": "B91", "name": "PASS"},
    "Z2/b11mnouz_61512170064-0": {"family": "G90", "name": "PASS"},
    "Z2/b11mnouz_61512170098-8": {"family": "G90", "name": "PASS"},
    "Z2/wrmnouz_61518870191_1": {"family": "406A", "name": "PASS"},
}
