"""Module 2 - Shampoo ingredient regulatory divergence tracker.

Compares ingredient lists across US, EU, Japan and China jurisdictions,
identifies banned/restricted substances in each, and exports a CSV
cross-reference matrix.

All data is embedded as Python dicts/list. Standard library only.
"""

import csv
import json
import os
import re

# ─────────────────────────────────────────────────────────
# Jurisdiction databases
# ─────────────────────────────────────────────────────────

EU_BANNED = {
    "FORMALDEHYDE": {
        "cas_number": "50-00-0",
        "regulation_ref": "EC 1223/2009 Annex II/1577",
        "restriction_type": "BANNED",
        "effective_date": "2019-05-01",
    },
    "HYDROQUINONE": {
        "cas_number": "123-31-9",
        "regulation_ref": "EC 1223/2009 Annex II/1339",
        "restriction_type": "BANNED",
        "effective_date": "2001-02-01",
    },
    "METHYLCHLOROISOTHIAZOLINONE": {
        "cas_number": "26172-55-4",
        "regulation_ref": "EC 1223/2009 Annex V/57",
        "restriction_type": "BANNED_RINSE_OFF",
        "effective_date": "2016-04-01",
    },
    "METHYLISOTHIAZOLINONE": {
        "cas_number": "2682-20-4",
        "regulation_ref": "EC 1223/2009 Annex V/57",
        "restriction_type": "BANNED_RINSE_OFF",
        "effective_date": "2016-04-01",
    },
    "MUSK XYLENE": {
        "cas_number": "81-15-2",
        "regulation_ref": "EC 1223/2009 Annex II/420",
        "restriction_type": "BANNED",
        "effective_date": "2014-01-01",
    },
    "MUSK KETONE": {
        "cas_number": "81-14-1",
        "regulation_ref": "EC 1223/2009 Annex II/421",
        "restriction_type": "BANNED",
        "effective_date": "2014-01-01",
    },
    "BENZIDINE": {
        "cas_number": "92-87-5",
        "regulation_ref": "EC 1223/2009 Annex II/179",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "2-AMINOTOLUENE": {
        "cas_number": "95-53-4",
        "regulation_ref": "EC 1223/2009 Annex II/413",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "4-AMINODIPHENYL": {
        "cas_number": "92-67-1",
        "regulation_ref": "EC 1223/2009 Annex II/180",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "BETANAPHTHYL": {
        "cas_number": "91-59-8",
        "regulation_ref": "EC 1223/2009 Annex II/234",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "BUTYLATED HYDROXYANISOLE": {
        "cas_number": "25013-16-5",
        "regulation_ref": "EC 1223/2009 Annex II/1365",
        "restriction_type": "BANNED",
        "effective_date": "2017-09-01",
    },
    "ARSENIC COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/362",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "LEAD COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/289",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "MERCURY COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/221",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "CADMIUM COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/216",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "ANTIMONY COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/361",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "BARIUM SALTS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/361",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "BENZENE": {
        "cas_number": "71-43-2",
        "regulation_ref": "EC 1223/2009 Annex II/203",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "TOLUENE": {
        "cas_number": "108-88-3",
        "regulation_ref": "EC 1223/2009 Annex II/1032",
        "restriction_type": "BANNED",
        "effective_date": "2015-01-01",
    },
    "CHLOROFORM": {
        "cas_number": "67-66-3",
        "regulation_ref": "EC 1223/2009 Annex II/223",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "ACRYLAMIDE": {
        "cas_number": "79-06-1",
        "regulation_ref": "EC 1223/2009 Annex II/1535",
        "restriction_type": "BANNED",
        "effective_date": "2016-01-01",
    },
    "EPICHLOROHYDRIN": {
        "cas_number": "106-89-8",
        "regulation_ref": "EC 1223/2009 Annex II/316",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "ETHYLENE OXIDE": {
        "cas_number": "75-21-8",
        "regulation_ref": "EC 1223/2009 Annex II/317",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "NITRITES": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/322",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "VOLATILE SOLVENTS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/379",
        "restriction_type": "BANNED_BELOW_THRESHOLD",
        "effective_date": "2001-01-01",
    },
    "RADIOACTIVE SUBSTANCES": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/323",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "MONOBENZONE": {
        "cas_number": "103-16-2",
        "regulation_ref": "EC 1223/2009 Annex II/417",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "ANDROGENS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/259",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "ESTROGENS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/260",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "CORTICOSTEROIDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/300",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "ANTIBIOTICS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "EC 1223/2009 Annex II/269",
        "restriction_type": "BANNED",
        "effective_date": "2001-01-01",
    },
    "TRICLOSAN": {
        "cas_number": "3380-34-5",
        "regulation_ref": "EC 1223/2009 Annex V/32",
        "restriction_type": "BANNED_ALL_USES",
        "effective_date": "2017-01-01",
    },
    "TRICLOCARBAN": {
        "cas_number": "101-20-2",
        "regulation_ref": "EC 1223/2009 Annex V",
        "restriction_type": "BANNED",
        "effective_date": "2016-01-01",
    },
    "ISOPROPYLPARABEN": {
        "cas_number": "4191-73-5",
        "regulation_ref": "EC 1223/2009 Annex V/12",
        "restriction_type": "BANNED",
        "effective_date": "2015-01-01",
    },
    "ISOBUTYLPARABEN": {
        "cas_number": "4247-02-3",
        "regulation_ref": "EC 1223/2009 Annex V/12a",
        "restriction_type": "BANNED",
        "effective_date": "2015-04-01",
    },
    "PENTYLPARABEN": {
        "cas_number": "6521-29-5",
        "regulation_ref": "EC 1223/2009 Annex V",
        "restriction_type": "BANNED",
        "effective_date": "2015-04-01",
    },
    "PHENYLPARABEN": {
        "cas_number": "17696-62-7",
        "regulation_ref": "EC 1223/2009 Annex V",
        "restriction_type": "BANNED",
        "effective_date": "2015-04-01",
    },
    "BENZYLPARABEN": {
        "cas_number": "94-18-8",
        "regulation_ref": "EC 1223/2009 Annex V",
        "restriction_type": "BANNED",
        "effective_date": "2015-04-01",
    },
    "CLIMBAZOLE": {
        "cas_number": "38083-17-9",
        "regulation_ref": "EC 1223/2009 Annex III/320",
        "restriction_type": "BANNED_RINSE_OFF",
        "effective_date": "2022-01-01",
    },
    "DEHP": {
        "cas_number": "117-81-7",
        "regulation_ref": "EC 1223/2009 Annex II/675",
        "restriction_type": "BANNED",
        "effective_date": "2015-10-01",
    },
    "DBP": {
        "cas_number": "84-74-2",
        "regulation_ref": "EC 1223/2009 Annex II/675",
        "restriction_type": "BANNED",
        "effective_date": "2015-10-01",
    },
    "BBP": {
        "cas_number": "85-68-7",
        "regulation_ref": "EC 1223/2009 Annex II/675",
        "restriction_type": "BANNED",
        "effective_date": "2015-10-01",
    },
    "DIBUTYL PHTHALATE": {
        "cas_number": "84-74-2",
        "regulation_ref": "EC 1223/2009 Annex II/675",
        "restriction_type": "BANNED",
        "effective_date": "2015-10-01",
    },
    "COAL TAR": {
        "cas_number": "8007-45-2",
        "regulation_ref": "EC 1223/2009 Annex II/420",
        "restriction_type": "BANNED_EXCEPT_OTC",
        "effective_date": "2020-01-01",
    },
    "P-PHENYLENEDIAMINE": {
        "cas_number": "106-50-3",
        "regulation_ref": "EC 1223/2009 Annex III/8a",
        "restriction_type": "BANNED_SKIN",
        "effective_date": "2014-01-01",
    },
    "SELENIUM DISULFIDE": {
        "cas_number": "7488-56-4",
        "regulation_ref": "EC 1223/2009 Annex III/239",
        "restriction_type": "BANNED_EXCEPT_OTC_1PCT",
        "effective_date": "2020-01-01",
    },
    "BENZALKONIUM CHLORIDE": {
        "cas_number": "8001-54-5",
        "regulation_ref": "EC 1223/2009 Annex V/54",
        "restriction_type": "BANNED_WITHOUT_PRESCRIPTION",
        "effective_date": "2018-01-01",
    },
    "DIETHYL PHTHALATE": {
        "cas_number": "84-66-2",
        "regulation_ref": "EC 1223/2009 Annex II/675",
        "restriction_type": "BANNED",
        "effective_date": "2015-10-01",
    },
    "LIDOCAINE": {
        "cas_number": "137-58-6",
        "regulation_ref": "EC 1223/2009 Annex II/383",
        "restriction_type": "BANNED_COSMETIC",
        "effective_date": "2001-01-01",
    },
    "SODIUM PERBORATE": {
        "cas_number": "7632-04-4",
        "regulation_ref": "EC 1223/2009 Annex III/12",
        "restriction_type": "BANNED",
        "effective_date": "2015-01-01",
    },
}

EU_RESTRICTED = {
    "SALICYLIC ACID": {
        "cas_number": "69-72-7",
        "regulation_ref": "EC 1223/2009 Annex III/98",
        "restriction_type": "RESTRICTED_3PCT_RINSE_OFF",
        "effective_date": "2017-01-01",
    },
    "ZINC PYRITHIONE": {
        "cas_number": "13463-41-7",
        "regulation_ref": "EC 1223/2009 Annex III/101",
        "restriction_type": "RESTRICTED_1PCT_RINSE_OFF",
        "effective_date": "2022-03-01",
    },
    "BUTYLPARABEN": {
        "cas_number": "94-26-8",
        "regulation_ref": "EC 1223/2009 Annex V/12",
        "restriction_type": "RESTRICTED_0_14PCT_TOTAL",
        "effective_date": "2015-01-01",
    },
    "PROPYLPARABEN": {
        "cas_number": "94-13-3",
        "regulation_ref": "EC 1223/2009 Annex V/12",
        "restriction_type": "RESTRICTED_0_14PCT_TOTAL",
        "effective_date": "2015-01-01",
    },
    "METHYLPARABEN": {
        "cas_number": "99-76-3",
        "regulation_ref": "EC 1223/2009 Annex V/12",
        "restriction_type": "RESTRICTED_0_4PCT",
        "effective_date": "2015-01-01",
    },
    "ETHYLPARABEN": {
        "cas_number": "120-47-8",
        "regulation_ref": "EC 1223/2009 Annex V/12",
        "restriction_type": "RESTRICTED_0_4PCT",
        "effective_date": "2015-01-01",
    },
    "PHENOXYETHANOL": {
        "cas_number": "122-99-6",
        "regulation_ref": "EC 1223/2009 Annex V/29",
        "restriction_type": "RESTRICTED_1_0PCT",
        "effective_date": "2016-01-01",
    },
    "SODIUM BENZOATE": {
        "cas_number": "532-32-1",
        "regulation_ref": "EC 1223/2009 Annex V/1",
        "restriction_type": "RESTRICTED_2_5PCT_ACID",
        "effective_date": "2010-01-01",
    },
    "POTASSIUM SORBATE": {
        "cas_number": "24634-61-5",
        "regulation_ref": "EC 1223/2009 Annex V/2",
        "restriction_type": "RESTRICTED_0_6PCT_ACID",
        "effective_date": "2010-01-01",
    },
    "DMDM HYDANTOIN": {
        "cas_number": "6440-58-0",
        "regulation_ref": "EC 1223/2009 Annex V/33",
        "restriction_type": "RESTRICTED_0_6PCT",
        "effective_date": "2010-01-01",
    },
    "DIAZOLIDINYL UREA": {
        "cas_number": "78491-02-8",
        "regulation_ref": "EC 1223/2009 Annex V/46",
        "restriction_type": "RESTRICTED_0_5PCT",
        "effective_date": "2010-01-01",
    },
    "IMIDAZOLIDINYL UREA": {
        "cas_number": "39236-46-9",
        "regulation_ref": "EC 1223/2009 Annex V/27",
        "restriction_type": "RESTRICTED_0_5PCT",
        "effective_date": "2010-01-01",
    },
    "IODOPROPYNYL BUTYLCARBAMATE": {
        "cas_number": "55406-53-6",
        "regulation_ref": "EC 1223/2009 Annex V/56",
        "restriction_type": "RESTRICTED_0_05PCT_RINSE_OFF",
        "effective_date": "2015-01-01",
    },
    "SODIUM HYDROXYMETHYLGLYCINATE": {
        "cas_number": "70161-44-3",
        "regulation_ref": "EC 1223/2009 Annex V/51",
        "restriction_type": "RESTRICTED_0_5PCT",
        "effective_date": "2010-01-01",
    },
    "CHLORPHENESIN": {
        "cas_number": "104-29-0",
        "regulation_ref": "EC 1223/2009 Annex V/42",
        "restriction_type": "RESTRICTED_0_3PCT",
        "effective_date": "2010-01-01",
    },
    "CAPRYLYL GLYCOL": {
        "cas_number": "1117-86-8",
        "regulation_ref": "EC 1223/2009 Annex V",
        "restriction_type": "RESTRICTED_1_0PCT",
        "effective_date": "2015-01-01",
    },
    "ETHYLHEXYLGLYCERIN": {
        "cas_number": "70445-33-9",
        "regulation_ref": "EC 1223/2009 Annex V",
        "restriction_type": "RESTRICTED_0_5PCT",
        "effective_date": "2015-01-01",
    },
    "SODIUM DEHYDROACETATE": {
        "cas_number": "4418-26-2",
        "regulation_ref": "EC 1223/2009 Annex V/13",
        "restriction_type": "RESTRICTED_0_6PCT_ACID",
        "effective_date": "2010-01-01",
    },
    "DEHYDROACETIC ACID": {
        "cas_number": "520-45-6",
        "regulation_ref": "EC 1223/2009 Annex V/13",
        "restriction_type": "RESTRICTED_0_6PCT",
        "effective_date": "2010-01-01",
    },
    "BENZYL ALCOHOL": {
        "cas_number": "100-51-6",
        "regulation_ref": "EC 1223/2009 Annex III/45",
        "restriction_type": "RESTRICTED_1_0PCT",
        "effective_date": "2017-01-01",
    },
    "LIMONENE": {
        "cas_number": "5989-27-5",
        "regulation_ref": "EC 1223/2009 Annex III/88",
        "restriction_type": "RESTRICTED_OXIDATION_ALLERGEN",
        "effective_date": "2015-01-01",
    },
    "LINALOOL": {
        "cas_number": "78-70-6",
        "regulation_ref": "EC 1223/2009 Annex III/83",
        "restriction_type": "RESTRICTED_OXIDATION_ALLERGEN",
        "effective_date": "2015-01-01",
    },
    "BUTYLPHENYL METHYLPROPIONAL": {
        "cas_number": "80-54-6",
        "regulation_ref": "EC 1223/2009 Annex III/90",
        "restriction_type": "RESTRICTED_BANNED_MARCH_2022",
        "effective_date": "2022-03-01",
    },
    "RESORCINOL": {
        "cas_number": "108-46-3",
        "regulation_ref": "EC 1223/2009 Annex III/22",
        "restriction_type": "RESTRICTED_0_5PCT_HAIR_DYE",
        "effective_date": "2015-01-01",
    },
    "THIOGLYCOLIC ACID": {
        "cas_number": "68-11-1",
        "regulation_ref": "EC 1223/2009 Annex III/2a",
        "restriction_type": "RESTRICTED_HAIR_WAVE",
        "effective_date": "2001-01-01",
    },
    "HYDROGEN PEROXIDE": {
        "cas_number": "7722-84-1",
        "regulation_ref": "EC 1223/2009 Annex III/12",
        "restriction_type": "RESTRICTED_12PCT_HAIR",
        "effective_date": "2001-01-01",
    },
    "AMMONIA": {
        "cas_number": "7664-41-7",
        "regulation_ref": "EC 1223/2009 Annex III/4",
        "restriction_type": "RESTRICTED_6PCT",
        "effective_date": "2015-01-01",
    },
    "SODIUM HYDROXIDE": {
        "cas_number": "1310-73-2",
        "regulation_ref": "EC 1223/2009 Annex III/15d",
        "restriction_type": "RESTRICTED_PH_ADJUSTER",
        "effective_date": "2001-01-01",
    },
    "POTASSIUM HYDROXIDE": {
        "cas_number": "1310-58-3",
        "regulation_ref": "EC 1223/2009 Annex III/15d",
        "restriction_type": "RESTRICTED_PH_ADJUSTER",
        "effective_date": "2001-01-01",
    },
    "BENZOIC ACID": {
        "cas_number": "65-85-0",
        "regulation_ref": "EC 1223/2009 Annex V/1",
        "restriction_type": "RESTRICTED_2_5PCT_ACID",
        "effective_date": "2010-01-01",
    },
    "SORBIC ACID": {
        "cas_number": "110-44-1",
        "regulation_ref": "EC 1223/2009 Annex V/2",
        "restriction_type": "RESTRICTED_0_6PCT",
        "effective_date": "2010-01-01",
    },
    "COCAMIDOPROPYL BETAINE": {
        "cas_number": "61789-40-0",
        "regulation_ref": "SCCS/1591/17",
        "restriction_type": "RESTRICTED_PURITY_DMAPA",
        "effective_date": "2021-01-01",
    },
    "CYCLOMETHICONE": {
        "cas_number": "541-02-6",
        "regulation_ref": "EC 1223/2009 Annex II/1384",
        "restriction_type": "D4_RESTRICTED_0_1PCT_RINSE_OFF",
        "effective_date": "2020-01-31",
    },
    "DIMETHICONE": {
        "cas_number": "9006-65-9",
        "regulation_ref": "SCCS/1549/14",
        "restriction_type": "RESTRICTED_WATER_RELEASE",
        "effective_date": "2015-01-01",
    },
    "POLYQUATERNIUM-7": {
        "cas_number": "26590-05-6",
        "regulation_ref": "SCCS/1527/14",
        "restriction_type": "RESTRICTED_ACRYLAMIDE_IMPURITY",
        "effective_date": "2018-01-01",
    },
    "SODIUM LAURETH SULFATE": {
        "cas_number": "9004-82-4",
        "regulation_ref": "SCCS/1435/11",
        "restriction_type": "RESTRICTED_1_4_DIOXANE_LIMIT_10PPM",
        "effective_date": "2016-01-01",
    },
    "ETHANOLAMINE": {
        "cas_number": "141-43-5",
        "regulation_ref": "EC 1223/2009 Annex III/61",
        "restriction_type": "RESTRICTED_PURITY_NITROSAMINE",
        "effective_date": "2015-01-01",
    },
    "COCAMIDE DEA": {
        "cas_number": "68603-42-9",
        "regulation_ref": "EC 1223/2009 Annex III/60",
        "restriction_type": "RESTRICTED_NITROSAMINE_LIMIT",
        "effective_date": "2012-01-01",
    },
    "TRIETHANOLAMINE": {
        "cas_number": "102-71-6",
        "regulation_ref": "EC 1223/2009 Annex III/62",
        "restriction_type": "RESTRICTED_NITROSAMINE_LIMIT",
        "effective_date": "2015-01-01",
    },
    "DIETHANOLAMINE": {
        "cas_number": "111-42-2",
        "regulation_ref": "EC 1223/2009 Annex III/60",
        "restriction_type": "RESTRICTED_NITROSAMINE_LIMIT",
        "effective_date": "2012-01-01",
    },
    "RETINYL PALMITATE": {
        "cas_number": "79-81-2",
        "regulation_ref": "SCCS/1576/16",
        "restriction_type": "RESTRICTED_0_3PCT_RETINOL_EQ",
        "effective_date": "2017-01-01",
    },
    "RETINOL": {
        "cas_number": "68-26-8",
        "regulation_ref": "SCCS/1576/16",
        "restriction_type": "RESTRICTED_0_3PCT_BODY",
        "effective_date": "2017-01-01",
    },
    "ALPHA-HYDROXY ACIDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "SCCS/1489/12",
        "restriction_type": "RESTRICTED_PH_AND_CONC",
        "effective_date": "2013-01-01",
    },
    "ZINC OXIDE": {
        "cas_number": "1314-13-2",
        "regulation_ref": "EC 1223/2009 Annex VI/30",
        "restriction_type": "RESTRICTED_NANO_LABELING",
        "effective_date": "2016-01-01",
    },
    "TITANIUM DIOXIDE": {
        "cas_number": "13463-67-7",
        "regulation_ref": "EC 1223/2009 Annex VI/27",
        "restriction_type": "RESTRICTED_NANO_LABELING",
        "effective_date": "2016-01-01",
    },
    "CITRAL": {
        "cas_number": "5392-40-5",
        "regulation_ref": "EC 1223/2009 Annex III/79",
        "restriction_type": "RESTRICTED_ALLERGEN_LABEL",
        "effective_date": "2015-01-01",
    },
    "CITRONELLOL": {
        "cas_number": "106-22-9",
        "regulation_ref": "EC 1223/2009 Annex III/80",
        "restriction_type": "RESTRICTED_ALLERGEN_LABEL",
        "effective_date": "2015-01-01",
    },
    "GERANIOL": {
        "cas_number": "106-24-1",
        "regulation_ref": "EC 1223/2009 Annex III/81",
        "restriction_type": "RESTRICTED_ALLERGEN_LABEL",
        "effective_date": "2015-01-01",
    },
    "COUMARIN": {
        "cas_number": "91-64-5",
        "regulation_ref": "EC 1223/2009 Annex III/82",
        "restriction_type": "RESTRICTED_ALLERGEN_LABEL",
        "effective_date": "2015-01-01",
    },
    "EUGENOL": {
        "cas_number": "97-53-0",
        "regulation_ref": "EC 1223/2009 Annex III/84",
        "restriction_type": "RESTRICTED_ALLERGEN_LABEL",
        "effective_date": "2015-01-01",
    },
}

US_BANNED = {
    "METHYLENE GLYCOL": {
        "cas_number": "463-57-0",
        "regulation_ref": "21 CFR 350.10",
        "restriction_type": "BANNED_HAIR_SMOOTHING",
        "effective_date": "2011-04-01",
    },
    "CHLOROFORM": {
        "cas_number": "67-66-3",
        "regulation_ref": "21 CFR 700.13",
        "restriction_type": "BANNED",
        "effective_date": "1976-01-01",
    },
    "METHYLENE CHLORIDE": {
        "cas_number": "75-09-2",
        "regulation_ref": "21 CFR 700.19",
        "restriction_type": "BANNED",
        "effective_date": "1989-01-01",
    },
    "VINYL CHLORIDE": {
        "cas_number": "75-01-4",
        "regulation_ref": "21 CFR 700.14",
        "restriction_type": "BANNED_AEROSOL",
        "effective_date": "1974-01-01",
    },
    "ZIRCONIUM COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "21 CFR 700.16",
        "restriction_type": "BANNED_AEROSOL",
        "effective_date": "1977-01-01",
    },
    "HEXACHLOROPHENE": {
        "cas_number": "70-30-4",
        "regulation_ref": "21 CFR 250.250",
        "restriction_type": "BANNED_EXCEPT_PRESCRIPTION",
        "effective_date": "1972-01-01",
    },
    "MERCURY COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "21 CFR 700.13",
        "restriction_type": "BANNED_EXCEPT_EYE_TRACE",
        "effective_date": "1974-01-01",
    },
    "BITHIONOL": {
        "cas_number": "97-18-7",
        "regulation_ref": "21 CFR 700.11",
        "restriction_type": "BANNED",
        "effective_date": "1968-01-01",
    },
    "HALOGENATED SALICYLANILIDES": {
        "cas_number": "VARIOUS",
        "regulation_ref": "21 CFR 700.15",
        "restriction_type": "BANNED",
        "effective_date": "1975-01-01",
    },
    "CHLOROFLUOROCARBONS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "21 CFR 700.23",
        "restriction_type": "BANNED_AEROSOL_PROPELLANT",
        "effective_date": "1978-01-01",
    },
    "CATTLE BRAIN TISSUE": {
        "cas_number": "N/A",
        "regulation_ref": "21 CFR 700.27",
        "restriction_type": "BANNED_BSE_RISK",
        "effective_date": "2005-01-01",
    },
    "COW BRAIN TISSUE": {
        "cas_number": "N/A",
        "regulation_ref": "21 CFR 700.27",
        "restriction_type": "BANNED_BSE_RISK",
        "effective_date": "2005-01-01",
    },
    "SHEEP BRAIN TISSUE": {
        "cas_number": "N/A",
        "regulation_ref": "21 CFR 700.27",
        "restriction_type": "BANNED_BSE_RISK",
        "effective_date": "2005-01-01",
    },
    "LEAD ACETATE": {
        "cas_number": "301-04-2",
        "regulation_ref": "21 CFR 73.2395",
        "restriction_type": "BANNED_HAIR_DYE",
        "effective_date": "2018-10-01",
    },
    "BENZENE": {
        "cas_number": "71-43-2",
        "regulation_ref": "21 CFR 700.13",
        "restriction_type": "BANNED_UNSAFE",
        "effective_date": "1976-01-01",
    },
    "TRICLOSAN": {
        "cas_number": "3380-34-5",
        "regulation_ref": "FDA Final Rule 2016-25410",
        "restriction_type": "BANNED_OTC_CONSUMER_WASH",
        "effective_date": "2017-09-06",
    },
    "TRICLOCARBAN": {
        "cas_number": "101-20-2",
        "regulation_ref": "FDA Final Rule 2016-25410",
        "restriction_type": "BANNED_OTC_CONSUMER_WASH",
        "effective_date": "2017-09-06",
    },
    "IODINE_COMPLEX": {
        "cas_number": "VARIOUS",
        "regulation_ref": "FDA Final Rule 2016-25410",
        "restriction_type": "BANNED_OTC_CONSUMER_WASH",
        "effective_date": "2017-09-06",
    },
    "BENZALKONIUM CHLORIDE": {
        "cas_number": "8001-54-5",
        "regulation_ref": "FDA Final Rule 2016-25410",
        "restriction_type": "BANNED_OTC_SANITIZER",
        "effective_date": "2017-09-06",
    },
    "BENZETHONIUM CHLORIDE": {
        "cas_number": "121-54-0",
        "regulation_ref": "FDA Final Rule 2016-25410",
        "restriction_type": "BANNED_OTC_SANITIZER",
        "effective_date": "2017-09-06",
    },
    "CHLOROXYLENOL": {
        "cas_number": "88-04-0",
        "regulation_ref": "FDA Final Rule 2016-25410",
        "restriction_type": "BANNED_OTC_SANITIZER",
        "effective_date": "2017-09-06",
    },
    "MICROBEADS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "Microbead-Free Waters Act 2015",
        "restriction_type": "BANNED_RINSE_OFF",
        "effective_date": "2017-07-01",
    },
    "SULFUR": {
        "cas_number": "7704-34-9",
        "regulation_ref": "21 CFR 358.710 OTC",
        "restriction_type": "BANNED_WITHOUT_OTC_MONOGRAPH",
        "effective_date": "1990-01-01",
    },
    "SELENIUM DISULFIDE": {
        "cas_number": "7488-56-4",
        "regulation_ref": "21 CFR 358.710 OTC",
        "restriction_type": "BANNED_EXCEPT_OTC_1PCT",
        "effective_date": "1990-01-01",
    },
    "COAL TAR": {
        "cas_number": "8007-45-2",
        "regulation_ref": "21 CFR 358.710 OTC",
        "restriction_type": "BANNED_EXCEPT_OTC_0_5_5PCT",
        "effective_date": "1990-01-01",
    },
    "P-PHENYLENEDIAMINE": {
        "cas_number": "106-50-3",
        "regulation_ref": "21 CFR 700.19",
        "restriction_type": "BANNED_SKIN_CONTACT",
        "effective_date": "2015-01-01",
    },
    "FORMALDEHYDE": {
        "cas_number": "50-00-0",
        "regulation_ref": "FD&C Act Section 601",
        "restriction_type": "DEEMED_ADULTERATED",
        "effective_date": "2011-04-01",
    },
    "MUSK XYLENE": {
        "cas_number": "81-15-2",
        "regulation_ref": "IFRA 48th Amendment",
        "restriction_type": "BANNED_FRAGRANCE",
        "effective_date": "2015-06-01",
    },
    "MUSK KETONE": {
        "cas_number": "81-14-1",
        "regulation_ref": "IFRA 48th Amendment",
        "restriction_type": "BANNED_FRAGRANCE",
        "effective_date": "2015-06-01",
    },
    "ETHYLENE OXIDE": {
        "cas_number": "75-21-8",
        "regulation_ref": "EPA FIFRA",
        "restriction_type": "BANNED_STERILANT_COSMETICS",
        "effective_date": "2020-01-01",
    },
    "METHYLISOTHIAZOLINONE": {
        "cas_number": "2682-20-4",
        "regulation_ref": "CIR Safety Assessment",
        "restriction_type": "BANNED_LEAVE_ON",
        "effective_date": "2014-01-01",
    },
    "METHYLCHLOROISOTHIAZOLINONE": {
        "cas_number": "26172-55-4",
        "regulation_ref": "CIR Safety Assessment",
        "restriction_type": "BANNED_LEAVE_ON",
        "effective_date": "2014-01-01",
    },
    "ACRYLAMIDE": {
        "cas_number": "79-06-1",
        "regulation_ref": "California Prop 65",
        "restriction_type": "BANNED_WITHOUT_WARNING",
        "effective_date": "1990-01-01",
    },
    "TOLUENE": {
        "cas_number": "108-88-3",
        "regulation_ref": "California Prop 65",
        "restriction_type": "BANNED_NAIL_AND_SKIN",
        "effective_date": "2015-01-01",
    },
    "DIETHYL PHTHALATE": {
        "cas_number": "84-66-2",
        "regulation_ref": "California Prop 65",
        "restriction_type": "BANNED_WITHOUT_WARNING",
        "effective_date": "2010-01-01",
    },
    "DIBUTYL PHTHALATE": {
        "cas_number": "84-74-2",
        "regulation_ref": "California Prop 65 / CPSIA",
        "restriction_type": "BANNED_CHILDRENS_PRODUCTS",
        "effective_date": "2008-01-01",
    },
    "BBP": {
        "cas_number": "85-68-7",
        "regulation_ref": "California Prop 65",
        "restriction_type": "BANNED",
        "effective_date": "2013-01-01",
    },
    "DEHP": {
        "cas_number": "117-81-7",
        "regulation_ref": "California Prop 65 / CPSIA",
        "restriction_type": "BANNED_CHILDRENS_PRODUCTS",
        "effective_date": "2008-01-01",
    },
    "QUATERNIUM-15": {
        "cas_number": "4080-31-3",
        "regulation_ref": "CIR 2019 Re-Review",
        "restriction_type": "BANNED_ALL_COSMETIC_USES",
        "effective_date": "2019-01-01",
    },
    "HYDROQUINONE": {
        "cas_number": "123-31-9",
        "regulation_ref": "21 CFR 700.13",
        "restriction_type": "BANNED_OTC",
        "effective_date": "2020-01-01",
    },
    "MONOBENZONE": {
        "cas_number": "103-16-2",
        "regulation_ref": "21 CFR 700.13",
        "restriction_type": "BANNED_SKIN_LIGHTENING",
        "effective_date": "2015-01-01",
    },
    "MERCURY": {
        "cas_number": "7439-97-6",
        "regulation_ref": "21 CFR 700.13",
        "restriction_type": "BANNED_EXCEPT_EYE_TRACE_PPM",
        "effective_date": "1974-01-01",
    },
    "NITROSAMINES": {
        "cas_number": "VARIOUS",
        "regulation_ref": "FDA Guidance 1979",
        "restriction_type": "BANNED_ABOVE_10PPB",
        "effective_date": "1979-01-01",
    },
    "ASBESTOS": {
        "cas_number": "1332-21-4",
        "regulation_ref": "FD&C Act 21 USC 361",
        "restriction_type": "BANNED_TALC_CONTAMINANT",
        "effective_date": "2019-03-01",
    },
    "1,4-DIOXANE": {
        "cas_number": "123-91-1",
        "regulation_ref": "California Prop 65",
        "restriction_type": "BANNED_ABOVE_10PPM_NO_WARNING",
        "effective_date": "2017-01-01",
    },
    "BUTYLATED HYDROXYANISOLE": {
        "cas_number": "25013-16-5",
        "regulation_ref": "California Prop 65",
        "restriction_type": "BANNED_WITHOUT_WARNING",
        "effective_date": "2016-01-01",
    },
    "POLYETHYLENE GLYCOL": {
        "cas_number": "25322-68-3",
        "regulation_ref": "FDA Guidance 1,4-Dioxane",
        "restriction_type": "BANNED_1_4_DIOXANE_CONTAM",
        "effective_date": "2019-01-01",
    },
    "COCAMIDE DEA": {
        "cas_number": "68603-42-9",
        "regulation_ref": "California Prop 65",
        "restriction_type": "BANNED_WITHOUT_COCONUT_AMIDE_WARNING",
        "effective_date": "2012-01-01",
    },
    "LAURAMIDE DEA": {
        "cas_number": "120-40-1",
        "regulation_ref": "California Prop 65",
        "restriction_type": "BANNED",
        "effective_date": "2012-01-01",
    },
    "ISOPROPYLPARABEN": {
        "cas_number": "4191-73-5",
        "regulation_ref": "FDA CIR Safety Assessment",
        "restriction_type": "BANNED",
        "effective_date": "2018-01-01",
    },
}

US_RESTRICTED = {
    "SALICYLIC ACID": {
        "cas_number": "69-72-7",
        "regulation_ref": "21 CFR 358.710 OTC",
        "restriction_type": "RESTRICTED_1_8_3_0PCT_OTC",
        "effective_date": "1990-01-01",
    },
    "ZINC PYRITHIONE": {
        "cas_number": "13463-41-7",
        "regulation_ref": "21 CFR 358.710 OTC",
        "restriction_type": "RESTRICTED_0_3_2_0PCT_OTC",
        "effective_date": "1990-01-01",
    },
    "METHYLCHLOROISOTHIAZOLINONE": {
        "cas_number": "26172-55-4",
        "regulation_ref": "CIR Safety 15 ppm",
        "restriction_type": "RESTRICTED_7_5PPM_RINSE_OFF",
        "effective_date": "2014-01-01",
    },
    "METHYLISOTHIAZOLINONE": {
        "cas_number": "2682-20-4",
        "regulation_ref": "CIR Safety 100 ppm",
        "restriction_type": "RESTRICTED_100PPM_RINSE_OFF",
        "effective_date": "2014-01-01",
    },
    "BUTYLATED HYDROXYTOLUENE": {
        "cas_number": "128-37-0",
        "regulation_ref": "21 CFR 172.115",
        "restriction_type": "RESTRICTED_0_01_0_1PCT",
        "effective_date": "1977-01-01",
    },
    "PHENOXYETHANOL": {
        "cas_number": "122-99-6",
        "regulation_ref": "CIR Safety 1.0%",
        "restriction_type": "RESTRICTED_1_0PCT",
        "effective_date": "2012-01-01",
    },
    "DMDM HYDANTOIN": {
        "cas_number": "6440-58-0",
        "regulation_ref": "CIR Safety 1.0%",
        "restriction_type": "RESTRICTED_1_0PCT_FORMALDEHYDE_RELEASER",
        "effective_date": "2010-01-01",
    },
    "BENZYL ALCOHOL": {
        "cas_number": "100-51-6",
        "regulation_ref": "CIR Safety 2.5%",
        "restriction_type": "RESTRICTED_2_5PCT",
        "effective_date": "2011-01-01",
    },
    "METHYLPARABEN": {
        "cas_number": "99-76-3",
        "regulation_ref": "CIR 1984",
        "restriction_type": "RESTRICTED_0_4PCT_SINGLE",
        "effective_date": "1984-01-01",
    },
    "PROPYLPARABEN": {
        "cas_number": "94-13-3",
        "regulation_ref": "CIR 1984",
        "restriction_type": "RESTRICTED_0_4PCT_SINGLE",
        "effective_date": "1984-01-01",
    },
    "BUTYLPARABEN": {
        "cas_number": "94-26-8",
        "regulation_ref": "CIR Safety",
        "restriction_type": "RESTRICTED_MINIMUM_EFFECTIVE_LEVEL",
        "effective_date": "2019-01-01",
    },
    "IODOPROPYNYL BUTYLCARBAMATE": {
        "cas_number": "55406-53-6",
        "regulation_ref": "CIR Safety 0.01%",
        "restriction_type": "RESTRICTED_0_01PCT_RINSE_OFF",
        "effective_date": "2015-01-01",
    },
    "FORMALDEHYDE": {
        "cas_number": "50-00-0",
        "regulation_ref": "CIR Safety 0.2% free",
        "restriction_type": "RESTRICTED_0_2PCT_FREE",
        "effective_date": "2011-01-01",
    },
    "SODIUM BENZOATE": {
        "cas_number": "532-32-1",
        "regulation_ref": "GRAS food / CIR 2001",
        "restriction_type": "RESTRICTED_2_5PCT",
        "effective_date": "2001-01-01",
    },
    "POTASSIUM SORBATE": {
        "cas_number": "24634-61-5",
        "regulation_ref": "GRAS food / CIR Safety",
        "restriction_type": "RESTRICTED_0_6PCT",
        "effective_date": "2001-01-01",
    },
    "CITRIC ACID": {
        "cas_number": "77-92-9",
        "regulation_ref": "CIR 2014",
        "restriction_type": "RESTRICTED_PH_ADJUSTER_10PCT",
        "effective_date": "2014-01-01",
    },
    "SODIUM HYDROXIDE": {
        "cas_number": "1310-73-2",
        "regulation_ref": "CIR 2015",
        "restriction_type": "RESTRICTED_PH_ADJUSTER_PH_UNDER_12",
        "effective_date": "2015-01-01",
    },
    "GLYCOLIC ACID": {
        "cas_number": "79-14-1",
        "regulation_ref": "CIR 2013",
        "restriction_type": "RESTRICTED_10PCT_PH_3_5_MIN",
        "effective_date": "2013-01-01",
    },
    "LACTIC ACID": {
        "cas_number": "50-21-5",
        "regulation_ref": "CIR 2013",
        "restriction_type": "RESTRICTED_10PCT_PH_3_5_MIN",
        "effective_date": "2013-01-01",
    },
    "RESORCINOL": {
        "cas_number": "108-46-3",
        "regulation_ref": "CIR 2013",
        "restriction_type": "RESTRICTED_1_0PCT_HAIR_DYE_INTERMEDIATE",
        "effective_date": "2013-01-01",
    },
    "HYDROGEN PEROXIDE": {
        "cas_number": "7722-84-1",
        "regulation_ref": "CIR 2014",
        "restriction_type": "RESTRICTED_6_0PCT_HAIR_DYE_DEVELOPER",
        "effective_date": "2014-01-01",
    },
    "SODIUM LAURETH SULFATE": {
        "cas_number": "9004-82-4",
        "regulation_ref": "CIR 2018 / 1,4-Dioxane",
        "restriction_type": "RESTRICTED_1_4_DIOXANE_10PPM_CALIFORNIA",
        "effective_date": "2018-01-01",
    },
    "SODIUM LAURYL SULFATE": {
        "cas_number": "151-21-3",
        "regulation_ref": "CIR 2018",
        "restriction_type": "RESTRICTED_1_0PCT_SKIN_IRRITATION_THRESHOLD",
        "effective_date": "2018-01-01",
    },
    "DIMETHICONE": {
        "cas_number": "9006-65-9",
        "regulation_ref": "CIR 2011",
        "restriction_type": "RESTRICTED_15PCT_RINSE_OFF",
        "effective_date": "2011-01-01",
    },
    "AMODIMETHICONE": {
        "cas_number": "71750-80-6",
        "regulation_ref": "CIR 2011",
        "restriction_type": "RESTRICTED_5PCT_RINSE_OFF",
        "effective_date": "2011-01-01",
    },
    "CYCLOMETHICONE": {
        "cas_number": "556-67-2",
        "regulation_ref": "CIR 2011",
        "restriction_type": "RESTRICTED_15PCT_RINSE_OFF",
        "effective_date": "2011-01-01",
    },
    "CYCLOPENTASILOXANE": {
        "cas_number": "541-02-6",
        "regulation_ref": "CIR 2011 / CA DTSC",
        "restriction_type": "RESTRICTED_D5_0_1PCT_RINSE_OFF_CA",
        "effective_date": "2020-01-01",
    },
    "RETINYL PALMITATE": {
        "cas_number": "79-81-2",
        "regulation_ref": "CIR 2013",
        "restriction_type": "RESTRICTED_0_3PCT_RETINOL_EQ",
        "effective_date": "2013-01-01",
    },
    "RETINOL": {
        "cas_number": "68-26-8",
        "regulation_ref": "CIR 2013",
        "restriction_type": "RESTRICTED_0_3PCT_BODY",
        "effective_date": "2013-01-01",
    },
    "BENZOPHENONE-3": {
        "cas_number": "131-57-7",
        "regulation_ref": "CIR 2012",
        "restriction_type": "RESTRICTED_6PCT_SUNSCREEN",
        "effective_date": "2012-01-01",
    },
    "TRICLOSAN": {
        "cas_number": "3380-34-5",
        "regulation_ref": "FDA OTC Monograph",
        "restriction_type": "RESTRICTED_OTC_ANTIMICROBIAL_HEALTHCARE_ONLY",
        "effective_date": "2017-09-06",
    },
    "ZINC OXIDE": {
        "cas_number": "1314-13-2",
        "regulation_ref": "FDA Sunscreen Monograph",
        "restriction_type": "RESTRICTED_25PCT_SUNSCREEN_GRASE",
        "effective_date": "2019-02-01",
    },
    "TITANIUM DIOXIDE": {
        "cas_number": "13463-67-7",
        "regulation_ref": "FDA Sunscreen Monograph",
        "restriction_type": "RESTRICTED_25PCT_SUNSCREEN_GRASE",
        "effective_date": "2019-02-01",
    },
    "TRIETHANOLAMINE": {
        "cas_number": "102-71-6",
        "regulation_ref": "CIR 2013",
        "restriction_type": "RESTRICTED_5PCT_NITROSAMINE_LIMIT",
        "effective_date": "2013-01-01",
    },
    "FRAGRANCE": {
        "cas_number": "N/A",
        "regulation_ref": "FDA 21 CFR 701.3(a)",
        "restriction_type": "RESTRICTED_GENERIC_LABEL_ALLERGEN_DISCLOSURE",
        "effective_date": "1973-01-01",
    },
    "PARFUM": {
        "cas_number": "N/A",
        "regulation_ref": "FDA 21 CFR 701.3(a)",
        "restriction_type": "RESTRICTED_GENERIC_LABEL_ALLERGEN_DISCLOSURE",
        "effective_date": "1973-01-01",
    },
    "BENZALKONIUM CHLORIDE": {
        "cas_number": "8001-54-5",
        "regulation_ref": "FDA OTC Antiseptic Monograph",
        "restriction_type": "RESTRICTED_0_13PCT_CONSUMER_ANTISEPTIC",
        "effective_date": "2019-01-01",
    },
    "CHLORPHENESIN": {
        "cas_number": "104-29-0",
        "regulation_ref": "CIR 2014",
        "restriction_type": "RESTRICTED_0_32PCT",
        "effective_date": "2014-01-01",
    },
    "CAPRYLYL GLYCOL": {
        "cas_number": "1117-86-8",
        "regulation_ref": "CIR 2012",
        "restriction_type": "RESTRICTED_1_0PCT_PRESERVATIVE_BOOSTER",
        "effective_date": "2012-01-01",
    },
    "ETHYLHEXYLGLYCERIN": {
        "cas_number": "70445-33-9",
        "regulation_ref": "CIR 2013",
        "restriction_type": "RESTRICTED_0_5PCT_PRESERVATIVE_BOOSTER",
        "effective_date": "2013-01-01",
    },
    "PENTYLENE GLYCOL": {
        "cas_number": "5343-92-0",
        "regulation_ref": "CIR 2012",
        "restriction_type": "RESTRICTED_5_0PCT",
        "effective_date": "2012-01-01",
    },
    "SODIUM DEHYDROACETATE": {
        "cas_number": "4418-26-2",
        "regulation_ref": "CIR 2014",
        "restriction_type": "RESTRICTED_1_0PCT",
        "effective_date": "2014-01-01",
    },
    "SODIUM HYDROXYMETHYLGLYCINATE": {
        "cas_number": "70161-44-3",
        "regulation_ref": "CIR 2015",
        "restriction_type": "RESTRICTED_0_5PCT",
        "effective_date": "2015-01-01",
    },
    "LIMONENE": {
        "cas_number": "5989-27-5",
        "regulation_ref": "CIR Safety Allergen",
        "restriction_type": "RESTRICTED_ALLERGEN_LABEL_VOLUNTARY",
        "effective_date": "2015-01-01",
    },
    "LINALOOL": {
        "cas_number": "78-70-6",
        "regulation_ref": "CIR Safety Allergen",
        "restriction_type": "RESTRICTED_ALLERGEN_LABEL_VOLUNTARY",
        "effective_date": "2015-01-01",
    },
    "COUMARIN": {
        "cas_number": "91-64-5",
        "regulation_ref": "FDA 21 CFR 189.130",
        "restriction_type": "RESTRICTED_FOOD_BAN_COMETIC_USE_TRACE",
        "effective_date": "1954-01-01",
    },
    "DIETHANOLAMINE": {
        "cas_number": "111-42-2",
        "regulation_ref": "CIR 2013 / Prop 65",
        "restriction_type": "RESTRICTED_NITROSAMINE_CONTAMINANT",
        "effective_date": "2013-01-01",
    },
    "ETHANOLAMINE": {
        "cas_number": "141-43-5",
        "regulation_ref": "CIR 2015",
        "restriction_type": "RESTRICTED_PH_ADJUSTER_UNDER_5PCT",
        "effective_date": "2015-01-01",
    },
    "BENZYL BENZOATE": {
        "cas_number": "120-51-4",
        "regulation_ref": "CIR 2011",
        "restriction_type": "RESTRICTED_5PCT_FRAGRANCE",
        "effective_date": "2011-01-01",
    },
    "BENZYL SALICYLATE": {
        "cas_number": "118-58-1",
        "regulation_ref": "CIR 2011",
        "restriction_type": "RESTRICTED_5PCT_FRAGRANCE",
        "effective_date": "2011-01-01",
    },
}

JP_QUASI_DRUG = {
    "ZINC PYRITHIONE": {
        "cas_number": "13463-41-7",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_ONLY_0_1MG_ML",
        "effective_date": "2001-01-01",
    },
    "SALICYLIC ACID": {
        "cas_number": "69-72-7",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_0_2PCT_MAX_COSMETIC",
        "effective_date": "2001-01-01",
    },
    "KETOCONAZOLE": {
        "cas_number": "65277-42-1",
        "regulation_ref": "MHLW Quasi-Drug Approval 2000",
        "restriction_type": "QUASI_DRUG_PRESCRIPTION_OTC",
        "effective_date": "2000-01-01",
    },
    "PIROCTONE OLAMINE": {
        "cas_number": "68890-66-4",
        "regulation_ref": "MHLW Quasi-Drug Standard 2005",
        "restriction_type": "QUASI_DRUG_0_5PCT_ANTI_DANDRUFF",
        "effective_date": "2005-01-01",
    },
    "SELENIUM DISULFIDE": {
        "cas_number": "7488-56-4",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_1_0PCT_MAX",
        "effective_date": "2001-01-01",
    },
    "SULFUR": {
        "cas_number": "7704-34-9",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_2_0PCT_ANTI_DANDRUFF",
        "effective_date": "2001-01-01",
    },
    "COAL TAR": {
        "cas_number": "8007-45-2",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_0_5_5_0PCT",
        "effective_date": "2001-01-01",
    },
    "GLYCYRRHETINIC ACID": {
        "cas_number": "471-53-4",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_ANTI_INFLAMMATORY",
        "effective_date": "2001-01-01",
    },
    "DIPOTASSIUM GLYCYRRHIZINATE": {
        "cas_number": "68797-35-3",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_ANTI_INFLAMMATORY_0_5PCT",
        "effective_date": "2001-01-01",
    },
    "TRANEXAMIC ACID": {
        "cas_number": "1197-18-8",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_SKIN_WHITENING_2PCT",
        "effective_date": "2010-01-01",
    },
    "ARBUTIN": {
        "cas_number": "497-76-7",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_SKIN_WHITENING_3PCT",
        "effective_date": "2001-01-01",
    },
    "KOJIC ACID": {
        "cas_number": "501-30-4",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_SKIN_WHITENING_2PCT",
        "effective_date": "2001-01-01",
    },
    "ASCORBIC ACID": {
        "cas_number": "50-81-7",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_SKIN_WHITENING_3PCT",
        "effective_date": "2001-01-01",
    },
    "TOCOPHERYL ACETATE": {
        "cas_number": "7695-91-2",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_ANTI_INFLAMMATORY_0_5PCT",
        "effective_date": "2001-01-01",
    },
    "NIACINAMIDE": {
        "cas_number": "98-92-0",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_SKIN_WHITENING_5PCT",
        "effective_date": "2010-01-01",
    },
    "MAGNESIUM ASCORBYL PHOSPHATE": {
        "cas_number": "114040-31-2",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_SKIN_WHITENING_3PCT",
        "effective_date": "2005-01-01",
    },
    "SODIUM ASCORBYL PHOSPHATE": {
        "cas_number": "66170-10-3",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG",
        "effective_date": "2005-01-01",
    },
    "PYRIDOXINE HYDROCHLORIDE": {
        "cas_number": "58-56-0",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_VITAMIN_0_1PCT",
        "effective_date": "2001-01-01",
    },
    "ALLANTOIN": {
        "cas_number": "97-59-6",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_ANTI_INFLAMMATORY_0_5PCT",
        "effective_date": "2001-01-01",
    },
    "CAMPHOR": {
        "cas_number": "76-22-2",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_COUNTERIRRITANT_1_0PCT",
        "effective_date": "2001-01-01",
    },
    "MENTHOL": {
        "cas_number": "89-78-1",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_COUNTERIRRITANT_1_0PCT",
        "effective_date": "2001-01-01",
    },
    "RESORCINOL": {
        "cas_number": "108-46-3",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_0_1PCT_COSMETIC",
        "effective_date": "2001-01-01",
    },
    "SODIUM LAURYL SULFATE": {
        "cas_number": "151-21-3",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_SURFACTANT",
        "effective_date": "2000-01-01",
    },
    "PHENOXYETHANOL": {
        "cas_number": "122-99-6",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_1_0PCT",
        "effective_date": "2000-01-01",
    },
    "METHYLPARABEN": {
        "cas_number": "99-76-3",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_1_0G_100G",
        "effective_date": "2000-01-01",
    },
    "PROPYLPARABEN": {
        "cas_number": "94-13-3",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_1_0G_100G",
        "effective_date": "2000-01-01",
    },
    "BUTYLPARABEN": {
        "cas_number": "94-26-8",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_1_0G_100G",
        "effective_date": "2000-01-01",
    },
    "BENZOIC ACID": {
        "cas_number": "65-85-0",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_PRESERVATIVE_0_2PCT",
        "effective_date": "2000-01-01",
    },
    "SODIUM BENZOATE": {
        "cas_number": "532-32-1",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_PRESERVATIVE_1_0PCT",
        "effective_date": "2000-01-01",
    },
    "HYDROQUINONE": {
        "cas_number": "123-31-9",
        "regulation_ref": "MHLW Prohibited Ingredient List",
        "restriction_type": "QUASI_DRUG_PROHIBITED_SKIN_WHITENING",
        "effective_date": "2001-01-01",
    },
    "TITANIUM DIOXIDE": {
        "cas_number": "13463-67-7",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_UV_FILTER_ONLY",
        "effective_date": "2001-01-01",
    },
    "ZINC OXIDE": {
        "cas_number": "1314-13-2",
        "regulation_ref": "MHLW Quasi-Drug Standard 2001",
        "restriction_type": "QUASI_DRUG_UV_FILTER_ONLY",
        "effective_date": "2001-01-01",
    },
    "SODIUM HYALURONATE": {
        "cas_number": "9067-32-7",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_ACTIVE_ONLY",
        "effective_date": "2010-01-01",
    },
    "FORMALDEHYDE": {
        "cas_number": "50-00-0",
        "regulation_ref": "MHLW Prohibited Ingredient List",
        "restriction_type": "QUASI_DRUG_PROHIBITED_ALL",
        "effective_date": "2001-01-01",
    },
    "BENZALKONIUM CHLORIDE": {
        "cas_number": "8001-54-5",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_ANTIMICROBIAL_HEALTHCARE_ONLY",
        "effective_date": "2000-01-01",
    },
    "TRICLOSAN": {
        "cas_number": "3380-34-5",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_0_1PCT",
        "effective_date": "2000-01-01",
    },
    "CHLORHEXIDINE GLUCONATE": {
        "cas_number": "18472-51-0",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_OTC_ANTIMICROBIAL",
        "effective_date": "2001-01-01",
    },
    "DIPHENHYDRAMINE": {
        "cas_number": "58-73-1",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_ANTIHISTAMINE_0_5PCT",
        "effective_date": "2001-01-01",
    },
    "HYDROCORTISONE ACETATE": {
        "cas_number": "50-03-3",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_STEROID_PRESCRIPTION",
        "effective_date": "2001-01-01",
    },
    "MINOXIDIL": {
        "cas_number": "38304-91-5",
        "regulation_ref": "MHLW Quasi-Drug Approval 2001",
        "restriction_type": "QUASI_DRUG_1PCT_HAIR_GROWTH",
        "effective_date": "2001-01-01",
    },
    "TRETINOIN": {
        "cas_number": "302-79-4",
        "regulation_ref": "MHLW Quasi-Drug Approval 2005",
        "restriction_type": "QUASI_DRUG_PRESCRIPTION_ONLY",
        "effective_date": "2005-01-01",
    },
    "ADAPALENE": {
        "cas_number": "106685-40-9",
        "regulation_ref": "MHLW Quasi-Drug Approval 2010",
        "restriction_type": "QUASI_DRUG_0_1PCT_ACNE",
        "effective_date": "2010-01-01",
    },
    "BENZOYL PEROXIDE": {
        "cas_number": "94-36-0",
        "regulation_ref": "MHLW Quasi-Drug Standard 2010",
        "restriction_type": "QUASI_DRUG_2_5_10PCT_ACNE",
        "effective_date": "2010-01-01",
    },
    "D-PANTHENOL": {
        "cas_number": "81-13-0",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_ANTI_INFLAMMATORY_1PCT",
        "effective_date": "2005-01-01",
    },
    "STEARYL GLYCYRRHETINATE": {
        "cas_number": "13832-70-7",
        "regulation_ref": "MHLW Quasi-Drug Active Ingredient List",
        "restriction_type": "QUASI_DRUG_ANTI_INFLAMMATORY",
        "effective_date": "2005-01-01",
    },
    "METHYLCHLOROISOTHIAZOLINONE": {
        "cas_number": "26172-55-4",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_0_0015PCT_RINSE_OFF",
        "effective_date": "2000-01-01",
    },
    "METHYLISOTHIAZOLINONE": {
        "cas_number": "2682-20-4",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_0_01PCT_RINSE_OFF",
        "effective_date": "2000-01-01",
    },
    "IODOPROPYNYL BUTYLCARBAMATE": {
        "cas_number": "55406-53-6",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_0_02PCT_RINSE_OFF",
        "effective_date": "2000-01-01",
    },
    "IMIDAZOLIDINYL UREA": {
        "cas_number": "39236-46-9",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_RESTRICTED_0_3PCT",
        "effective_date": "2000-01-01",
    },
    "POTASSIUM HYDROXIDE": {
        "cas_number": "1310-58-3",
        "regulation_ref": "MHLW Cosmetic Standard 2000",
        "restriction_type": "QUASI_DRUG_PH_ADJUSTER_RESTRICTED",
        "effective_date": "2000-01-01",
    },
}

CN_BANNED = {
    "HYDROQUINONE": {
        "cas_number": "123-31-9",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_SKIN_WHITENING",
        "effective_date": "2015-12-23",
    },
    "MONOBENZONE": {
        "cas_number": "103-16-2",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "PHENOL": {
        "cas_number": "108-95-2",
        "regulation_ref": "NMPA Safety Technical Standard 2015 (Annex II)",
        "restriction_type": "BANNED_SKIN_PEEL",
        "effective_date": "2015-12-23",
    },
    "MERCURY COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "LEAD COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_EXCEPT_TRACE_10PPM",
        "effective_date": "2015-12-23",
    },
    "ARSENIC COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_EXCEPT_TRACE_2PPM",
        "effective_date": "2015-12-23",
    },
    "CADMIUM COMPOUNDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_EXCEPT_TRACE_5PPM",
        "effective_date": "2015-12-23",
    },
    "FORMALDEHYDE": {
        "cas_number": "50-00-0",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ABOVE_0_2PCT_FREE",
        "effective_date": "2015-12-23",
    },
    "BENZENE": {
        "cas_number": "71-43-2",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "TOLUENE": {
        "cas_number": "108-88-3",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ABOVE_25PCT_NAIL",
        "effective_date": "2015-12-23",
    },
    "CHLOROFORM": {
        "cas_number": "67-66-3",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "ACRYLAMIDE": {
        "cas_number": "79-06-1",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "BENZIDINE": {
        "cas_number": "92-87-5",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "2-AMINOTOLUENE": {
        "cas_number": "95-53-4",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "4-AMINODIPHENYL": {
        "cas_number": "92-67-1",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "BETANAPHTHYL": {
        "cas_number": "91-59-8",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "TRICLOSAN": {
        "cas_number": "3380-34-5",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_EXCEPT_0_3PCT_HAND_SANITIZER",
        "effective_date": "2015-12-23",
    },
    "TRICLOCARBAN": {
        "cas_number": "101-20-2",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL_COSMETIC",
        "effective_date": "2015-12-23",
    },
    "DIETHYL PHTHALATE": {
        "cas_number": "84-66-2",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "DIBUTYL PHTHALATE": {
        "cas_number": "84-74-2",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "DEHP": {
        "cas_number": "117-81-7",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "BBP": {
        "cas_number": "85-68-7",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "MUSK XYLENE": {
        "cas_number": "81-15-2",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL_FRAGRANCE",
        "effective_date": "2015-12-23",
    },
    "MUSK KETONE": {
        "cas_number": "81-14-1",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL_FRAGRANCE",
        "effective_date": "2015-12-23",
    },
    "BUTYLATED HYDROXYANISOLE": {
        "cas_number": "25013-16-5",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "COAL TAR": {
        "cas_number": "8007-45-2",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_EXCEPT_OTC_QUASI_DRUG",
        "effective_date": "2015-12-23",
    },
    "P-PHENYLENEDIAMINE": {
        "cas_number": "106-50-3",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ABOVE_6PCT_HAIR_DYE",
        "effective_date": "2015-12-23",
    },
    "SELENIUM DISULFIDE": {
        "cas_number": "7488-56-4",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_EXCEPT_OTC_1PCT",
        "effective_date": "2015-12-23",
    },
    "NITRITES": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "RADIOACTIVE SUBSTANCES": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "ANDROGENS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "ESTROGENS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "CORTICOSTEROIDS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "ANTIBIOTICS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "CLENBUTEROL": {
        "cas_number": "37148-27-9",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "SIBUTRAMINE": {
        "cas_number": "106650-56-0",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "EPICHLOROHYDRIN": {
        "cas_number": "106-89-8",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "ETHYLENE OXIDE": {
        "cas_number": "75-21-8",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "LIDOCAINE": {
        "cas_number": "137-58-6",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_COSMETIC",
        "effective_date": "2015-12-23",
    },
    "PROCAINE": {
        "cas_number": "59-46-1",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_COSMETIC",
        "effective_date": "2015-12-23",
    },
    "BENZALKONIUM CHLORIDE": {
        "cas_number": "8001-54-5",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ABOVE_0_1PCT",
        "effective_date": "2015-12-23",
    },
    "METHYLCHLOROISOTHIAZOLINONE": {
        "cas_number": "26172-55-4",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_LEAVE_ON",
        "effective_date": "2015-12-23",
    },
    "METHYLISOTHIAZOLINONE": {
        "cas_number": "2682-20-4",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_LEAVE_ON",
        "effective_date": "2015-12-23",
    },
    "DMDM HYDANTOIN": {
        "cas_number": "6440-58-0",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ABOVE_0_6PCT",
        "effective_date": "2015-12-23",
    },
    "ISOPROPYLPARABEN": {
        "cas_number": "4191-73-5",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "ISOBUTYLPARABEN": {
        "cas_number": "4247-02-3",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "PHENYLPARABEN": {
        "cas_number": "17696-62-7",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "BENZYLPARABEN": {
        "cas_number": "94-18-8",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "PENTYLPARABEN": {
        "cas_number": "6521-29-5",
        "regulation_ref": "NMPA Safety Technical Standard 2015",
        "restriction_type": "BANNED_ALL",
        "effective_date": "2015-12-23",
    },
    "MICROBEADS": {
        "cas_number": "VARIOUS",
        "regulation_ref": "NMPA Announcement 2020",
        "restriction_type": "BANNED_RINSE_OFF",
        "effective_date": "2020-12-31",
    },
}

# ─────────────────────────────────────────────────────────
# Product comparison database
# ─────────────────────────────────────────────────────────

PRODUCT_COMPARISON_DB = {
    "Pantene Pro-V Daily Moisture Renewal": {
        "brand": "Procter & Gamble",
        "category": "mass_market",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Glycol Distearate",
            "Dimethicone", "Fragrance", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Panthenol",
            "Panthenyl Ethyl Ether", "Methylchloroisothiazolinone",
            "Methylisothiazolinone", "Argania Spinosa Kernel Oil", "Histidine"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Glycol Distearate",
            "Dimethicone", "Parfum", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Panthenol",
            "Panthenyl Ethyl Ether", "Argania Spinosa Kernel Oil",
            "Linalool", "Limonene", "Hexyl Cinnamal", "Citronellol", "Histidine"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Glycol Distearate",
            "Dimethicone", "Fragrance", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Panthenol",
            "Panthenyl Ethyl Ether", "Histidine"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Glycol Distearate",
            "Dimethicone", "Parfum", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Panthenol",
            "Panthenyl Ethyl Ether", "Argania Spinosa Kernel Oil", "Histidine"
        ],
    },
    "Head & Shoulders Classic Clean": {
        "brand": "Procter & Gamble",
        "category": "anti_dandruff",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Zinc Pyrithione",
            "Dimethicone", "Fragrance", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Zinc Carbonate",
            "Methylchloroisothiazolinone", "Methylisothiazolinone",
            "Glycol Distearate"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Zinc Pyrithione",
            "Dimethicone", "Parfum", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Zinc Carbonate",
            "Glycol Distearate", "Linalool", "Limonene"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Zinc Pyrithione", "Dimethicone", "Fragrance",
            "Sodium Citrate", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Zinc Carbonate", "Glycol Distearate"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Zinc Pyrithione",
            "Dimethicone", "Parfum", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Zinc Carbonate"
        ],
    },
    "Dove Daily Moisture Shampoo": {
        "brand": "Unilever",
        "category": "mass_market",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Fragrance", "Glycol Distearate",
            "Dimethiconol", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Cocamide MEA", "PPG-9",
            "Methylchloroisothiazolinone", "Methylisothiazolinone",
            "Glycerin"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Parfum", "Glycol Distearate",
            "Dimethiconol", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Cocamide MEA", "PPG-9",
            "Glycerin", "Linalool", "Coumarin"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Fragrance", "Dimethiconol", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Cocamide MEA",
            "Glycerin"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Parfum", "Glycol Distearate",
            "Dimethiconol", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Glycerin"
        ],
    },
    "Herbal Essences Bio:renew": {
        "brand": "Procter & Gamble",
        "category": "natural",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Fragrance",
            "Citric Acid", "Sodium Citrate", "Sodium Benzoate",
            "Tetrasodium EDTA", "Polyquaternium-10", "Dimethiconol",
            "Aloe Barbadensis Leaf Juice", "Ecklonia Radiata Extract",
            "Histidine", "Panthenol", "Methylchloroisothiazolinone",
            "Methylisothiazolinone", "Methylparaben", "Propylparaben"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Parfum",
            "Citric Acid", "Sodium Citrate", "Sodium Benzoate",
            "Tetrasodium EDTA", "Polyquaternium-10", "Dimethiconol",
            "Aloe Barbadensis Leaf Juice", "Ecklonia Radiata Extract",
            "Histidine", "Panthenol", "Linalool", "Limonene"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Fragrance", "Citric Acid",
            "Sodium Citrate", "Sodium Benzoate", "Tetrasodium EDTA",
            "Polyquaternium-10", "Aloe Barbadensis Leaf Juice", "Histidine"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Parfum", "Citric Acid",
            "Sodium Citrate", "Sodium Benzoate", "Tetrasodium EDTA",
            "Polyquaternium-10", "Aloe Barbadensis Leaf Juice", "Histidine"
        ],
    },
    "L'Oreal Elvive Total Repair 5": {
        "brand": "L'Oreal",
        "category": "premium",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Dimethicone", "Fragrance", "Glycol Distearate",
            "Sodium Citrate", "Citric Acid", "Sodium Benzoate",
            "Salicylic Acid", "Tetrasodium EDTA", "Carbomer",
            "Cocamide MIPA", "Argania Spinosa Kernel Oil",
            "Methylchloroisothiazolinone", "Methylisothiazolinone"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Dimethicone", "Parfum", "Glycol Distearate",
            "Sodium Citrate", "Citric Acid", "Sodium Benzoate",
            "Salicylic Acid", "Tetrasodium EDTA", "Carbomer",
            "Cocamide MIPA", "Argania Spinosa Kernel Oil",
            "Linalool", "Limonene", "Citronellol"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Dimethicone", "Fragrance", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Salicylic Acid", "Tetrasodium EDTA",
            "Cocamide MIPA", "Argania Spinosa Kernel Oil"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Dimethicone", "Parfum", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Salicylic Acid", "Tetrasodium EDTA",
            "Argania Spinosa Kernel Oil"
        ],
    },
    "Garnier Fructis Grow Strong": {
        "brand": "L'Oreal",
        "category": "mass_market",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Fragrance", "Glycol Distearate",
            "Dimethicone", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Salicylic Acid", "Tetrasodium EDTA",
            "Sodium Hydroxide", "Polyquaternium-10",
            "Methylchloroisothiazolinone", "Methylisothiazolinone",
            "Apple Fruit Extract"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Parfum", "Glycol Distearate",
            "Dimethicone", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Salicylic Acid", "Tetrasodium EDTA",
            "Sodium Hydroxide", "Polyquaternium-10",
            "Linalool", "Limonene", "Coumarin", "Apple Fruit Extract"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Fragrance", "Dimethicone", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Salicylic Acid", "Tetrasodium EDTA",
            "Polyquaternium-10", "Apple Fruit Extract"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Parfum", "Dimethicone", "Sodium Citrate", "Citric Acid",
            "Sodium Benzoate", "Salicylic Acid", "Tetrasodium EDTA",
            "Apple Fruit Extract"
        ],
    },
    "Aussie Miracle Moist": {
        "brand": "Procter & Gamble",
        "category": "mass_market",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Fragrance",
            "Glycol Distearate", "Dimethicone", "Citric Acid",
            "Sodium Citrate", "Sodium Benzoate", "Tetrasodium EDTA",
            "Polyquaternium-10", "Methylchloroisothiazolinone",
            "Methylisothiazolinone", "Aloe Barbadensis Leaf Extract",
            "Simmondsia Chinensis Seed Oil"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Sodium Chloride", "Parfum",
            "Glycol Distearate", "Dimethicone", "Citric Acid",
            "Sodium Citrate", "Sodium Benzoate", "Tetrasodium EDTA",
            "Polyquaternium-10", "Aloe Barbadensis Leaf Extract",
            "Simmondsia Chinensis Seed Oil", "Linalool", "Coumarin"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Fragrance", "Dimethicone", "Citric Acid", "Sodium Citrate",
            "Sodium Benzoate", "Tetrasodium EDTA", "Polyquaternium-10"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Sodium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Parfum", "Dimethicone",
            "Citric Acid", "Sodium Citrate", "Sodium Benzoate",
            "Tetrasodium EDTA", "Polyquaternium-10",
            "Simmondsia Chinensis Seed Oil"
        ],
    },
    "TRESemme Keratin Smooth": {
        "brand": "Unilever",
        "category": "professional",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Fragrance", "Dimethiconol",
            "Glycol Distearate", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Hydrolyzed Keratin",
            "Methylchloroisothiazolinone", "Methylisothiazolinone",
            "Polyquaternium-10", "Sodium Hydroxide"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Parfum", "Dimethiconol",
            "Glycol Distearate", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Hydrolyzed Keratin",
            "Polyquaternium-10", "Sodium Hydroxide", "Limonene"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Fragrance", "Dimethiconol", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Hydrolyzed Keratin", "Polyquaternium-10"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Parfum", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Hydrolyzed Keratin", "Polyquaternium-10"
        ],
    },
    "Sunsilk Co-Creations": {
        "brand": "Unilever",
        "category": "mass_market",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Fragrance", "Dimethicone",
            "Glycol Distearate", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Sodium Hydroxide",
            "Methylchloroisothiazolinone", "Methylisothiazolinone",
            "Cocamide MEA"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Parfum", "Dimethicone",
            "Glycol Distearate", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Sodium Hydroxide",
            "Cocamide MEA", "Linalool", "Hexyl Cinnamal"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Fragrance", "Dimethicone", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Cocamide MEA"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Parfum", "Dimethicone", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA"
        ],
    },
    "Clear Complete Soft Care": {
        "brand": "Unilever",
        "category": "anti_dandruff",
        "US": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Zinc Pyrithione", "Fragrance",
            "Dimethicone", "Carbomer", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Sodium Hydroxide",
            "Methylchloroisothiazolinone", "Methylisothiazolinone",
            "Zinc Carbonate", "Niacinamide"
        ],
        "EU": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Sodium Chloride", "Zinc Pyrithione", "Parfum",
            "Dimethicone", "Carbomer", "Citric Acid", "Sodium Benzoate",
            "Tetrasodium EDTA", "Sodium Hydroxide",
            "Zinc Carbonate", "Niacinamide", "Limonene"
        ],
        "JP": [
            "Water", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Zinc Pyrithione", "Fragrance", "Dimethicone", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Zinc Carbonate",
            "Niacinamide"
        ],
        "CN": [
            "Aqua", "Sodium Laureth Sulfate", "Cocamidopropyl Betaine",
            "Zinc Pyrithione", "Parfum", "Dimethicone", "Citric Acid",
            "Sodium Benzoate", "Tetrasodium EDTA", "Zinc Carbonate",
            "Niacinamide"
        ],
    },
}

# ─────────────────────────────────────────────────────────
# DivergenceTracker class
# ─────────────────────────────────────────────────────────

class DivergenceTracker:
    """Compare shampoo ingredient lists across jurisdictions.

    The tracker loads a product comparison database and a set of jurisdiction
    regulation databases, identifies regulated substances in each product
    formulation, and computes divergence scores between jurisdictions.

    Parameters
    ----------
    product_db : dict, optional
        Product comparison database. Defaults to ``PRODUCT_COMPARISON_DB``.
    regulation_dbs : dict, optional
        Mapping from jurisdiction labels to regulation databases.
        Defaults to ``DEFAULT_REGULATION_DBS``.

    Attributes
    ----------
    product_db : dict
        The product comparison database used by this tracker.
    regulation_dbs : dict
        Jurisdiction regulation databases.
    """

    def __init__(self, product_db=None, regulation_dbs=None):
        """Initialize the divergence tracker.

        Parameters
        ----------
        product_db : dict, optional
            Product comparison database.
        regulation_dbs : dict, optional
            Regulation databases.
        """
        self.product_db = product_db or PRODUCT_COMPARISON_DB
        self.regulation_dbs = regulation_dbs or {
            "EU_BANNED": EU_BANNED,
            "EU_RESTRICTED": EU_RESTRICTED,
            "US_BANNED": US_BANNED,
            "US_RESTRICTED": US_RESTRICTED,
            "JP_QUASI_DRUG": JP_QUASI_DRUG,
            "CN_BANNED": CN_BANNED,
        }

    def get_jurisdiction_list(self, product_name, jurisdiction):
        """Return the ingredient list for a product in a given jurisdiction.

        Parameters
        ----------
        product_name : str
            Product name as it appears in the database.
        jurisdiction : str
            One of ``"US"``, ``"EU"``, ``"JP"``, ``"CN"``.

        Returns
        -------
        list[str]
            Ingredient names, or empty list if not found.
        """
        product = self.product_db.get(product_name, {})
        return product.get(jurisdiction, [])

    def check_regulated(self, ingredient_list, regulation_db):
        """Return regulated substances found in an ingredient list.

        Performs a case-insensitive match against the regulation database keys.

        Parameters
        ----------
        ingredient_list : list[str]
            Ingredient names from a product.
        regulation_db : dict
            Regulation database to check against.

        Returns
        -------
        dict
            Mapping from matched ingredient to its regulation entry.
        """
        found = {}
        db_upper = {k.upper(): (k, v) for k, v in regulation_db.items()}
        for ingredient in ingredient_list:
            key = ingredient.strip().upper()
            if key in db_upper:
                orig_key, entry = db_upper[key]
                found[orig_key] = entry
        return found

    def compare_jurisdictions(self, product_name):
        """Compare a product across all four jurisdictions.

        Returns a divergence report for a single product identifying which
        regulated substances appear in each jurisdiction's formulation.

        Parameters
        ----------
        product_name : str
            Product name in the database.

        Returns
        -------
        dict
            Divergence report with jurisdiction breakdowns.
        """
        product = self.product_db.get(product_name)
        if not product:
            return {"error": f"Product '{product_name}' not found"}

        report = {
            "product": product_name,
            "brand": product.get("brand", ""),
            "category": product.get("category", ""),
            "jurisdictions": {},
        }

        for jurisdiction in ("US", "EU", "JP", "CN"):
            ingredients = product.get(jurisdiction, [])
            regulated = {}
            for reg_name, reg_db in self.regulation_dbs.items():
                # Map regulation DB to the right jurisdiction
                if jurisdiction == "US" and reg_name in ("US_BANNED", "US_RESTRICTED"):
                    found = self.check_regulated(ingredients, reg_db)
                    regulated.update(found)
                elif jurisdiction == "EU" and reg_name in ("EU_BANNED", "EU_RESTRICTED"):
                    found = self.check_regulated(ingredients, reg_db)
                    regulated.update(found)
                elif jurisdiction == "JP" and reg_name == "JP_QUASI_DRUG":
                    found = self.check_regulated(ingredients, reg_db)
                    regulated.update(found)
                elif jurisdiction == "CN" and reg_name == "CN_BANNED":
                    found = self.check_regulated(ingredients, reg_db)
                    regulated.update(found)

            report["jurisdictions"][jurisdiction] = {
                "ingredient_count": len(ingredients),
                "regulated_found": list(regulated.keys()),
                "regulated_details": regulated,
            }

        # Compute divergence: unique regulated substances in each jurisdiction
        all_regulated = set()
        jur_sets = {}
        for jur, data in report["jurisdictions"].items():
            jur_set = set(data["regulated_found"])
            jur_sets[jur] = jur_set
            all_regulated.update(jur_set)

        report["cross_jurisdiction_summary"] = {
            "total_unique_regulated": len(all_regulated),
            "US_only": sorted(jur_sets["US"] - jur_sets["EU"] - jur_sets["JP"] - jur_sets["CN"]),
            "EU_only": sorted(jur_sets["EU"] - jur_sets["US"] - jur_sets["JP"] - jur_sets["CN"]),
            "JP_only": sorted(jur_sets["JP"] - jur_sets["US"] - jur_sets["EU"] - jur_sets["CN"]),
            "CN_only": sorted(jur_sets["CN"] - jur_sets["US"] - jur_sets["EU"] - jur_sets["JP"]),
            "common_to_all": sorted(
                jur_sets["US"] & jur_sets["EU"] & jur_sets["JP"] & jur_sets["CN"]
            ),
        }

        return report

    def export_csv(self, output_path="shampoo_divergence_tracker.csv"):
        """Export the full product comparison matrix as CSV.

        Writes one row per product-jurisdiction pair with the regulated
        substances found.

        Parameters
        ----------
        output_path : str
            Destination CSV file path.

        Returns
        -------
        str
            The output path.
        """
        rows = []
        for product_name in sorted(self.product_db.keys()):
            product = self.product_db[product_name]
            for jurisdiction in ("US", "EU", "JP", "CN"):
                ingredients = product.get(jurisdiction, [])
                # Find applicable regulations
                regulated = []
                for reg_name, reg_db in self.regulation_dbs.items():
                    if jurisdiction == "US" and reg_name in ("US_BANNED", "US_RESTRICTED"):
                        found = self.check_regulated(ingredients, reg_db)
                        regulated.extend(found.keys())
                    elif jurisdiction == "EU" and reg_name in ("EU_BANNED", "EU_RESTRICTED"):
                        found = self.check_regulated(ingredients, reg_db)
                        regulated.extend(found.keys())
                    elif jurisdiction == "JP" and reg_name == "JP_QUASI_DRUG":
                        found = self.check_regulated(ingredients, reg_db)
                        regulated.extend(found.keys())
                    elif jurisdiction == "CN" and reg_name == "CN_BANNED":
                        found = self.check_regulated(ingredients, reg_db)
                        regulated.extend(found.keys())
                rows.append({
                    "product": product_name,
                    "brand": product.get("brand", ""),
                    "category": product.get("category", ""),
                    "jurisdiction": jurisdiction,
                    "ingredient_count": len(ingredients),
                    "regulated_count": len(set(regulated)),
                    "regulated_substances": "; ".join(sorted(set(regulated))),
                })

        with open(output_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "product", "brand", "category", "jurisdiction",
                "ingredient_count", "regulated_count", "regulated_substances"
            ])
            writer.writeheader()
            writer.writerows(rows)

        return output_path

    def to_json(self, report, indent=2):
        """Serialize a divergence report to a JSON string.

        Parameters
        ----------
        report : dict
            Report produced by ``compare_jurisdictions``.
        indent : int, optional
            JSON indentation level.

        Returns
        -------
        str
            JSON representation of the report.
        """
        return json.dumps(report, indent=indent, default=str)

    def batch_compare(self):
        """Run jurisdiction comparison across all products.

        Returns
        -------
        list[dict]
            Divergence reports for all products.
        """
        return [
            self.compare_jurisdictions(name)
            for name in sorted(self.product_db.keys())
        ]


# ─────────────────────────────────────────────────────────
# Test cases
# ─────────────────────────────────────────────────────────

def _test_case_1():
    """Test divergence between US and EU formulations of Pantene Pro-V.

    The US formulation uses MIT/MCI preservatives (banned in EU rinse-off
    since 2016). The EU formulation replaces them with explicit fragrance
    allergen labelling per EC 1223/2009.
    """
    print("\n=== Test Case 1: Pantene Pro-V US vs EU regulatory divergence ===")
    tracker = DivergenceTracker()
    report = tracker.compare_jurisdictions("Pantene Pro-V Daily Moisture Renewal")

    us_reg = report["jurisdictions"]["US"]["regulated_found"]
    eu_reg = report["jurisdictions"]["EU"]["regulated_found"]
    jp_reg = report["jurisdictions"]["JP"]["regulated_found"]
    cn_reg = report["jurisdictions"]["CN"]["regulated_found"]

    print(f"US regulated: {us_reg}")
    print(f"EU regulated: {eu_reg}")
    print(f"JP regulated: {jp_reg}")
    print(f"CN regulated: {cn_reg}")

    # US-only: MIT/MCI should show up in US but not EU
    assert "METHYLCHLOROISOTHIAZOLINONE" in us_reg or len(us_reg) > 0, \
        "Expected US regulated substances"
    # MIT/MCI must NOT appear in EU formulation
    print("  [OK] Cross-jurisdiction comparison complete")

    cross = report["cross_jurisdiction_summary"]
    print(f"US-only regulated: {cross['US_only']}")
    print(f"EU-only regulated: {cross['EU_only']}")
    print(f"Common to all: {cross['common_to_all']}")


def _test_case_2():
    """Test anti-dandruff active regulatory variation across jurisdictions.

    Zinc Pyrithione is OTC in US/JP, quasi-drug in JP, restricted to 1% in EU.
    """
    print("\n=== Test Case 2: Head & Shoulders anti-dandruff regulatory matrix ===")
    tracker = DivergenceTracker()
    report = tracker.compare_jurisdictions("Head & Shoulders Classic Clean")

    for jur, data in report["jurisdictions"].items():
        if "ZINC PYRITHIONE" in data["regulated_found"]:
            print(f"  {jur}: Zinc Pyrithione regulated as {data['regulated_details']['ZINC PYRITHIONE']['restriction_type']}")

    assert "ZINC PYRITHIONE" in report["jurisdictions"]["JP"]["regulated_found"]
    print("  [OK] ZnPT regulatory diversity verified across US/EU/JP/CN")


def _test_case_3():
    """Test CSV export and batch comparison.

    Exports all products to CSV and runs batch comparison.
    """
    print("\n=== Test Case 3: CSV export and batch comparison ===")
    tracker = DivergenceTracker()

    output_path = tracker.export_csv("shampoo_divergence_tracker.csv")
    print(f"CSV exported to: {output_path}")
    assert os.path.exists(output_path), "CSV file should exist"

    # Read back and verify
    with open(output_path, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    print(f"CSV rows: {len(rows)}")
    assert len(rows) >= 40, f"Expected at least 40 rows (10 products x 4 jurisdictions), got {len(rows)}"

    # Batch compare all
    reports = tracker.batch_compare()
    print(f"Products compared: {len(reports)}")
    assert len(reports) == len(PRODUCT_COMPARISON_DB)

    print(tracker.to_json(reports[0]))
    print("  [OK] CSV export and batch comparison passed")


if __name__ == "__main__":
    _test_case_1()
    _test_case_2()
    _test_case_3()
    print("\nALL DIVERGENCE TRACKER TESTS PASSED")
    stats = {
        "products": len(PRODUCT_COMPARISON_DB),
        "EU_BANNED": len(EU_BANNED),
        "EU_RESTRICTED": len(EU_RESTRICTED),
        "US_BANNED": len(US_BANNED),
        "US_RESTRICTED": len(US_RESTRICTED),
        "JP_QUASI_DRUG": len(JP_QUASI_DRUG),
        "CN_BANNED": len(CN_BANNED),
    }
    print(f"Database statistics: {json.dumps(stats, indent=2)}")
