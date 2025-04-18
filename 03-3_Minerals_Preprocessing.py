# import statements
import pandas as pd

# load the original dataframe with scrapped data from mindat.org
file_path = "Data/03-2_Coordinates_Cleaned-dataset.xlsx"

# load the data
df = pd.read_excel(file_path, sheet_name="Enriched")

# Normalize the dataframe based on the minerals
df_normalized = pd.melt(
    df,
    id_vars = ['Mindat Locality ID','Long-form identifier','GUID','Latitude & Longitude','Altitude', 'GeoHash','GRN','Type','Köppen climate type'],
    var_name = 'Mineral'
)

print(df_normalized.head())

# Drop column name mineral as it represents the number of mineral found and not the actual mineral
if 'Mineral' in df_normalized.columns and 'value' in df_normalized.columns:
    df_normalized = df_normalized.drop(columns='Mineral')

# Rename 'value' to 'Mineral' as it represents the actual mineral name
df_normalized = df_normalized.rename(columns={'value': 'Mineral'})

# Check data
print("=== DataFrame Info ===")
print(df_normalized.info())

# Count of minerals
print("\n=== Mineral Counts ===")
print(df_normalized['Mineral'].value_counts())

# Unique Minerals
print("\n=== Unique Minerals ===")
print(df_normalized['Mineral'].nunique())

# Remove rows that have no mineral entry
df_clean = df_normalized[df_normalized['Mineral'].notna() & (df_normalized['Mineral'].str.strip() != '')]

print(df_clean.info())

# Further preprocessing
df_clean = df_clean.copy()
df_clean['Mineral'] = df_clean['Mineral'].str.strip("'").str.strip('"') # get rid of '' wrappers
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'\bvar\.\s*', '', regex=True).str.strip() # get rid of var. for various at the beginning of the mineral name
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'\?\s*$', '', regex=True).str.strip() # Remove question mark at the end of the mineral name
df_clean['Mineral'] = (df_clean['Mineral'].str.replace(r'\b(Group|Subgroup|Supergroup)\b', '', regex=True)
                       .str.replace(r'\s+', ' ', regex=True).str.strip()) # get rid of Group / Supergroup / Subgroup
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'-\([^)]*\)', '', regex=True).str.strip() # get rid of the elements in parentheses as we don't analyse the dominant element further
df_clean['Mineral'] = df_clean['Mineral'].str.replace(r'\s*\(TL\)', '', regex=True).str.strip() # get rid of (TL) parenthesis because it's another way to display a dominant element
unique_minerals = df_clean['Mineral'].unique()
unique_minerals = sorted(unique_minerals)

print(f"Number of unique minerals: {df_clean['Mineral'].nunique()}")

mineral_value_counts = df_clean['Mineral'].value_counts().reset_index()
mineral_value_counts.columns = ['Mineral', 'Count']

mineral_value_counts.to_csv('mineral_value_counts.csv', index=False)

print(mineral_value_counts)

# Create a new dataframe with the columns required for further analysis
selected_columns = [
    'Mindat Locality ID',
    'Latitude & Longitude',
    'Altitude',
    'Type',
    'Köppen climate type',
    'Mineral'
]

df_selected = df_clean[selected_columns].copy()

# Preview the result
print(df_selected.head())

##### Categorize the minerals in broader categories #####

df = df_selected.copy()

# Categories
QUARTZ= {"Opal-AN","Berner Sandstein","Amber", "Carnelian", "Agate","Rutilated Quartz", "Blue Quartz","Oil Quartz", "Sceptre Quartz", "Quartz Gwindel", 'Apophyllite Group', 'Quartz', 'var. Binnite (of Des Cloizeaux)', 'Var. Smoky Quartz', 'var. Duftite-β', 'var. Smoky Quartz', 'Opal', 'var. Silver-bearing Galena', 'var. Adularia', 'var. Thorogummite', 'var. Iron Rose', 'var. Fensterquarz', 'var. Agate', 'var. Amethyst', 'var. Sapphire', 'Amethyst', 'var. Byssolite', 'Cristobalite', 'var. Ruby', 'var. Blue Quartz', 'var. Hyalophane', 'Var. Silver-bearing Galena', 'var. Silver-bearing Tetrahedrite', 'Var. Iron Rose', 'Chalcedony', 'var. Sericite', 'var. Rock Crystal', 'var. Milky Quartz', 'var. Emerald', 'var. Faden Quartz', 'var. Sceptre Quartz', 'var. Chalcedony', 'Fluorapatite', 'var. Pericline', 'Fluorapophyllite-(K)', 'Apatite', 'var. Brecciated Agate', 'var. Quartz Gwindel', 'Citrine', 'Var. Rock Crystal', 'Gwindel', 'var. Rutilated Quartz', 'var. Oligoclase-Albite', 'Brushite', 'Rock Crystal', 'Milky Quartz', 'Silex', 'Smoky Quartz', 'Amphibole', 'Saphir', 'Fluorapophyllite'}

FELDSPAT = {"Perthite", "Oligoclase", "Oligoclase-Andesine", "Oligoclase-Albite", "Albite","Plagioclase", "Sanidine", "Albite", "Microcline", "K Feldspar", "Orthoklas", "Anorthite", "Adularia", "Plagioclase", "Sanidine", "Albite", "Microcline", "Orthoclase", "Labradorite", "Orthoclase", "var. Oligoclase", "var. Andesine", "var. Bytownite", "var. Niobium-bearing Anatase", "Pericline", "Albit", "Anorthite", "Feldspar", "Meionite", "Andesine", "Piemontite",'Almandine-Spessartine Series', 'Feldspat', 'var. Niobium-bearing Anatase', 'Adularia', 'var. Oligoclase', 'Orthoclase', 'Albite', 'var. Bytownite', 'Prehnite', 'Helvine', 'Labradorite', "'Orthoklas'", 'var. Adularia', 'Anorthite', 'var. Pericline', 'Cordierite', 'var. Perthite', 'Sanidine', 'Almandine', 'Zoisite', 'Plagioclase', 'var. Hyalophane', "'Feldspar Group'", 'Grossular', 'var. Andesine', 'K Feldspar', 'var. Labradorite', "'var. Adularia'", 'Microcline'}

GLIMMER = {"Titanium-bearing Biotite", "Muscovite", "Biotite", "Feldspar", "Lautite","Byssolite", "Biotit", "Hornblende Root Name",'Phlogopite', "'Serpentine Subgroup'", 'Muscovite', 'Phlogopite ?', 'Biotite', "'Muscovite-1M'", 'Fuchsite', 'White mica', 'Muscovite-1M', 'Dravite-Schorl Series', 'Phengite', 'Biotit', 'Muskovit', 'Paragonite', 'Var. Phengite', 'Sericite', 'Glimmer'}

CALCIT = {"Cobalt-bearing Calcite", "Fluorcalcioroméite", "Fluorcalcioroméite","Bariopharmacosiderite","Caryinite", "Strunzite","Manganese-bearing Calcite", "Diaspore", "Celestine", "Barium-rich Celestine", "Beryllium-Calcium",'Magnesite', 'Baryte', 'var. Manganese-bearing Fluorapatite', 'Calcite', 'Barite', 'var. Barium-rich Celestine', 'var. Manganese-bearing Calcite', 'var. Cobalt-bearing Calcite', 'Cerussite', 'Pyrite', 'Talc', 'Rosasite', 'var. Chalcedony', 'Aragonite', 'Chalcopyrite', 'Rhodochrosite', 'var. Taraspite', 'Wulfenite', 'Siderite', 'Hydrocerussite', 'Malachite', 'Limonite', 'Azurite', 'Smithsonite', 'Becquerelite', 'Gypsum'}

DOLOMIT = {"Iron-bearing Magnesite", "Dolomite","Iron-bearing Dolomite", "Dolomite", "Kutnohorite",'var. Breunnerite', 'Dolomit', 'Magnesio-hornblende', 'Magnesite', 'Ankerite', 'Magnesio-riebeckite', 'Aragonite', 'Sainfeldite', 'Siderite', 'var. Iron-bearing Dolomite', 'var. Fuchsite', 'Dolomite', 'Magnesiochloritoid'}

CHLORIT = {"Nontronite", "Chamosite-Clinochlore Series", "Chlorite", "Saponite","Parsettensite", "Vandendriesscheite",'Epidote', "Chlorit","Chlorite", "Glauconite", "Serpentine", "Saponite", "Montmorillonite", 'Magnesio-chloritoid', 'Chlorite', 'Chlorite Group', 'Lizardite', 'Goyazite', "'Chlorite Group'", 'Clinochrysotile', 'Dravite', 'Chlorapatite', 'Clinochlore', 'Chamosite', "'Clinochrysotile'", 'Fuchsite', 'Chloritoid'}

GRANAT = {"Almandine-Pyrope Series","Almandine", "Grossular", "Pyrope", "Mangano-Grossular","Almandine", "Grossular", "Pyrope", "Mangano-Grossular", "Spessartine", "Grossular", "Piemontite", 'Grossular', 'Granat','Pyrope', 'Andradite', 'Hessonite', 'Uvarovite', 'Spessartine', 'Helvine', 'Almandine', 'Demantoid', 'Garnet Group'}

SERPENTIN = {"Allalin-gabbro",'Clinohumite', "'Serpentine Subgroup'","Serpentine", "Antigorite", "Chrysotile", 'Beudantite-Segnitite Series', 'Prehnite', 'Ophicalcite', 'Humite Group', "'Clinochrysotile'", 'Talc', 'Lizardite', 'Chrysotile', 'Antigorite', 'Orthoserpierite', 'Antigorite (TL)', 'Caryopilite', 'Serpentine'}

AMPHIBOLE = {"Aegirine-augite", "Roméite", "Roméite", "Crossite", "Tapiolite","Hornblende", "Tremolite", "Actinolite", "Glaucodot","Ferro-actinolite-Tremolite Series",'Pargasite', 'Enstatite', 'Tennantite-(Zn)', 'Tennantite-(Zn) (TL)', "'Hornblende Root Name Group'", 'Actinolite-Ferro-actinolite Series', 'Edenite', 'Hercynite', 'Forsterite', 'Richterite', 'Var. Byssolite', 'Clinozoisite-Epidote Series', 'Rutile', 'Fayalite-Forsterite Series', 'Magnesio-hornblende', 'Winchite', 'Edenite-Pargasite Series', 'Magnesio-riebeckite', 'Actinolite', 'Hornblende', 'Riebeckite Root Name Group', 'Tremolite', 'Actinolite-Tremolite Series', 'Tremolit', 'Ferro-actinolite', "'Amphibole Supergroup'", 'Clinoenstatite', 'Glaucophane', 'Ferri-winchite', 'Diopside', 'Magnesiohastingsite-Pargasite Series', 'Ferro-pargasite', 'Chromite'}

PYROXENE = {"Pyroxene","Metastibnite", "Clinopyroxene","Diopsid", "Augite", "Rhomboclase", "Enargite", "Römerite", "Tschermakite", 'Manganberzeliite', 'Riebeckite', 'Tetradymite', 'Diopside', "'var. Chromium-bearing Diopside'", 'Pyrrhotite', 'Aegirine', 'Enstatite', 'Clinozoisite', 'Tiragalloite', 'Rhodonite', 'Wollastonite', 'Pyrope', 'Hedenbergite', 'Cervantite', 'Acanthite', 'Xilingolite', 'Fayalite', 'Fayalite-Forsterite Series', 'Augite', 'Zincostaurolite (TL)', 'Omphacite', 'Spodumene', 'Metanováčekite', 'Grossular'}

TITANIT = {'Anatase', 'Topaz', 'Titanite', 'Titanit'}

ZIRCON = {"Zirkon", "Schreibersite", 'Thorite', 'Zircon', 'Metamorphic Zircon', 'Zirconolite', 'Xenotime', 'Baddeleyite', 'var. Melanite', 'Sphene'}

RUTIL = {'Brookite', 'Rutil', 'Anatase', 'Cristobalite', 'Rutile'}

MAGNETIT_UND_HAEMATIT = {"Magnetit", "Hämatit", "Iron Rose", 'Hematite', 'Sphalerite', 'Graphite', 'Safflorite', 'Löllingite', 'Goethite', 'Pyrrhotite', 'Spinel', 'Ilmenite', 'Hercynite', 'Ferrarisite', 'Bismuth', 'Limonite', 'Magnetite', 'Bismuthinite', 'Magnesite'}

URANMINERALE = {"Torbernite", "Thermonatrite", "Uranopilite", "Franklinphilite","Uranospinite", "Meta-autunite", "Lavendulan","Pitchblende", "Sklodowskite", "Tyuyamunite", "Metazeunerite", "Studtite", "Arsenuranospathite",'Ullmannite', 'Uraninite', 'Uranophane', 'Parauranophane', 'Coffinite', 'Duftite', 'Zálesíite'}

SILICATE = {"Sphero-cobaltite","Cobaltosite", 'Anthophyllite', 'Kyanite', 'Bastnäsite', 'Epidote', 'Acid-based mineral forms','Alunogen', 'Forsterite', 'Magnesiozippeite', 'Prehnite', 'Schorl', 'Symplesite', 'Muscovite', 'Zeolites', 'Chamosite', "Humite", "Sideronatrite", "Ramsdellite", "Ganterite", "Bayldonite", "Zinnwaldite", "Preisingerite", "Ceylonite", "Clino-suenoite", "Zinczippeite", "Kolfanite", "Långbanite", "Aikinite", "Chalcocite", "Rectorite", "Smolyaninovite", "Columbite-Columbite Series", "Heimite", "Fianelite", "Krutovite", "Hingganite", "Ettringite", "Katophorite", "Titanclinohumite", "Zincolivenite", "Tantalite", "Claraite", "Chrysoberyl", "Rhodochrosite", "Zincalstibite", "Kolfanite", "Sphero-cobaltite", "Smectite", "Morenosite", "Fluorcalciomicrolite", "Sonolite", "Tantalaeschynite", "Coralloite",'Cannizzarite', 'Nesquehonite', 'Cannizzarite', 'Pumpellyite', 'Weilite', 'Greenalite', 'Mansfieldite', 'Ilesite', 'Lagalyite', 'Datolite', 'Galenobismutite', 'Argentopearceite', 'Scheuchzerite', 'Hydroandradite', 'Thaumasite', 'Hinsdalite', 'Plaffeiite', 'Plaffeiite', 'Jimthompsonite', 'Reevesite', 'Illite', 'Breunnerite', 'Cheralite', 'Robinsonite', 'Barroisite', 'Tinzenite', 'Robinsonite', 'Bronzite', 'Humite', 'Eugsterite', 'Starkeyite', 'Szomolnokite', 'Billietite', 'Nováčekite', 'Datolite', 'Emilite', 'Cupropolybasite', 'Jahnsite', 'Picotite', 'Pizgrischite', 'Diabantite', 'Chesterite', 'Cuprosklodowskite', 'Triplite', 'Duftite-β', 'Papierspat', 'Triplite', 'Orthopyroxene', 'Geikielite-Ilmenite Series', 'Zincowoodwardite-1T', 'Dorallcharite', 'Hexahydrite',"Epistilbite", "Hemimorphite","Hydroxylclinohumite", "Scapolite", "Dietrichite", "Emplectite", "Heulandite", "Devilline", "Duhamelite", "Roméite", "Rhabdophane", "Nolanite", "Yingjiangite", "Wiserite", "Eclarite", "Bindheimite", "Tilasite", "Pitticite", "Sagenite (of Saussure)", "Saussurite", "Dewindtite", "Heyrovskýite", "Roméite", "Avicennite", "Voltaite", "Heyrovskýite", "Oligoclase", "Oxy-dravite", "Lipscombite", "Sauconite", "Lindbergite", "Wroewolfeite", "Turtmannite", "Shandite", "Chernovite", "Hörnesite", "Orcelite", "Tučekite", "Scapolite", "Apophyllite", "Eclarite","Haüyne", "Danburite", "Smythite", "Gadolinite", "Columbite", "Elyite", "Allophane", "Yukonite", "Kemmlitzite", "Gadolinite", "Flinkite", "Fougèrite", "Cyanotrichite", "Thomsonite", "Romanèchite", "Mica", "Pyrophanite", "Aeschynite", "Friedelite", "Euxenite", "Microlite", "Melanite", "Brannerite", "Chabazite", "Olivenite", "Wurtzite","Senaite", "Pennine", "Fairfieldite", "Beudantite", "Ardennite", "Chalconatronite", "Graftonite", "Nsutite", "Matildite", "Pyrochlore", "Samarskite", "Crichtonite", "Fergusonite", "Pyrosmalite", "Laitakarite", "Celsian", "Rhombohedral Carbonate", "Topazolite", "Manganese-bearing Fluorapatite", "Franklinphilite","Diallage", "Axinite", "Tephroite", "Muscovite", "Zeolite", "Jadeite", "Aquamarine", "Topazolite", "Nepheline","Kaolinite", "Allanite", "Vermiculite", "Sillénite", "Paarite", "Birnessite", "Rammelsbergite", "Pennantite", "Cookeite", "Phuralumite", "Pseudojohannite", "Osarizawaite", "Maucherite", "Vésigniéite","Kainosite", "Enargite", "Gladite", "Dumortierite", "Ferro-actinolite-Tremolite Series", 'Ilmenite', 'Beryl', 'Erythrite', 'Analcime', 'Apatite', 'Senarmontite', 'Tourmaline', 'Perovskite', 'Diopside', 'Bementite ?', 'Baryte', 'Becquerelite', 'Helvine', 'Forsterite', 'Actinolite', 'Quartz', 'Hematite', 'Rhodonite', 'Staurolite', 'Heterogenite', 'Almandine', 'Stilbite', 'Strontianite', 'Synchysite-(Y)', 'Tsumebite', 'Prehnite', 'Manganberzeliite', 'Kainosite-(Y)', 'Greenockite', 'Marcasite', 'Axinite-(Fe)', 'Takanelite', 'Fluorite', 'Tennantite-(Zn)', 'Cleusonite', 'Scolecite', 'Rhodochrosite', 'Laumontite', 'Fibroferrite', 'Brochantite', 'Clinozoisite', 'Chromite', 'Manganese Oxides', 'Limonite', 'Zinkenite', 'Magnesiochloritoid', 'Violarite', 'Wolframite Group', 'Clinochlore', 'Uraninite', 'Gypsum', 'Spinel', 'Hingganite-(Y)', 'Tenuicrystallite', 'Zincrosasite', 'Hercynite', 'Phenakite', 'Cordierite', 'Bearthite (TL)', 'Andalusite', 'Tripuhyite', 'Djerfisherite', 'Chrysocolla', 'Monazite', 'Sphalerite', 'Pyrophyllite', 'Halloysite', 'Kermesite', 'Kyanite', 'Serpierite', 'Jamesonite', 'Vesuvianite', 'Cervantite', 'Pyrobelonite', 'Yarrowite', 'Valentinite', 'Roscoelite', 'Philipsbornite', 'Mottramite', 'Andradite', 'Armenite', 'Clinohumite', 'Chalcopyrite', 'Tremolite', 'Pyrargyrite', 'Xenotime-(Y)', 'Magnetite', 'Chabazite-Ca', 'Senandorite', 'Valleriite', 'Amphibole (z.\u202fB. Hornblende)', 'Gadolinite-(Y)', 'Bournonite', 'Stellerite', 'Talc', 'Enstatite', 'Lazulite', 'Semseyite', 'Stilpnomelane', 'Cerussite', 'Beyerite', 'Digenite', 'Bavenite', 'Barriospharmacosiderite', 'Natrolite', 'Wollastonite', 'Heulandite-Ca', 'Zoisite', 'Pyrrhotite', 'Aeschynite-(Ce)', 'Tetrahedrite-(Fe)', 'Axinite Group', 'Margarite', 'Stilbite-Ca', 'Pyrolusite', 'Epidote'}

OXIDE = {"Ice", "Ice", "Hisingerite", "Annite", "Kintoreite", "Stolzite", "Magnesite", "Zinczippeite", "Seidozerite", "Zippeite", "Ferri-ghoseite", "Zinczippeite","Chrome-Spinel", "Fe-Nickel Sulfide", "Högbomite", "Böhmite", "Hetaerolite", "Rosickýite", "Ramsdellite", "Molybdite", "Walpurgite", "Tenorite", "Kenocalcioroméite", "Roxbyite", "Geerite", "Pyrite", "Zaccagnaite", "Masuyite", "Feroxyhyte", "Leucoxene", "Zincolivenite", "Specularite", "Feitknechtite", "Heterogenite-3R", "Hollandite", "Pyrite", "Ferrisicklerite", "Leucoxene", "Nickelhexahydrite","Manganohörnesite", "Ktenasite", "Ranciéite-Takanelite Series", "Ribbeite", "Cervelleite", "Krettnichite", "Bursaite", "Hodrušite", "Calderite", "Arseniopleite","Bismite", "Breithauptite", "Ferrisymplesite", "Gunningite", "Manganophyllite", "Wölsendorfite","Bravoite", "Maghemite", "Gadolinite", "Troilite", "Kamacite", "Nickel-iron","Maghemite", "Ilvaite", "Beudantite", "Rozenite","Cassiterite", "Magnetite", "Braunite", "Gabbro", "Hematite", "Lilianite","Hausmannite", "Cuprite", "Manganosite", "Manganite", "Zinc-bearing Staurolite", "Galaxite", "Rösslerite", "Jacobsite", "Djurleite", "Retgersite",'Pyrite', 'Enstatite', 'Bismuth', 'Löllingite', 'Spinel', 'Uvarovite', 'Manganberzeliite', 'Magnesiochromite', 'Beyerite', 'Fluorite', 'Bismuthinite', 'Stibnite', 'Tetra-auricupride', 'Perovskite', 'Baryte', 'Heterogenite', 'Selenite', 'Geigerite', 'Alabandite', 'Strashimirite', 'Corundum', 'Scorodite', 'Limonite', 'Gahnite', 'Guérinite', 'Kasolite', 'Gypsum', 'Thorite', 'Langite', 'Magnetite', 'Zincstaurolite', 'Cervantite', 'Ilmenite', 'Safflorite', 'Cerussite', 'Lazulite', 'Chromite', 'Skutterudite', 'Fibroferrite', 'Beryllite', 'Hematite', 'Linnaeite', 'Symplesite', 'Nickeline', 'Erythrite', 'Cobaltite', 'Uraninite', 'Magnesiochloritoid', 'Zincrosasite', 'Descloizite', 'Hessite'}

SULFIDE = {"Silver-bearing Galena", "Selenium", "Selenium-bearing Galena", "Leadhillite", "Chromium-bearing Diopside", "Psilomelane", "Cosalite", "Cosalite", "Cosalite", "Antlerite", "Paratacamite", "Corkite",'Pyrite', 'Pentlandite', 'Dyscrasite', 'Bornite', 'Chalcodite', 'Mottramite', 'Limonite', 'Tetra-auricupride', 'Barite', 'Anilite', 'Manganberzeliite', 'Pyrrhotite', 'Copper', 'Kermesite', 'Krupkaite', 'Bismuthinite', 'Goethite', 'Langite', 'Mimetite', 'Arsenic', 'Tetrahedrite Subgroup', 'Awaruite', 'Acanthite', 'Wulfenite', 'Chalcopyrite', 'Lepidocrocite', 'Copper-bearing Adamite', 'Arsenopyrite', 'Stibnite', 'Cobaltite', 'Zincrosasite', 'Cuproroméite', 'Stannite', 'Bournonite', 'Strontianite', 'Sulphur', 'Nickelalumite', 'Tremolite', 'Wittichenite', 'Siderite', 'Nickeline', 'Azurite', 'Molybdofornacite', 'Gold', 'Clausthalite', 'Pyrobelonite', 'Galena', 'Mackinawite', 'Hematite', 'Idaite', 'Cinnabar', 'Kobellite', 'Plumbojarosite', 'Pyrargyrite', 'Tennantite-(Cu)', 'Hessite', 'Tetrahedrite-(Zn)', 'Willemseite', 'Marcasite', 'Magnetite', 'Pyrolusite', 'Tyrolite', 'Routhierite', 'Orpiment', 'Realgar', 'Tennantite', 'Millerite', 'Spionkopite', 'Rhodonite', 'Sphalerite', 'Heazlewoodite', 'Empressite', 'Yarrowite', 'Anglesite', 'Skutterudite', 'Covellite', 'Cattierite', 'Bismutite', 'Molybdenite', 'Löllingite', 'Baryte'}

CARBONATE = {"Strontium-bearing Baryte", "Gummite", "Walpurgite", "Bastite", "Scorzalite", "Preisingerite", "Falottaite","Sphero-cobaltite", "Zincostaurolite", "Cuprite", "Rosickyite", "Mixite""Phlogopite ?","Argandite", "Metavoltine","Molybdenite-2H", "Françoisite",'Siderotil', 'Barite', 'Aurichalcite', 'Andalusite', 'Malachite', 'Epsomite', 'Wüstite', 'Cerussite', 'Dolomit', 'Pickeringite', 'Azurite', 'Dolomite', 'Calcite', 'Anglesite', 'Siderite', 'Baryte', 'Fluorite', 'Chalcophyllite', 'Strontium-bearing Piemontite', 'Chalcopyrite', 'Sperrylite', 'Smithsonite', 'Mangano-calcite', 'Hydrozincite'}

PHOSPHATE = {"Bayldonite", "Cualstibite-1M", "Talmessite", "Preisingerite", "Meneghinite", "Gummite", "Rutherfordine", "Bismuth-bearing Tetrahedrite","Molybdite", "Pyrophosphate", "Paroniite", "Swedenite", "Fe-Nickel sulfide","Pearceite-Polybasite Series","Beudantite", "Weilbullite", "Florencite", "Sursassite", "Scheelite", "Arsenoflorencite", "Vochtenite","Euchroite", "Svanbergite", "Strunzite", "Florencite","Tennantite-Tetrahedrite Series", "Ferri-taramite", "Calcioandyrobertsite","Brushite", "Asbecasite", "Argentopentlandite", "Bassetite", "Berthierite", "Bertrandite", 'Variscite', 'Gahnite', 'Apatite', 'Gersdorffite', 'Laumontite', 'Fluorapatite', 'Bastnäsite-(Ce)', 'Bieberite', 'Xenotime', 'Pharmacolite', 'Chalcopyrite', 'Tetrahedrite Subgroup', 'Synchysite-(Y)', 'Cacoxenite', 'Fluorite', 'Vanadinite', 'Skutterudite', 'Silica', 'Pyromorphite', 'Bazzite', 'Milarite', 'Annabergite', 'Arsenopyrite', 'Topaz', 'Prehnite', 'Vivianite', 'Monazite-(Ce)', 'AnglesiteFluorapatite', 'Uraninite', 'Scorodite', 'Garnet', 'Tennantite Subgroup', 'Garnet Group', 'Euclase', 'Mimetite', 'Chrysocolla', 'Smithsonite', 'Xenotime-(Y)', 'Dravite', 'Zoisite', 'Hernandezite', 'Angelsite', 'Hydroxylapatite', 'Heterogenite', 'Azurite', 'Pararealgar', 'Cerussite', 'Synchysite-(Ce)', 'Autunite'}

HALOGENIDE_UND_SALZE =  {"Zanelliite", "Cualstibite", "Fluorapophyllite",'Pickeringite', 'Linarite', 'Fluorite', 'Sphalerite', 'Descloizite', 'Bournonite', 'Epsomite', 'Wulfenite', 'Halite', 'Gypsum'}

METALLE_UND_LEGIERUNGEN = {'Tetra-auricupride', 'Nickelalumite', 'Wairauite', 'Nickel', 'Iron', 'Copper', 'Nickeline', 'Algodonite', 'Gallium', 'Koutekite', 'Cobaltite', 'Taenite', 'Graphite', 'Silver', 'Bismuth', 'Willemseite', 'Domeykite', 'Molybdofornacite', 'Gold'}

ARSENATE = {"Phosphosiderite", "Arseniosiderite", "Arseniosiderite", "Hawleyite", "Minium", "Simonkolleite", "Oxyplumboroméite", "Bismuth-bearing Tetrahedrite", "Zincocopiapite", "Hydrohalloysite", "Martite", "Triphylite", "Marmateite", "Hureaulite", "Stephanite", "Retzian", "Lillianite", "Siderophyllite","Adamite", "Cafarsite", "Johannite", "Grischunite", "Felsőbányaite", "UM2006-20-VO:AsHMnSi", "Nambulite", "Berzeliite", "Tetrahedrite", "Arsenolite", "Jáchymovite", "Reppiaite", "Arsenuranospathite", 'Acanthite', 'Anglesite', 'Jarosite', 'Tooeleite', 'Yarrowite', 'Arsenate', 'Pararammelsbergite', 'Cinnabar', 'Mimetite', 'Symplesite', 'Bismuth', 'Agardite-(La)', 'Pharmacolite', 'Metavanmeersscheite', 'Parasymplesite', 'Boulangerite', 'Sphalerite', 'Scorodite', 'Senarmontite', 'Pharmacosiderite', 'Arsenogoyazite', 'Becquerelite', 'Safflorite', 'Senandorite', 'Wulfenite'}

ALUMINIUM_SILIKATE = {'Zircon', 'Prehnite', 'Kyanite', 'Sphalerite', 'Sillimanite', 'Klockmannite', 'Melilite', 'Staurolite', 'Nebulaite', 'Pseúdoarithmeticite'}

SULFATE_UND_HYDROXIDE = {"Alum", "Stibiocolumbite", "Gonnardite", "Hammarite", "Vigezzite", "Gaylussite", "Carnotite", "Cerianite", "Salzburgite", "Tangdanite", "Woodruffite", "Neotocite", "Crednerite", "Babingtonite", "Barylite", "Sabelliite", "Metatyuyamunite", "Boyleite", "Palenzonaite", "Cosalite", "Seidozerite", "Ferri-ghoseite", "Mitridatite", "Natron", "Goldmanite", "Tellurium", "Wilcoxite", "Tschermigite", "Dypingite", "Pearceite-T2ac", "Palenzonaite", "Thometzekite", "Cornubite", "Batoniite", "Carminite", "Rüdlingerite", "Cabalzarite", "Cornwallite", "Atelestite", "Kupčíkite", "Giessenite", "Coconinoite", "Camérolaite", "Heterosite", "Pistomesite", "Crednerite", "Dussertite", "Uranospathite", "Atacamite", "Fornacite", "Rockbridgeite", "Medaite", "Oxycalciobetafite", "Weibullite", "Cesàrolite", "Natrozippeite", "Rabejacite", "Metaheimite", "Kupčíkite", "UM2006-21-VO:AsHMnSi", "Marthozite", "Crednerite", "Camérolaite", "Fraipontite", "Compreignacite", "Spherocobaltite"

,"Ettringite", "Cualstibite-1M", "Hawleyite", "Szmikite", "Phosphosiderite", "Bassanite", "Beraunite", "Dawsonite", "Parisite", "Trona", "Hydrohetaerolite", "Volborthite", "Heterogenite", "Masuyite", "Sphero-cobaltite", "Asbestos", "Brucite", "Hydroglauberite", "Bementite", "Asbestos", "Bitumen", "Pyrochroite", "Brucite", "Sphero-Cobaltite", "Mesolite", "Marmatite", "Hydromagnesite", "Lazarenkoite", "Manganese-bearing Siderite", "Aikinite", "Heterogenite-3R", "Picropharmacolite", "Chalcocite", "Caledonite", "Tamarugite", "Wad", "Agardite", "Theisite", "Preiswerkite", "Dessauite", "Friedrichite", "Gasparite", "Magnesiocopiapite", "Wallkilldellite", "Parnauite", "Haidingerite", "Wittite","Coquimbite", "Coquimbite", "Coquimbite", "Metatorbernite", "Conichalcite", "Conichalcite", "Conichalcite", "Conichalcite", "Ranciéite", "Whitmoreite","Petroleum", "Mirabilite", "Nahcolite", "Thénardite", "Anhydrite", "Pyroxmangite", "Powellite", "Taraspite", "Copper-sklodowskite","Copiapite", "Cubanite", "Chalconatronite", "Bergslagite", "Posnjakite", "Sursassite", "Chalcoalumite","Plumboagardite", "Natrojarosite", "Halotrichite", "Aluminocopiapite", "Schröckingerite", "Segnitite", "Todorokite", "Hydronováčekite", "Marécottite", "Sarkinite", "Fourmarierite","Chalcanthite", "Synchysite", "Schoepite", "Stibiconite", "Beryllium-Calcium", 'Limonite', 'Gips', 'Magnesite', 'Zeunerite', 'Ammoniozippeite', 'Feldspaite', 'Cerrunoite', 'Kieserite', 'Sulfureaite', 'Stromeyerite', 'Melanterite', 'Gypsum', 'Stilbite', 'Selenite', 'Lepidocrocite'}

SONSTIGE = {'Bastnäsite-(Ce)', 'Arsenic', 'Pyrargyrite', 'Fluorite', 'Selenite', 'Halite', 'Aeschynite-(Ce)', 'Rhodonite', 'Brookite', 'Elbaite', 'Idaite'}

EDELSTEINE = ["Thulite","Ruby", "Uvite", "Tamarugite", "Sapphire","Saphir", "Amber", "Haüyne", "Danburite", "Tansanit", "Saphir", "Rubin", "Smaragd", "Achat", "Diamant", "Amethyst", "Citrin", "Bergkristall", "Rose Quartz", "Tropfenquarz", "Topas", "Turmalin", "Peridot", "Jade", "Granat", "Tsavorit", "Spinell", "Apatit", "Kyanit", "Sphalerit", "Labradorit", "Moonstone", "Tansanit", "Amber", "Jet", "Koralle", "Diamant", "Zirkon", "Fluorit", "Opal", "Pyrit", "Hämatit", "Amber", "Haüyne", "Topas", "Smaragd", "Danburite", "Saphir", "Tansanit"]


# Function that returns the categories for a mineral
def kategorien_ermitteln(mineral):
    kategorien = []
    if mineral in QUARTZ:
        kategorien.append('QUARTZ')
    if mineral in EDELSTEINE:
        kategorien.append('EDELSTEINE')
    if mineral in SONSTIGE:
        kategorien.append('SONSTIGE')
    if mineral in SULFATE_UND_HYDROXIDE:
        kategorien.append('SULFATE_UND_HYDROXIDE')
    if mineral in ALUMINIUM_SILIKATE:
        kategorien.append('ALUMINIUM_SILIKATE')
    if mineral in ARSENATE:
        kategorien.append('ARSENATE')
    if mineral in METALLE_UND_LEGIERUNGEN:
        kategorien.append('METALLE_UND_LEGIERUNGEN')
    if mineral in HALOGENIDE_UND_SALZE:
        kategorien.append('HALOGENIDE_UND_SALZE')
    if mineral in PHOSPHATE:
        kategorien.append('PHOSPHATE')
    if mineral in CARBONATE:
        kategorien.append('CARBONATE')
    if mineral in SULFIDE:
        kategorien.append('SULFIDE')
    if mineral in OXIDE:
        kategorien.append('OXIDE')
    if mineral in SILICATE:
        kategorien.append('SILICATE')
    if mineral in URANMINERALE:
        kategorien.append('URANMINERALE')
    if mineral in MAGNETIT_UND_HAEMATIT:
        kategorien.append('MAGNETIT_UND_HAEMATIT')
    if mineral in RUTIL:
        kategorien.append('RUTIL')
    if mineral in ZIRCON:
        kategorien.append('ZIRCON')
    if mineral in TITANIT:
        kategorien.append('TITANIT')
    if mineral in PYROXENE:
        kategorien.append('PYROXENE')
    if mineral in AMPHIBOLE:
        kategorien.append('AMPHIBOLE')
    if mineral in SERPENTIN:
        kategorien.append('SERPENTIN')
    if mineral in GRANAT:
        kategorien.append('GRANAT')
    if mineral in CHLORIT:
        kategorien.append('CHLORIT')
    if mineral in DOLOMIT:
        kategorien.append('DOLOMIT')
    if mineral in CALCIT:
        kategorien.append('CALCIT')
    if mineral in FELDSPAT:
        kategorien.append('FELDSPAT')
    if mineral in GLIMMER:
        kategorien.append('GLIMMER')

        # If more categories, return the first one, otherwise: "SONSTIGES"
    if kategorien:
        return kategorien[0]  # only the first category
    else:
        return 'SONSTIGES'  # if no category: "SONSTIGES"

    # Assign Category 1
df['Category'] = df['Mineral'].apply(kategorien_ermitteln)

df.to_csv('Data/03-4_Minerals-Categorization_Cleaned-dataset.csv', index=False)
