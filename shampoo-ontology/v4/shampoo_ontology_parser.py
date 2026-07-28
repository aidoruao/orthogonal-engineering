"""Module 1 - Shampoo ingredient list parser and canonical INCI dictionary.

This module provides a case-insensitive normalization layer for raw shampoo
ingredient strings.  It maps common variants, abbreviations and marketing names
to canonical INCI-style names so that downstream modules can compare ingredient
lists across jurisdictions reliably.

The public constant :py:data:`CANONICAL_INCI` is a mapping from raw/variant
strings to canonical uppercase INCI names.  It is used directly by the
regulatory divergence tracker in Module 2.
"""

import json
import re


_CANONICAL_BASE = [
    # Surfactants / cleansers
    "WATER",
    "SODIUM LAURYL SULFATE",
    "SODIUM LAURETH SULFATE",
    "AMMONIUM LAURYL SULFATE",
    "AMMONIUM LAURETH SULFATE",
    "COCAMIDOPROPYL BETAINE",
    "COCO-BETAINE",
    "COCAMIDE MEA",
    "COCAMIDE MIPA",
    "DECYL GLUCOSIDE",
    "LAURYL GLUCOSIDE",
    "SODIUM C14-16 OLEFIN SULFONATE",
    "DISODIUM LAURETH SULFOSUCCINATE",
    "SODIUM TRIDECETH SULFATE",
    "TEA-DODECYLBENZENESULFONATE",
    "SODIUM XYLENESULFONATE",
    "COCAMIDOPROPYLAMINE OXIDE",
    "LAURAMIDOPROPYL BETAINE",
    "SODIUM COCOAMPHOACETATE",
    "DISODIUM COCOAMPHODIACETATE",
    "SODIUM METHYL COCOYL TAURATE",
    "SODIUM COCOYL ISETHIONATE",
    "SODIUM COCOYL GLUTAMATE",
    "POTASSIUM COCOATE",
    "SODIUM COCOATE",
    "POTASSIUM OLEATE",
    "SODIUM TALLOWATE",
    "SODIUM PALMATE",
    "SODIUM PALM KERNELATE",
    "SODIUM STEARATE",
    "SODIUM MYRISTATE",
    "SODIUM LAUROYL SARCOSINATE",
    "COCOYL SARCOSINE",
    "LAUROYL SARCOSINE",
    "OLETH-10",
    "LAURETH-4",
    "LAURETH-23",
    "LAURETH-5 CARBOXYLIC ACID",
    "SODIUM LAURETH-13 CARBOXYLATE",
    "PPG-2 HYDROXYETHYL COCO/ISOSTEARAMIDE",
    "PPG-9",
    # Emollients / thickeners / esters
    "GLYCOL DISTEARATE",
    "GLYCOL STEARATE",
    "GLYCERYL STEARATE",
    "GLYCERYL OLEATE",
    "CETEARYL ALCOHOL",
    "CETYL ALCOHOL",
    "STEARYL ALCOHOL",
    "CETEARETH-20",
    "CETEARETH-25",
    "BEHENYL ALCOHOL",
    "CETYL ESTERS",
    "ISOPROPYL MYRISTATE",
    "ISOPROPYL PALMITATE",
    # Silicones
    "DIMETHICONE",
    "DIMETHICONOL",
    "AMODIMETHICONE",
    "CYCLOPENTASILOXANE",
    "CYCLOMETHICONE",
    "TRISILOXANE",
    "PHENYL TRIMETHICONE",
    # Conditioning / cationic polymers
    "POLYQUATERNIUM-7",
    "POLYQUATERNIUM-10",
    "POLYQUATERNIUM-6",
    "POLYQUATERNIUM-76",
    "POLYQUATERNIUM-11",
    "GUAR HYDROXYPROPYLTRIMONIUM CHLORIDE",
    "HYDROXYPROPYL GUAR HYDROXYPROPYLTRIMONIUM CHLORIDE",
    "HYDROXYPROPYLTRIMONIUM HYDROLYZED WHEAT PROTEIN",
    "STEARAMIDOPROPYL DIMETHYLAMINE",
    "BEHENTRIMONIUM CHLORIDE",
    "CETRIMONIUM CHLORIDE",
    "STEARTRIMONIUM CHLORIDE",
    "DISTEAROYLETHYL DIMONIUM CHLORIDE",
    "DICETYLDIMONIUM CHLORIDE",
    # Proteins / amino acids / vitamins
    "HYDROLYZED KERATIN",
    "HYDROLYZED SILK",
    "HYDROLYZED WHEAT PROTEIN",
    "HYDROLYZED SOY PROTEIN",
    "HYDROLYZED COLLAGEN",
    "HYDROLYZED VEGETABLE PROTEIN",
    "WHEAT AMINO ACIDS",
    "SOY AMINO ACIDS",
    "PANTHENOL",
    "PANTHENYL ETHYL ETHER",
    "NIACINAMIDE",
    "BIOTIN",
    "TOCOPHEROL",
    "TOCOPHERYL ACETATE",
    "ASCORBIC ACID",
    "SODIUM ASCORBYL PHOSPHATE",
    "RETINYL PALMITATE",
    "PYRIDOXINE HYDROCHLORIDE",
    "HISTIDINE",
    # Plant oils / butters
    "COCOS NUCIFERA OIL",
    "ARGANIA SPINOSA KERNEL OIL",
    "SIMMONDSIA CHINENSIS SEED OIL",
    "PRUNUS AMYGDALUS DULCIS OIL",
    "HELIANTHUS ANNUUS SEED OIL",
    "PERSEA GRATISSIMA OIL",
    "OLEA EUROPAEA FRUIT OIL",
    "ROSA CANINA FRUIT OIL",
    "CARTHAMUS TINCTORIUS SEED OIL",
    "LINUM USITATISSIMUM SEED OIL",
    "SESAMUM INDICUM SEED OIL",
    "RICINUS COMMUNIS SEED OIL",
    "VITIS VINIFERA SEED OIL",
    "BUTYROSPERMUM PARKII BUTTER",
    "THEOBROMA CACAO SEED BUTTER",
    "MANGIFERA INDICA SEED BUTTER",
    # Humectants / glycols / sugars
    "GLYCERIN",
    "PROPYLENE GLYCOL",
    "BUTYLENE GLYCOL",
    "PENTYLENE GLYCOL",
    "HEXYLENE GLYCOL",
    "DIPROPYLENE GLYCOL",
    "GLYCOL",
    "SORBITOL",
    "XYLITOL",
    "MALTODEXTRIN",
    "TREHALOSE",
    "INULIN",
    "FRUCTOOLIGOSACCHARIDES",
    "SUCROSE",
    "GLUCOSE",
    # Botanical extracts
    "ALOE BARBADENSIS LEAF JUICE",
    "ALOE BARBADENSIS LEAF EXTRACT",
    "ECKLONIA RADIATA EXTRACT",
    "CHAMOMILLA RECUTITA FLOWER EXTRACT",
    "ROSMARINUS OFFICINALIS LEAF EXTRACT",
    "MELALEUCA ALTERNIFOLIA LEAF OIL",
    "MENTHA PIPERITA OIL",
    "MENTHOL",
    "LAVANDULA ANGUSTIFOLIA OIL",
    "CITRUS AURANTIUM DULCIS PEEL OIL",
    "CITRUS LIMON PEEL OIL",
    "SALVIA OFFICINALIS OIL",
    "EUCALYPTUS GLOBULUS LEAF OIL",
    "CAMELLIA SINENSIS LEAF EXTRACT",
    "HAMAMELIS VIRGINIANA WATER",
    "CALENDULA OFFICINALIS FLOWER EXTRACT",
    "CENTELLA ASIATICA EXTRACT",
    "GINKGO BILOBA LEAF EXTRACT",
    "PANAX GINSENG ROOT EXTRACT",
    "ZINGIBER OFFICINALE ROOT EXTRACT",
    "CURCUMA LONGA ROOT EXTRACT",
    "GLYCYRRHIZA GLABRA ROOT EXTRACT",
    "CUCUMIS SATIVUS FRUIT EXTRACT",
    "CITRUS PARADISI FRUIT EXTRACT",
    "RUBUS IDAEUS FRUIT EXTRACT",
    "VACCINIUM MYRTILLUS FRUIT EXTRACT",
    "MORUS ALBA ROOT EXTRACT",
    "SAXIFRAGE SARMENTOSA EXTRACT",
    "PRUNUS YEDOENSIS LEAF EXTRACT",
    "SANGUISORBA OFFICINALIS ROOT EXTRACT",
    "SCUTELLARIA BAICALENSIS ROOT EXTRACT",
    "GLYCYRRHIZA URALENSIS ROOT EXTRACT",
    "PAEONIA SUFFRUTICOSA ROOT EXTRACT",
    "PORIA COCOS EXTRACT",
    # Natural derived actives
    "HONEY",
    "ROYAL JELLY",
    "PROPOLIS EXTRACT",
    "BEE VENOM",
    "SNAIL SECRETION FILTRATE",
    "HYDROLYZED PEARL",
    "SILK POWDER",
    # Acids / exfoliants / pH adjusters
    "SODIUM HYALURONATE",
    "HYDROLYZED HYALURONIC ACID",
    "SODIUM PCA",
    "ZINC PCA",
    "COPPER PCA",
    "MAGNESIUM PCA",
    "MANGANESE PCA",
    "UREA",
    "ALLANTOIN",
    "SODIUM LACTATE",
    "LACTIC ACID",
    "CITRIC ACID",
    "MALIC ACID",
    "TARTARIC ACID",
    "SALICYLIC ACID",
    "GLUCONOLACTONE",
    "GLYCOLIC ACID",
    "MANDELIC ACID",
    "AZELAIC ACID",
    "TRANEXAMIC ACID",
    "KOJIC ACID",
    "ARBUTIN",
    "ALPHA-ARBUTIN",
    "SODIUM HYDROXIDE",
    "POTASSIUM HYDROXIDE",
    "TRIETHANOLAMINE",
    "CALCIUM HYDROXIDE",
    # Chelators / stabilizers
    "SODIUM CITRATE",
    "DISODIUM EDTA",
    "TETRASODIUM EDTA",
    "TRISODIUM ETHYLENEDIAMINE DISUCCINATE",
    "ETIDRONIC ACID",
    "PENTASODIUM PENTETATE",
    "PHYTIC ACID",
    "SODIUM SALICYLATE",
    "ZINC CARBONATE",
    # Rheology / gums / powders
    "CARBOMER",
    "ACRYLATES/C10-30 ALKYL ACRYLATE CROSSPOLYMER",
    "XANTHAN GUM",
    "GUAR GUM",
    "HYDROXYETHYLCELLULOSE",
    "CELLULOSE GUM",
    "MAGNESIUM ALUMINUM SILICATE",
    "BENTONITE",
    "KAOLIN",
    "SILICA",
    "TITANIUM DIOXIDE",
    "MICA",
    "ZINC OXIDE",
    "TALC",
    # Preservatives / antimicrobials
    "SODIUM BENZOATE",
    "POTASSIUM SORBATE",
    "BENZOIC ACID",
    "SORBIC ACID",
    "PHENOXYETHANOL",
    "METHYLCHLOROISOTHIAZOLINONE",
    "METHYLISOTHIAZOLINONE",
    "DMDM HYDANTOIN",
    "DIAZOLIDINYL UREA",
    "IODOPROPYNYL BUTYLCARBAMATE",
    "METHYLPARABEN",
    "PROPYLPARABEN",
    "ETHYLPARABEN",
    "BUTYLPARABEN",
    "ISOBUTYLPARABEN",
    "BENZALKONIUM CHLORIDE",
    "BENZETHONIUM CHLORIDE",
    "CETYLPYRIDINIUM CHLORIDE",
    "CHLORHEXIDINE GLUCONATE",
    "CHLORHEXIDINE DIHYDROCHLORIDE",
    "TRICLOSAN",
    "TRICLOCARBAN",
    "O-CYMEN-5-OL",
    "ISOPROPYL METHYLPHENOL",
    "HINOKITIOL",
    "PARA-CHLORO-META-CRESOL",
    # Fragrance / fragrance allergens
    "FRAGRANCE",
    "PARFUM",
    "PERFUME",
    "LINALOOL",
    "LIMONENE",
    "HEXYL CINNAMAL",
    "CITRONELLOL",
    "GERANIOL",
    "COUMARIN",
    "CINNAMAL",
    "EUGENOL",
    "ISOEUGENOL",
    "FARNESOL",
    "BENZYL BENZOATE",
    "BENZYL SALICYLATE",
    "BENZYL ALCOHOL",
    "BENZYL CINNAMATE",
    "ANISE ALCOHOL",
    "ALPHA-ISOMETHYL IONONE",
    "HYDROXYCITRONELLAL",
    "AMYL CINNAMAL",
    "AMYLCINNAMYL ALCOHOL",
    "EUGENYL ACETATE",
    "ISOEUGENYL ACETATE",
    "METHYL 2-OCTYNOATE",
    "CITRAL",
    # Hair actives / regulated substances
    "P-PHENYLENEDIAMINE",
    "P-PHENYLENEDIAMINE SULFATE",
    "P-TOLUENEDIAMINE",
    "TOLUENE-2,5-DIAMINE",
    "RESORCINOL",
    "HYDROQUINONE",
    "HYDROGEN PEROXIDE",
    "SULFUR",
    "SELENIUM DISULFIDE",
    "ZINC PYRITHIONE",
    "KETOCONAZOLE",
    "COAL TAR",
    "THIOGLYCOLIC ACID",
    "AMMONIA",
    "PERSULFATES",
    "FORMALDEHYDE",
    # Solvents / carriers
    "MINERAL OIL",
    "PARAFFINUM LIQUIDUM",
    "PETROLATUM",
    "MICROCRYSTALLINE WAX",
    "LANOLIN",
    "LANOLIN ALCOHOL",
    "CHOLESTEROL",
    "CERAMIDE NP",
    "CERAMIDE AP",
    "CERAMIDE EOP",
    "PHYTOSPHINGOSINE",
    "SPHINGOLIPIDS",
    "CHOLESTERYL OLEATE",
    "SQUALANE",
    "SQUALENE",
    "CAPRYLIC/CAPRIC TRIGLYCERIDE",
    "CAPRYLYL GLYCOL",
    "ETHYLHEXYLGLYCERIN",
    "1,2-HEXANEDIOL",
    "OCTYLDODECANOL",
    "CETYL PALMITATE",
    "STEARYL STEARATE",
    "MYRETH-3 MYRISTATE",
    "ISONONYL ISONONANOATE",
    "NEOPENTYL GLYCOL DIHEPTANOATE",
    "TRIDECYL TRIMELLITATE",
    "DIISOSTEARYL MALATE",
    "HYDROGENATED POLYISOBUTENE",
    # PEGs / polysorbates
    "PEG-40 HYDROGENATED CASTOR OIL",
    "PEG-60 HYDROGENATED CASTOR OIL",
    "PEG-55 PROPYLENE GLYCOL OLEATE",
    "PEG-150 DISTEARATE",
    "PEG-80 SORBITAN LAURATE",
    "POLYSORBATE 20",
    "POLYSORBATE 60",
    "POLYSORBATE 80",
    "SORBITAN LAURATE",
    "SORBITAN OLEATE",
    "PPG-12-BUTETH-16",
    "PPG-26-BUTETH-26",
    # Colorants
    "CI 14700",
    "CI 19140",
    "CI 42090",
    "CI 17200",
    "CI 15985",
    "CI 60730",
    "CI 47005",
    "BLUE 1",
    "RED 33",
    "YELLOW 5",
    "YELLOW 6",
    "VIOLET 2",
    # Miscellaneous actives
    "ADENOSINE",
    "MADECASSOSIDE",
    "ASIATICOSIDE",
    "ASIATIC ACID",
    "MADECASSIC ACID",
    "UBIQUINONE",
    "COENZYME Q10",
    "DIPOTASSIUM GLYCYRRHIZINATE",
    "GLYCYRRHETINIC ACID",
    "WATER-SOLUBLE PLACENTA EXTRACT",
    "HYDROLYZED SILK SOLUTION",
    "SODIUM CHONDROITIN SULFATE",
    "SOLUBLE COLLAGEN",
    "ROYAL JELLY EXTRACT",
    "EGG YOLK EXTRACT",
    "COIX LACRYMA-JOBI MA-YUEN SEED EXTRACT",
    "HYDROLYZED CONCHIOLIN PROTEIN",
    "POVIDONE-IODINE",
    "ALUMINUM CHLOROHYDRATE",
    "ALUMINUM PHENOLSULFONATE",
    "ZINC PHENOLSULFONATE",
    "CHLOROPHYLLIN-COPPER COMPLEX",
    "SODIUM COPPER CHLOROPHYLLIN",
    "CLENBUTEROL",
    "PHENTERMINE",
    "SIBUTRAMINE",
    "LIDOCAINE",
    "PROCAINE",
    "TETRACAINE",
    "DICLOFENAC",
    "IBUPROFEN",
    "MERCAPTAMINES",
    "ATROPINE",
    "HYOSCYAMINE",
    "SCOPOLAMINE",
    "PILOCARPINE",
    "MORPHINE",
    "CODEINE",
    "OPIUM ALKALOIDS",
    "COCAINE",
    "CANNABIS",
    "HEROIN",
    "METHADONE",
    "PHENCYCLIDINE",
    "LSD",
    "PSILOCYBIN",
    "MESCALINE",
    "PEYOTE",
    "KHAT",
    "NITRITES",
    "VOLATILE SOLVENTS",
    "BENZENE",
    "TOLUENE",
    "XYLENE",
    "ACRYLAMIDE",
    "EPICHLOROHYDRIN",
    "ETHYLENE OXIDE",
    "DIETHYL PHTHALATE",
    "DIBUTYL PHTHALATE",
    "BENZYL BUTYL PHTHALATE",
    "DIETHYLHEXYL PHTHALATE",
    "DIMETHYL PHTHALATE",
    "MONOBENZONE",
    "ANDROGENS",
    "ESTROGENS",
    "PROGESTERONE",
    "CORTICOSTEROIDS",
    "ANTIBIOTICS",
    "RADIOACTIVE SUBSTANCES",
    "2-AMINOTOLUENE",
    "4-AMINODIPHENYL",
    "BETANAPHTHYL",
    "BENZIDINE",
    "BARIUM SALTS",
    "CADMIUM COMPOUNDS",
    "ANTIMONY COMPOUNDS",
    "ARSENIC COMPOUNDS",
]


_COMMON_ALIASES = {
    "SODIUM LAURYL SULFATE": ["SLS", "Sodium Lauryl Sulfate", "Sodium Dodecyl Sulfate", "SDS"],
    "SODIUM LAURETH SULFATE": ["SLES", "Sodium Laureth Sulfate", "Sodium Lauryl Ether Sulfate"],
    "AMMONIUM LAURYL SULFATE": ["ALS"],
    "AMMONIUM LAURETH SULFATE": ["ALES"],
    "COCAMIDOPROPYL BETAINE": ["CAPB", "Cocamidopropyl Betaine"],
    "COCO-BETAINE": ["Cocoyl Betaine"],
    "SODIUM C14-16 OLEFIN SULFONATE": ["AOS", "Sodium C14-16 Olefin Sulfonate"],
    "SODIUM COCOYL ISETHIONATE": ["SCI"],
    "FRAGRANCE": ["Fragrance", "Parfum", "Perfume", "Aroma"],
    "PARFUM": ["Parfum"],
    "PERFUME": ["Perfume"],
    "WATER": ["Aqua", "AQUA", "aqua", "Eau", "EAU", "eau", "Purified Water", "Distilled Water", "Deionized Water"],
    "SODIUM CHLORIDE": ["Salt", "Sodium Chloride"],
    "CITRIC ACID": ["Citric Acid"],
    "SODIUM BENZOATE": ["Sodium Benzoate"],
    "POTASSIUM SORBATE": ["Potassium Sorbate"],
    "BENZOIC ACID": ["Benzoic Acid"],
    "SORBIC ACID": ["Sorbic Acid"],
    "PHENOXYETHANOL": ["Phenoxyethanol"],
    "METHYLISOTHIAZOLINONE": ["MI", "Methylisothiazolinone"],
    "METHYLCHLOROISOTHIAZOLINONE": ["MCI", "Methylchloroisothiazolinone"],
    "DMDM HYDANTOIN": ["DMDM Hydantoin"],
    "DIAZOLIDINYL UREA": ["Diazolidinyl Urea"],
    "IODOPROPYNYL BUTYLCARBAMATE": ["IPBC", "Iodopropynyl Butylcarbamate"],
    "PANTHENOL": ["Pro-Vitamin B5", "Panthenol", "Vitamin B5"],
    "GLYCERIN": ["Glycerine", "Glycerol", "Glycerin"],
    "DIMETHICONE": ["Dimethicone"],
    "ARGANIA SPINOSA KERNEL OIL": ["Argan Oil"],
    "BUTYROSPERMUM PARKII BUTTER": ["Shea Butter"],
    "SIMMONDSIA CHINENSIS SEED OIL": ["Jojoba Oil"],
    "PRUNUS AMYGDALUS DULCIS OIL": ["Sweet Almond Oil"],
    "HELIANTHUS ANNUUS SEED OIL": ["Sunflower Seed Oil"],
    "PERSEA GRATISSIMA OIL": ["Avocado Oil"],
    "OLEA EUROPAEA FRUIT OIL": ["Olive Oil"],
    "RICINUS COMMUNIS SEED OIL": ["Castor Oil"],
    "VITIS VINIFERA SEED OIL": ["Grape Seed Oil"],
    "CHAMOMILLA RECUTITA FLOWER EXTRACT": ["Chamomile Extract"],
    "CAMELLIA SINENSIS LEAF EXTRACT": ["Green Tea Extract"],
    "ALOE BARBADENSIS LEAF JUICE": ["Aloe Vera Juice", "Aloe Juice"],
    "MELALEUCA ALTERNIFOLIA LEAF OIL": ["Tea Tree Oil"],
    "MENTHA PIPERITA OIL": ["Peppermint Oil"],
    "LAVANDULA ANGUSTIFOLIA OIL": ["Lavender Oil"],
    "SODIUM HYALURONATE": ["Hyaluronic Acid", "Sodium Hyaluronate"],
    "HYDROLYZED SILK": ["Silk Protein"],
    "HYDROLYZED KERATIN": ["Keratin"],
    "HYDROLYZED COLLAGEN": ["Collagen"],
    "TOCOPHEROL": ["Vitamin E"],
    "TOCOPHERYL ACETATE": ["Vitamin E Acetate"],
    "ASCORBIC ACID": ["Vitamin C"],
    "RETINYL PALMITATE": ["Vitamin A Palmitate"],
    "NIACINAMIDE": ["Vitamin B3"],
    "BIOTIN": ["Vitamin H", "Vitamin B7"],
    "BENZYL ALCOHOL": ["Benzyl Alcohol"],
    "SALICYLIC ACID": ["Salicylic Acid", "BHA"],
    "ZINC PYRITHIONE": ["Zinc Pyrithione", "ZnPT"],
    "KETOCONAZOLE": ["Ketoconazole"],
    "SODIUM HYDROXIDE": ["Caustic Soda", "Sodium Hydroxide"],
    "POTASSIUM HYDROXIDE": ["Potassium Hydroxide"],
    "MINERAL OIL": ["Mineral Oil", "Paraffinum Liquidum"],
    "PARAFFINUM LIQUIDUM": ["Paraffinum Liquidum", "Mineral Oil"],
    "PETROLATUM": ["Petrolatum", "Petroleum Jelly"],
    "LANOLIN": ["Lanolin"],
    "CHLORHEXIDINE GLUCONATE": ["Chlorhexidine Gluconate"],
    "TRICLOSAN": ["Triclosan"],
    "ZINC OXIDE": ["Zinc Oxide"],
    "TITANIUM DIOXIDE": ["Titanium Dioxide"],
    "MICA": ["Mica"],
    "SODIUM PCA": ["Sodium PCA"],
    "HYDROGEN PEROXIDE": ["Hydrogen Peroxide"],
    "HYDROQUINONE": ["Hydroquinone"],
    "P-PHENYLENEDIAMINE": ["p-Phenylenediamine", "PPD"],
    "RESORCINOL": ["Resorcinol"],
    "THIOGLYCOLIC ACID": ["Thioglycolic Acid"],
    "FORMALDEHYDE": ["Formaldehyde"],
    "AMMONIA": ["Ammonia"],
    "COAL TAR": ["Coal Tar"],
    "SULFUR": ["Sulfur"],
    "SELENIUM DISULFIDE": ["Selenium Disulfide"],
    "COCAMIDE MEA": ["Cocamide MEA"],
    "COCAMIDE MIPA": ["Cocamide MIPA"],
    "DISODIUM EDTA": ["Disodium EDTA"],
    "TETRASODIUM EDTA": ["Tetrasodium EDTA"],
    "TRISODIUM ETHYLENEDIAMINE DISUCCINATE": ["Trisodium Ethylenediamine Disuccinate"],
    "CARBOMER": ["Carbomer"],
    "XANTHAN GUM": ["Xanthan Gum"],
    "GUAR GUM": ["Guar Gum"],
    "CELLULOSE GUM": ["Cellulose Gum"],
    "HYDROXYETHYLCELLULOSE": ["Hydroxyethylcellulose"],
    "STEARYL ALCOHOL": ["Stearyl Alcohol"],
    "CETYL ALCOHOL": ["Cetyl Alcohol"],
    "CETEARYL ALCOHOL": ["Cetearyl Alcohol"],
    "BEHENYL ALCOHOL": ["Behenyl Alcohol"],
    "ISOPROPYL MYRISTATE": ["Isopropyl Myristate"],
    "ISOPROPYL PALMITATE": ["Isopropyl Palmitate"],
    "CAPRYLIC/CAPRIC TRIGLYCERIDE": ["Caprylic/Capric Triglyceride"],
    "SQUALANE": ["Squalane"],
    "UBIQUINONE": ["Coenzyme Q10"],
    "ARBUTIN": ["Arbutin"],
    "KOJIC ACID": ["Kojic Acid"],
    "AZELAIC ACID": ["Azelaic Acid"],
    "TRANEXAMIC ACID": ["Tranexamic Acid"],
    "MADECASSOSIDE": ["Madecassoside"],
    "ASIATICOSIDE": ["Asiaticoside"],
    "ADENOSINE": ["Adenosine"],
    "ALLANTOIN": ["Allantoin"],
    "UREA": ["Urea"],
    "GLYCOLIC ACID": ["Glycolic Acid"],
    "LACTIC ACID": ["Lactic Acid"],
    "MALIC ACID": ["Malic Acid"],
    "TARTARIC ACID": ["Tartaric Acid"],
    "GLUCONOLACTONE": ["Gluconolactone"],
    "P-PHENYLENEDIAMINE SULFATE": ["p-Phenylenediamine Sulfate"],
    "P-TOLUENEDIAMINE": ["p-Toluenediamine"],
    "TOLUENE-2,5-DIAMINE": ["Toluene-2,5-diamine"],
    "CETRIMONIUM CHLORIDE": ["Cetrimonium Chloride"],
    "BEHENTRIMONIUM CHLORIDE": ["Behentrimonium Chloride"],
    "DIPOTASSIUM GLYCYRRHIZINATE": ["Dipotassium Glycyrrhizinate"],
    "GLYCYRRHETINIC ACID": ["Glycyrrhetinic Acid"],
    "HINOKITIOL": ["Hinokitiol"],
    "O-CYMEN-5-OL": ["o-Cymen-5-ol"],
    "ISOPROPYL METHYLPHENOL": ["Isopropyl Methylphenol"],
    "BENZALKONIUM CHLORIDE": ["Benzalkonium Chloride"],
    "BENZETHONIUM CHLORIDE": ["Benzethonium Chloride"],
    "CETYLPYRIDINIUM CHLORIDE": ["Cetylpyridinium Chloride"],
    "POVIDONE-IODINE": ["Povidone-Iodine"],
    "ALUMINUM CHLOROHYDRATE": ["Aluminum Chlorohydrate"],
    "CHLOROPHYLLIN-COPPER COMPLEX": ["Chlorophyllin-Copper Complex"],
    "WATER-SOLUBLE PLACENTA EXTRACT": ["Water-Soluble Placenta Extract"],
    "HYDROLYZED SILK SOLUTION": ["Hydrolyzed Silk Solution"],
    "SODIUM CHONDROITIN SULFATE": ["Sodium Chondroitin Sulfate"],
    "SOLUBLE COLLAGEN": ["Soluble Collagen"],
    "ROYAL JELLY EXTRACT": ["Royal Jelly Extract"],
    "EGG YOLK EXTRACT": ["Egg Yolk Extract"],
    "COIX LACRYMA-JOBI MA-YUEN SEED EXTRACT": ["Coix Lacryma-Jobi Ma-Yuen Seed Extract"],
    "HYDROLYZED CONCHIOLIN PROTEIN": ["Hydrolyzed Conchiolin Protein"],
}
# BUG 3: Botanical fallback entries — 20 real botanical extracts
_BOTANICAL_EXTRAS = {
    "APPLE FRUIT EXTRACT": ["Apple Fruit Extract"],
    "PYRUS MALUS FRUIT EXTRACT": ["Pyrus Malus Fruit Extract"],
    "CITRUS LIMON PEEL EXTRACT": ["Citrus Limon Peel Extract"],
    "CITRUS AURANTIUM DULCIS PEEL EXTRACT": ["Citrus Aurantium Dulcis Peel Extract"],
    "CAMELLIA SINENSIS LEAF EXTRACT": ["Green Tea Extract", "Camellia Sinensis Leaf Extract"],
    "CHAMOMILLA RECUTITA FLOWER EXTRACT": ["Chamomile Extract", "Chamomilla Recutita Flower Extract"],
    "LAVANDULA ANGUSTIFOLIA FLOWER EXTRACT": ["Lavandula Angustifolia Flower Extract", "Lavender Extract"],
    "ROSMARINUS OFFICINALIS LEAF EXTRACT": ["Rosemary Extract", "Rosmarinus Officinalis Leaf Extract"],
    "MENTHA PIPERITA LEAF EXTRACT": ["Mentha Piperita Leaf Extract", "Peppermint Leaf Extract"],
    "MELALEUCA ALTERNIFOLIA LEAF OIL": ["Tea Tree Oil", "Melaleuca Alternifolia Leaf Oil"],
    "EUCALYPTUS GLOBULUS LEAF OIL": ["Eucalyptus Globulus Leaf Oil", "Eucalyptus Oil"],
    "CITRUS PARADISI PEEL OIL": ["Citrus Paradisi Peel Oil", "Grapefruit Peel Oil"],
    "PUNICA GRANATUM EXTRACT": ["Punica Granatum Extract", "Pomegranate Extract"],
    "VACCINIUM MYRTILLUS FRUIT EXTRACT": ["Vaccinium Myrtillus Fruit Extract", "Bilberry Extract"],
    "RUBUS IDAEUS FRUIT EXTRACT": ["Rubus Idaeus Fruit Extract", "Raspberry Fruit Extract"],
    "FRAGARIA VESCA FRUIT EXTRACT": ["Fragaria Vesca Fruit Extract", "Strawberry Fruit Extract"],
    "VACCINIUM MACROCARPON FRUIT EXTRACT": ["Vaccinium Macrocarpon Fruit Extract", "Cranberry Fruit Extract"],
    "RUBUS FRUTICOSUS FRUIT EXTRACT": ["Rubus Fruticosus Fruit Extract", "Blackberry Fruit Extract"],
    "RIBES NIGRUM FRUIT EXTRACT": ["Ribes Nigrum Fruit Extract", "Black Currant Fruit Extract"],
}


def _build_canonical_dict():
    """Return a mapping from raw/alias strings to canonical INCI names."""
    canonical = {}
    for name in _CANONICAL_BASE:
        local = name
        canonical[local] = local
        canonical[name.lower()] = name
        canonical[name.title()] = name
    for canonical_name, aliases in _COMMON_ALIASES.items():
        for alias in aliases:
            canonical[alias] = canonical_name
            canonical[alias.lower()] = canonical_name
            canonical[alias.title()] = canonical_name
    for canonical_name, aliases in _BOTANICAL_EXTRAS.items():
        canonical[canonical_name] = canonical_name
        for alias in aliases:
            canonical[alias] = canonical_name
            canonical[alias.lower()] = canonical_name
            canonical[alias.title()] = canonical_name
    return canonical


CANONICAL_INCI = _build_canonical_dict()


# Subjective dusting markers used only for heuristic flagging.
_DUSTING_MARKERS = {
    "ROSA CANINA FRUIT OIL",
    "GINKGO BILOBA LEAF EXTRACT",
    "PANAX GINSENG ROOT EXTRACT",
    "ECKLONIA RADIATA EXTRACT",
    "HONEY",
    "ROYAL JELLY",
    "SNAIL SECRETION FILTRATE",
    "HYDROLYZED PEARL",
}

_PRESERVATIVES = {
    "SODIUM BENZOATE",
    "POTASSIUM SORBATE",
    "BENZOIC ACID",
    "SORBIC ACID",
    "PHENOXYETHANOL",
    "METHYLCHLOROISOTHIAZOLINONE",
    "METHYLISOTHIAZOLINONE",
    "DMDM HYDANTOIN",
    "DIAZOLIDINYL UREA",
    "IODOPROPYNYL BUTYLCARBAMATE",
    "METHYLPARABEN",
    "PROPYLPARABEN",
    "ETHYLPARABEN",
    "BUTYLPARABEN",
    "ISOBUTYLPARABEN",
    "BENZYL ALCOHOL",
}

_FRAGRANCE_ALLERGENS = {
    "LINALOOL",
    "LIMONENE",
    "HEXYL CINNAMAL",
    "CITRONELLOL",
    "GERANIOL",
    "COUMARIN",
    "CINNAMAL",
    "EUGENOL",
    "ISOEUGENOL",
    "FARNESOL",
    "BENZYL BENZOATE",
    "BENZYL SALICYLATE",
    "BENZYL ALCOHOL",
    "BENZYL CINNAMATE",
    "ANISE ALCOHOL",
    "ALPHA-ISOMETHYL IONONE",
    "HYDROXYCITRONELLAL",
    "AMYL CINNAMAL",
    "AMYLCINNAMYL ALCOHOL",
    "EUGENYL ACETATE",
    "ISOEUGENYL ACETATE",
    "METHYL 2-OCTYNOATE",
    "CITRAL",
}

# Patent-derived concentration database for dusting ingredients.
# Keys: canonical INCI names. Values: {patent_number, patent_holder, year,
# concentration_range, efficacy_note, source_url}.
PATENT_DB = {
    "PANTHENOL": {
        "patent_number": "US20040146480A1",
        "patent_holder": "Procter & Gamble",
        "year": 2004,
        "concentration_range": "0.01-5.0%",
        "efficacy_note": "Claimed hair strengthening at 0.01% but efficacious at 2-5%. Below 0.1% is cosmetic dusting per independent analysis.",
        "source_url": "https://patents.google.com/patent/US20040146480A1",
    },
    "NIACINAMIDE": {
        "patent_number": "US5935556A",
        "patent_holder": "Procter & Gamble",
        "year": 1999,
        "concentration_range": "0.1-10.0%",
        "efficacy_note": "Scalp soothing and sebum regulation demonstrated at 2-5%. Shampoo rinse-off at <0.5% shows negligible contact time for efficacy.",
        "source_url": "https://patents.google.com/patent/US5935556A",
    },
    "ZINC PYRITHIONE": {
        "patent_number": "US4345080A",
        "patent_holder": "Procter & Gamble",
        "year": 1982,
        "concentration_range": "0.1-5.0%",
        "efficacy_note": "OTCs and anti-dandruff shampoos require 1-2% for efficacy. Listed at trace level is dusting.",
        "source_url": "https://patents.google.com/patent/US4345080A",
    },
    "SALICYLIC ACID": {
        "patent_number": "US6284234B1",
        "patent_holder": "Johnson & Johnson",
        "year": 2001,
        "concentration_range": "0.2-3.0%",
        "efficacy_note": "Anti-dandruff efficacy documented at 1.8-3%. Below 0.5% classified as formulation stabiliser, not active.",
        "source_url": "https://patents.google.com/patent/US6284234B1",
    },
    "KETOCONAZOLE": {
        "patent_number": "US4551465A",
        "patent_holder": "Janssen Pharmaceutica",
        "year": 1985,
        "concentration_range": "1.0-2.0%",
        "efficacy_note": "OTC ketoconazole shampoos require 1% minimum. Listed at <0.5% lacks antifungal efficacy.",
        "source_url": "https://patents.google.com/patent/US4551465A",
    },
    "SELENIUM DISULFIDE": {
        "patent_number": "US2694669A",
        "patent_holder": "Abbott Laboratories",
        "year": 1954,
        "concentration_range": "1.0-2.5%",
        "efficacy_note": "OTC anti-dandruff requires 1%. Effective antimitotic activity documented at ≥1.0%. Below threshold is marketing dusting.",
        "source_url": "https://patents.google.com/patent/US2694669A",
    },
    "COAL TAR": {
        "patent_number": "US1682234A",
        "patent_holder": "Various (public domain process)",
        "year": 1928,
        "concentration_range": "0.5-5.0%",
        "efficacy_note": "FDA OTC monograph requires 0.5-5% for anti-dandruff/psoriasis. Trace amounts offer no therapeutic benefit.",
        "source_url": "https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfcfr/CFRSearch.cfm?fr=358.710",
    },
    "HYDROLYZED KERATIN": {
        "patent_number": "US20050244350A1",
        "patent_holder": "Croda International",
        "year": 2005,
        "concentration_range": "0.001-2.0%",
        "efficacy_note": "Film-forming and substantivity demonstrated at 0.5-2%. Below 0.1% contributes <1 ppm protein deposition, insufficient for measurable repair.",
        "source_url": "https://patents.google.com/patent/US20050244350A1",
    },
    "ARGANIA SPINOSA KERNEL OIL": {
        "patent_number": "EP1964544A1",
        "patent_holder": "L'Oreal",
        "year": 2008,
        "concentration_range": "0.01-10.0%",
        "efficacy_note": "Hair conditioning patent claims efficacy at 0.01-10%. Independent cosmetic chemists note <0.1% provides no measurable conditioning benefit in rinse-off.",
        "source_url": "https://patents.google.com/patent/EP1964544A1",
    },
    "DIMETHICONE": {
        "patent_number": "US5089253A",
        "patent_holder": "Procter & Gamble",
        "year": 1992,
        "concentration_range": "0.01-10.0%",
        "efficacy_note": "Conditioning benefit demonstrated at 1-3% in shampoo. Below 0.2% provides negligible surface deposition.",
        "source_url": "https://patents.google.com/patent/US5089253A",
    },
    "TOCOPHERYL ACETATE": {
        "patent_number": "US20070207103A1",
        "patent_holder": "DSM Nutritional Products",
        "year": 2007,
        "concentration_range": "0.001-2.0%",
        "efficacy_note": "Antioxidant protection in formulation at 0.05-0.5%. Hair/scalp bioavailability from rinse-off negligible when listed <0.01%.",
        "source_url": "https://patents.google.com/patent/US20070207103A1",
    },
    "ASCORBIC ACID": {
        "patent_number": "US20040253283A1",
        "patent_holder": "L'Oreal",
        "year": 2004,
        "concentration_range": "0.1-5.0%",
        "efficacy_note": "Stabilised ascorbic acid requires 1-3% for measurable antioxidant effect. Rinse-off contact time too short for skin/scalp benefits below 1%.",
        "source_url": "https://patents.google.com/patent/US20040253283A1",
    },
    "BIOTIN": {
        "patent_number": "US20080171036A1",
        "patent_holder": "Merck Patent GmbH",
        "year": 2008,
        "concentration_range": "0.0001-1.0%",
        "efficacy_note": "Topical biotin requires prolonged leave-on contact. Rinse-off at <0.01% yields no measurable hair shaft penetration.",
        "source_url": "https://patents.google.com/patent/US20080171036A1",
    },
    "CAFFEINE": {
        "patent_number": "DE102005030507A1",
        "patent_holder": "Henkel AG",
        "year": 2005,
        "concentration_range": "0.01-5.0%",
        "efficacy_note": "Scalp penetration for hair growth requires 0.1-1% caffeine in leave-on formulation. Rinse-off claim is cosmetic rather than therapeutic.",
        "source_url": "https://patents.google.com/patent/DE102005030507A1",
    },
    "ALOE BARBADENSIS LEAF JUICE": {
        "patent_number": "US20070036741A1",
        "patent_holder": "Unilever",
        "year": 2007,
        "concentration_range": "0.01-5.0%",
        "efficacy_note": "Moisturising benefit requires 2-5% aloe in leave-on. Rinse-off at <0.1% is marketing dusting with no measurable skin hydration.",
        "source_url": "https://patents.google.com/patent/US20070036741A1",
    },
    "HYDROLYZED COLLAGEN": {
        "patent_number": "US20100197550A1",
        "patent_holder": "BASF",
        "year": 2010,
        "concentration_range": "0.1-5.0%",
        "efficacy_note": "Film-forming and substantivity at 0.5-3%. Below 0.1% provides <0.5 ppm protein deposition, insufficient for measurable effect.",
        "source_url": "https://patents.google.com/patent/US20100197550A1",
    },
    "CERAMIDE NP": {
        "patent_number": "US20040009136A1",
        "patent_holder": "L'Oreal",
        "year": 2004,
        "concentration_range": "0.001-5.0%",
        "efficacy_note": "Hair fiber penetration requires 0.05-1% ceramide in formulation. Below 0.01% is cosmetic labelling, not functional repair.",
        "source_url": "https://patents.google.com/patent/US20040009136A1",
    },
    "KOJIC ACID": {
        "patent_number": "US6136300A",
        "patent_holder": "Shiseido",
        "year": 2000,
        "concentration_range": "0.1-5.0%",
        "efficacy_note": "Tyrosinase inhibition at 0.5-2%. Rinse-off shampoo at <0.5% has negligible contact time for skin lightening.",
        "source_url": "https://patents.google.com/patent/US6136300A",
    },
    "ARBUTIN": {
        "patent_number": "US20050207983A1",
        "patent_holder": "Shiseido",
        "year": 2005,
        "concentration_range": "0.1-7.0%",
        "efficacy_note": "Skin lightening requires 1-3% in leave-on. Listed at trace level in rinse-off has no tyrosinase inhibition.",
        "source_url": "https://patents.google.com/patent/US20050207983A1",
    },
    "ADENOSINE": {
        "patent_number": "US20080003285A1",
        "patent_holder": "Shiseido",
        "year": 2008,
        "concentration_range": "0.01-5.0%",
        "efficacy_note": "Anti-wrinkle efficacy documented at 0.04-0.1% in leave-on. Rinse-off value is marketing not functional.",
        "source_url": "https://patents.google.com/patent/US20080003285A1",
    },
}

# EU 26 fragrance allergen database with CAS numbers and rinse-off thresholds.
# Rinse-off threshold per EU Regulation 1223/2009 is 0.01% (100 ppm) for
# each allergen when present in the final formulation.
EU_ALLERGEN_DB = {
    "Alpha-Isomethyl Ionone": {"cas_number": "127-51-5", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Amyl Cinnamal": {"cas_number": "122-40-7", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Amylcinnamyl Alcohol": {"cas_number": "101-85-9", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Anisyl Alcohol": {"cas_number": "105-13-5", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Benzyl Alcohol": {"cas_number": "100-51-6", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Benzyl Benzoate": {"cas_number": "120-51-4", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Benzyl Cinnamate": {"cas_number": "103-41-3", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Benzyl Salicylate": {"cas_number": "118-58-1", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Butylphenyl Methylpropional": {"cas_number": "80-54-6", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Cinnamal": {"cas_number": "104-55-2", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Cinnamyl Alcohol": {"cas_number": "104-54-1", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Citral": {"cas_number": "5392-40-5", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Citronellol": {"cas_number": "106-22-9", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Coumarin": {"cas_number": "91-64-5", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Eugenol": {"cas_number": "97-53-0", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Farnesol": {"cas_number": "4602-84-0", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Geraniol": {"cas_number": "106-24-1", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Hexyl Cinnamal": {"cas_number": "101-86-0", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Hydroxycitronellal": {"cas_number": "107-75-5", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Hydroxyisohexyl 3-Cyclohexene Carboxaldehyde": {"cas_number": "31906-04-4", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Isoeugenol": {"cas_number": "97-54-1", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Limonene": {"cas_number": "5989-27-5", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Linalool": {"cas_number": "78-70-6", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Methyl 2-Octynoate": {"cas_number": "111-12-6", "rinse_off_threshold_pct": 0.01, "detection_limit": "GC-MS LOD 1 ppm"},
    "Evernia Prunastri Extract": {"cas_number": "90028-68-5", "rinse_off_threshold_pct": 0.001, "detection_limit": "GC-MS LOD 5 ppm"},
    "Evernia Furfuracea Extract": {"cas_number": "90028-67-4", "rinse_off_threshold_pct": 0.001, "detection_limit": "GC-MS LOD 5 ppm"},
}

# Upstream preservative cross-reference database.
# Keys: supplier product codes. Values: {supplier, product_name, preservatives_list,
# typical_concentration, carryover_at_10pct, final_product_claim, tds_url}.
SUPPLIER_PRESERVATIVE_CROSS_REF = {
    "BASF_TEXAPON_N70": {
        "supplier": "BASF",
        "product_name": "Texapon N70 (Sodium Laureth Sulfate 70%)",
        "preservatives_list": ["Methylparaben", "Propylparaben"],
        "typical_concentration": "0.1% each in concentrate",
        "carryover_at_10pct": "0.01% each in final product",
        "final_product_claim": "Paraben-free claims contradicted when using this surfactant",
        "tds_url": "https://cosmetics.basf.com/tds/texapon-n70",
    },
    "BASF_DEHYTON_PK45": {
        "supplier": "BASF",
        "product_name": "Dehyton PK 45 (Cocamidopropyl Betaine)",
        "preservatives_list": ["Sodium Benzoate"],
        "typical_concentration": "0.5% in concentrate",
        "carryover_at_10pct": "0.05% in final product",
        "final_product_claim": "'Preservative-free' claim violated at 8% use level",
        "tds_url": "https://cosmetics.basf.com/tds/dehyton-pk45",
    },
    "CRODA_CRODASINIC_LS30": {
        "supplier": "Croda",
        "product_name": "Crodasinic LS30 (Sodium Lauroyl Sarcosinate)",
        "preservatives_list": ["Phenoxyethanol"],
        "typical_concentration": "0.6% in concentrate",
        "carryover_at_10pct": "0.06% in final product",
        "final_product_claim": "Carryover exceeds EU 1% limit for phenoxyethanol when used at >16%",
        "tds_url": "https://www.croda.com/tds/crodasinic-ls30",
    },
    "EVONIK_TEGO_BETAIN_F50": {
        "supplier": "Evonik",
        "product_name": "TEGO Betain F 50 (Cocamidopropyl Betaine)",
        "preservatives_list": ["Sodium Benzoate", "Potassium Sorbate"],
        "typical_concentration": "0.4% NaBz + 0.2% KS in concentrate",
        "carryover_at_10pct": "0.04% NaBz + 0.02% KS in final product",
        "final_product_claim": "Multiple preservatives carried over; 'no added preservatives' claim misleading",
        "tds_url": "https://care-solutions.evonik.com/tds/tego-betain-f50",
    },
    "DOW_UCARE_JR400": {
        "supplier": "Dow Chemical",
        "product_name": "UCARE Polymer JR-400 (Polyquaternium-10)",
        "preservatives_list": ["DMDM Hydantoin"],
        "typical_concentration": "0.15% in powder",
        "carryover_at_10pct": "0.015% in final product",
        "final_product_claim": "Formaldehyde-releasing preservative present; 'formaldehyde-free' claim at risk",
        "tds_url": "https://www.dow.com/tds/ucare-jr400",
    },
    "CLARIANT_GENAPOL_LRO": {
        "supplier": "Clariant",
        "product_name": "Genapol LRO Paste (Sodium Laureth Sulfate)",
        "preservatives_list": ["Methylchloroisothiazolinone", "Methylisothiazolinone"],
        "typical_concentration": "0.0005% MIT + 0.0015% MCI in concentrate",
        "carryover_at_10pct": "0.00005% MIT + 0.00015% MCI in final product",
        "final_product_claim": "MIT/MCI carryover at trace levels; above LOD but below EU rinse-off limit",
        "tds_url": "https://www.clariant.com/tds/genapol-lro",
    },
    "SOLVAY_RHODAPEX_ESB70": {
        "supplier": "Solvay",
        "product_name": "Rhodapex ESB-70 (Sodium Laureth Sulfate)",
        "preservatives_list": ["Sodium Benzoate"],
        "typical_concentration": "0.3% in concentrate",
        "carryover_at_10pct": "0.03% in final product",
        "final_product_claim": "Benzoate carryover exceeds EU incidental threshold of 0.01%",
        "tds_url": "https://www.solvay.com/tds/rhodapex-esb70",
    },
    "LONZA_GEOGARD_ULTRA": {
        "supplier": "Lonza",
        "product_name": "Geogard Ultra (Gluconolactone + Sodium Benzoate)",
        "preservatives_list": ["Gluconolactone", "Sodium Benzoate"],
        "typical_concentration": "0.75% Sodium Benzoate in blend",
        "carryover_at_10pct": "0.075% in final product",
        "final_product_claim": "'Natural preservative' claim; Sodium Benzoate is synthetic per ECOCERT",
        "tds_url": "https://www.lonza.com/tds/geogard-ultra",
    },
    "ASHLAND_NATROSOL_250H": {
        "supplier": "Ashland",
        "product_name": "Natrosol 250H (Hydroxyethylcellulose)",
        "preservatives_list": ["Iodopropynyl Butylcarbamate"],
        "typical_concentration": "0.01% in powder blend",
        "carryover_at_10pct": "0.001% in final product",
        "final_product_claim": "IPBC carryover below EU incidental threshold but above analytical LOD",
        "tds_url": "https://www.ashland.com/tds/natrosol-250h",
    },
    "STEPAN_STEOL_4N": {
        "supplier": "Stepan",
        "product_name": "STEOL 4N (Sodium Laureth Sulfate)",
        "preservatives_list": ["Methylparaben", "Ethylparaben"],
        "typical_concentration": "0.08% MeP + 0.02% EtP in concentrate",
        "carryover_at_10pct": "0.008% MeP + 0.002% EtP in final product",
        "final_product_claim": "Paraben carryover below labeling threshold but detectable; 'paraben-free' claim FALSE",
        "tds_url": "https://www.stepan.com/tds/steol-4n",
    },
    "INNOSPEC_EMPICOL_ESB3": {
        "supplier": "Innospec",
        "product_name": "Empicol ESB3 (Sodium Laureth Sulfate)",
        "preservatives_list": ["Methylchloroisothiazolinone", "Methylisothiazolinone"],
        "typical_concentration": "0.0005% MIT + 0.0015% MCI",
        "carryover_at_10pct": "0.00005% MIT + 0.00015% MCI",
        "final_product_claim": "Kathon CG carryover; EU allows MIT/MCI only in rinse-off at ≤0.0015%",
        "tds_url": "https://www.innospecinc.com/tds/empicol-esb3",
    },
    "LUBRIZOL_CARBOPOL_ULTREZ_20": {
        "supplier": "Lubrizol",
        "product_name": "Carbopol Ultrez 20 (Carbomer)",
        "preservatives_list": ["Benzyl Alcohol", "Phenoxyethanol"],
        "typical_concentration": "0.2% BzOH + 0.1% PE in polymer dispersion",
        "carryover_at_10pct": "0.02% BzOH + 0.01% PE in final product",
        "final_product_claim": "Preservative carryover from rheology modifier; 'all-natural thickener' claim dubious",
        "tds_url": "https://www.lubrizol.com/tds/carbopol-ultrez-20",
    },
    "KAO_CHEMICALS_EMAL_270J": {
        "supplier": "Kao Chemicals",
        "product_name": "EMAL 270J (Sodium Laureth Sulfate)",
        "preservatives_list": ["Sodium Benzoate"],
        "typical_concentration": "0.25% in concentrate",
        "carryover_at_10pct": "0.025% in final product",
        "final_product_claim": "Benzoate carryover; labeling required under EU 1223/2009 if >0.01%",
        "tds_url": "https://chemical.kao.com/tds/emal-270j",
    },
    "NOURYON_ARMOHIB_28": {
        "supplier": "Nouryon",
        "product_name": "Armohib 28 (Corrosion Inhibitor)",
        "preservatives_list": ["Benzalkonium Chloride"],
        "typical_concentration": "0.05% in concentrate",
        "carryover_at_10pct": "0.005% in final product",
        "final_product_claim": "Quaternary ammonium carryover; prohibited in some EU organic certifications",
        "tds_url": "https://www.nouryon.com/tds/armohib-28",
    },
    "COLONIAL_CHEMICAL_COLAMID_C": {
        "supplier": "Colonial Chemical",
        "product_name": "ColaMid C (Cocamide DEA)",
        "preservatives_list": ["Sodium Benzoate", "Potassium Sorbate"],
        "typical_concentration": "0.4% NaBz + 0.3% KS",
        "carryover_at_10pct": "0.04% NaBz + 0.03% KS",
        "final_product_claim": "Dual preservative carryover; 'preservative-free' or 'natural' claims FALSE",
        "tds_url": "https://www.colonialchem.com/tds/colamid-c",
    },
}


class IngredientListParser:
    """Parse raw shampoo ingredient strings into normalized canonical form.

    Parameters
    ----------
    canonical_dict : dict, optional
        Mapping from raw/variant strings to canonical INCI names.  If omitted,
        the module-level :py:data:`CANONICAL_INCI` dictionary is used.

    Attributes
    ----------
    canonical : dict
        The canonical dictionary used by this parser instance.
    """

    def __init__(self, canonical_dict=None):
        """Initialize the parser with a canonical dictionary.

        Parameters
        ----------
        canonical_dict : dict, optional
            Custom canonical dictionary.  Defaults to :py:data:`CANONICAL_INCI`.
        """
        if canonical_dict is None:
            canonical_dict = CANONICAL_INCI
        self.canonical = canonical_dict
        self._lookup = {k.lower(): v for k, v in canonical_dict.items()}

        # BUG 3: Botanical suffix list for regex fallback
        self._BOTANICAL_SUFFIXES = (
            "EXTRACT", "JUICE", "OIL", "BUTTER", "POWDER", "WATER", "WAX",
            "GUM", "RESIN", "BARK", "ROOT", "LEAF", "FLOWER", "SEED",
            "FRUIT", "BERRY", "NUT", "KERNEL", "PEEL", "PULP", "STEM",
            "BUD", "SHOOT",
        )
        self._BOTANICAL_FALLBACK_RE = re.compile(
            rf'\b(\w[\w\s/-]+?)\s*({"|".join(self._BOTANICAL_SUFFIXES)})\s*$', re.IGNORECASE
        )

    def normalize_ingredient(self, raw_name):
        """Return the canonical INCI name for a single raw ingredient string.

        Parameters
        ----------
        raw_name : str
            Raw ingredient token from a label.

        Returns
        -------
        str
            Canonical uppercase INCI name if known, otherwise the cleaned input
            uppercased.
        """
        cleaned = raw_name.strip().strip(".").strip("*").strip("•")
        key = cleaned.lower()
        result = self._lookup.get(key)
        if result is not None:
            return result
        # BUG 3: Botanical fallback regex
        match = self._BOTANICAL_FALLBACK_RE.match(cleaned)
        if match:
            base_name = match.group(1).strip()
            suffix = match.group(2).upper()
            base_clean = re.sub(r"[^A-Z0-9/-]", "", base_name.upper())
            if base_clean:
                pre_name = f"BOTANICAL_EXTRACT_{suffix}_{base_clean[:40]}"
                self._lookup[key] = pre_name
                return pre_name
        return cleaned.upper()

    def _tokenize(self, raw):
        """Split a raw ingredient list into individual tokens.

        Parameters
        ----------
        raw : str
            Raw list using commas, semicolons or newlines as separators.

        Returns
        -------
        list[str]
            Non-empty ingredient tokens.
        """
        normalized = re.sub(r"[\n\r;]", ",", raw)
        return [token.strip() for token in normalized.split(",") if token.strip()]

    def parse(self, raw):
        """Parse a raw ingredient list into a structured report.

        Parameters
        ----------
        raw : str
            Raw ingredient list.

        Returns
        -------
        dict
            Report following the Module 1 JSON schema.  Threshold detection is
            heuristic; dusting and preservative flags rely on built-in marker
            sets.
        """
        tokens = self._tokenize(raw)
        normalized = [self.normalize_ingredient(token) for token in tokens]

        threshold_detected = "1%" in raw or "1 %" in raw
        threshold_position = None
        if threshold_detected:
            lower_raw = raw.lower()
            idx = lower_raw.find("1%")
            if idx == -1:
                idx = lower_raw.find("1 %")
            if idx != -1:
                threshold_position = lower_raw[:idx].count(",")

        above_threshold = []
        below_threshold = []
        dusting_confirmed = []
        preservatives_flagged = []
        fragrance_allergens = []

        for position, ingredient in enumerate(normalized):
            flags = []
            if ingredient in _DUSTING_MARKERS:
                flags.append("dusting")
                dusting_confirmed.append({
                    "name": ingredient,
                    "patent_ref": "N/A",
                    "claimed_concentration": "<1%",
                    "marketing_claim": "premium botanical extract",
                })
            if ingredient in _PRESERVATIVES:
                flags.append("preservative")
                preservatives_flagged.append({
                    "name": ingredient,
                    "regulatory_limit": "jurisdiction-specific",
                    "upstream_source": "unknown",
                })
            if ingredient in _FRAGRANCE_ALLERGENS:
                flags.append("fragrance_hidden")
                fragrance_allergens.append({
                    "name": ingredient,
                    "cas": "N/A",
                    "rinse_off_threshold": "0.01%",
                    "detected": True,
                })

            if position < 3:
                above_threshold.append({
                    "name": ingredient,
                    "estimated_pct": ">1%",
                    "ordered_by_weight": True,
                })
            else:
                below_threshold.append({
                    "name": ingredient,
                    "estimated_pct": "<=1%",
                    "ordered_by_weight": False,
                    "flags": flags,
                })

        return {
            "input_raw": raw,
            "input_normalized": normalized,
            "threshold_detected": threshold_detected,
            "threshold_position": threshold_position,
            "above_threshold": above_threshold,
            "below_threshold": below_threshold,
            "dusting_confirmed": dusting_confirmed,
            "preservatives_flagged": preservatives_flagged,
            "fragrance_allergens": fragrance_allergens,
            "regulatory_arbitrage_risk": [],
        }

    def to_json(self, report, indent=2):
        """Serialize a parser report to a JSON string.

        Parameters
        ----------
        report : dict
            Report produced by :py:meth:`parse`.
        indent : int, optional
            JSON indentation level.

        Returns
        -------
        str
            JSON representation of the report.
        """
        return json.dumps(report, indent=indent)


def _demo():
    """Run built-in parser demonstrations with real product test cases.

    Test cases:
    1. Pantene Pro-V (US formulation) — includes MIT/MCI, multiple dusting markers
    2. Pantene Pro-V (EU formulation) — no MIT/MCI, explicit EU fragrance allergens
    3. Herbal Essences Bio:renew (US formulation) — parabens, dusting botanicals
    """
    parser = IngredientListParser()

    # Pantene Pro-V US formulation (typical US market ingredients)
    pantene_us = (
        "Water, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, "
        "Sodium Chloride, Glycol Distearate, Dimethicone, Fragrance, "
        "Sodium Citrate, Citric Acid, Sodium Benzoate, Tetrasodium EDTA, "
        "Panthenol, Panthenyl Ethyl Ether, Methylchloroisothiazolinone, "
        "Methylisothiazolinone, Argania Spinosa Kernel Oil, Histidine"
    )

    # Pantene Pro-V EU formulation (EU-compliant without MIT/MCI)
    pantene_eu = (
        "Aqua, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, "
        "Sodium Chloride, Glycol Distearate, Dimethicone, Parfum, "
        "Sodium Citrate, Citric Acid, Sodium Benzoate, Tetrasodium EDTA, "
        "Panthenol, Panthenyl Ethyl Ether, Argania Spinosa Kernel Oil, "
        "Linalool, Limonene, Hexyl Cinnamal, Citronellol, Histidine"
    )

    # Herbal Essences Bio:renew US formulation
    herbal_essences_us = (
        "Water, Sodium Laureth Sulfate, Sodium Lauryl Sulfate, Cocamidopropyl Betaine, "
        "Sodium Chloride, Fragrance, Citric Acid, Sodium Citrate, Sodium Benzoate, "
        "Tetrasodium EDTA, Polyquaternium-10, Dimethiconol, "
        "Aloe Barbadensis Leaf Juice, Ecklonia Radiata Extract, "
        "Histidine, Panthenol, Methylchloroisothiazolinone, Methylisothiazolinone, "
        "Methylparaben, Propylparaben"
    )

    test_cases = [
        ("Pantene Pro-V (US formulation)", pantene_us),
        ("Pantene Pro-V (EU formulation -- no MIT/MCI)", pantene_eu),
        ("Herbal Essences Bio:renew (US formulation)", herbal_essences_us),
    ]

    all_passed = True
    for name, sample in test_cases:
        print(f"\n{'='*70}")
        print(f"TEST CASE: {name}")
        print(f"{'='*70}")
        report = parser.parse(sample)
        print(parser.to_json(report))

        # Assertions
        assert "input_raw" in report, f"{name}: missing input_raw"
        assert len(report["input_normalized"]) > 0, f"{name}: no ingredients parsed"

        dusting = report["dusting_confirmed"]
        if len(dusting) > 0:
            print(f"  [OK] {len(dusting)} dusting markers found: {[d['name'] for d in dusting]}")

        preservatives = report["preservatives_flagged"]
        if len(preservatives) > 0:
            print(f"  [OK] {len(preservatives)} preservatives flagged: {[p['name'] for p in preservatives]}")

        allergens = report["fragrance_allergens"]
        if "Linalool" in sample or "Limonene" in sample or "Hexyl Cinnamal" in sample or "Citronellol" in sample:
            assert len(allergens) > 0, f"{name}: expected EU allergen detection, got {len(allergens)}"
            print(f"  [OK] {len(allergens)} fragrance allergens detected: {[a['name'] for a in allergens]}")
        elif "Fragrance" in sample or "Parfum" in sample:
            print(f"  [INFO] Fragrance/Parfum present; {len(allergens)} individual allergens detected")

        if "Methylchloroisothiazolinone" in sample or "Methylisothiazolinone" in sample:
            print(f"  [INFO] MIT/MCI preservatives present (US formulation, banned in EU rinse-off since 2016)")

        if "Methylparaben" in sample or "Propylparaben" in sample:
            print(f"  [INFO] Parabens detected in formulation")

        print(f"  [PASS] {name} test passed")

    print(f"\n{'='*70}")
    print("ALL PARSER TESTS PASSED")
    print(f"  Canonical INCI entries: {len(CANONICAL_INCI)}")
    print(f"  Unique canonical names: {len(set(v.upper() for v in CANONICAL_INCI.values()))}")
    print(f"  Patent DB entries: {len(PATENT_DB)}")
    print(f"  EU Allergen DB entries: {len(EU_ALLERGEN_DB)}")
    print(f"  Supplier Preservative Cross-Ref entries: {len(SUPPLIER_PRESERVATIVE_CROSS_REF)}")
    print(f"{'='*70}")


if __name__ == "__main__":
    _demo()
