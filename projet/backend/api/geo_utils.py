"""
Gestionnaire de coordonnées géographiques pour les villes françaises
"""

# Base de données des principales villes françaises avec leurs coordonnées
VILLES_COORDONNEES = {
    # Île-de-France
    'paris': {'lat': 48.8566, 'lng': 2.3522, 'nom': 'Paris', 'zoom': 12},
    'boulogne-billancourt': {'lat': 48.8359, 'lng': 2.2398, 'nom': 'Boulogne-Billancourt', 'zoom': 14},
    'saint-denis': {'lat': 48.9362, 'lng': 2.3574, 'nom': 'Saint-Denis', 'zoom': 14},
    'argenteuil': {'lat': 48.9474, 'lng': 2.2482, 'nom': 'Argenteuil', 'zoom': 14},
    'montreuil': {'lat': 48.8636, 'lng': 2.4437, 'nom': 'Montreuil', 'zoom': 14},
    'créteil': {'lat': 48.7903, 'lng': 2.4555, 'nom': 'Créteil', 'zoom': 14},
    'nanterre': {'lat': 48.8923, 'lng': 2.2069, 'nom': 'Nanterre', 'zoom': 14},
    'vitry-sur-seine': {'lat': 48.7873, 'lng': 2.4037, 'nom': 'Vitry-sur-Seine', 'zoom': 14},
    'colombes': {'lat': 48.9223, 'lng': 2.2578, 'nom': 'Colombes', 'zoom': 14},
    'aulnay-sous-bois': {'lat': 48.9294, 'lng': 2.4951, 'nom': 'Aulnay-sous-Bois', 'zoom': 14},
    'asnières-sur-seine': {'lat': 48.9153, 'lng': 2.2877, 'nom': 'Asnières-sur-Seine', 'zoom': 14},
    'rueil-malmaison': {'lat': 48.8778, 'lng': 2.1839, 'nom': 'Rueil-Malmaison', 'zoom': 14},
    'champigny-sur-marne': {'lat': 48.8171, 'lng': 2.5156, 'nom': 'Champigny-sur-Marne', 'zoom': 14},
    'ville-juifs': {'lat': 48.7879, 'lng': 2.3467, 'nom': 'Ville Juifs', 'zoom': 15},  # Coordonnées approximatives
    'versailles': {'lat': 48.8014, 'lng': 2.1301, 'nom': 'Versailles', 'zoom': 14},
    'aubervilliers': {'lat': 48.9198, 'lng': 2.3816, 'nom': 'Aubervilliers', 'zoom': 14},
    'drancy': {'lat': 48.9285, 'lng': 2.4458, 'nom': 'Drancy', 'zoom': 14},
    'issy-les-moulineaux': {'lat': 48.8247, 'lng': 2.2736, 'nom': 'Issy-les-Moulineaux', 'zoom': 14},
    'levallois-perret': {'lat': 48.8972, 'lng': 2.2881, 'nom': 'Levallois-Perret', 'zoom': 14},
    'noisy-le-grand': {'lat': 48.8484, 'lng': 2.5531, 'nom': 'Noisy-le-Grand', 'zoom': 14},
    'antony': {'lat': 48.7537, 'lng': 2.2979, 'nom': 'Antony', 'zoom': 14},
    'neuilly-sur-seine': {'lat': 48.8846, 'lng': 2.2697, 'nom': 'Neuilly-sur-Seine', 'zoom': 14},
    'clichy': {'lat': 48.9041, 'lng': 2.3063, 'nom': 'Clichy', 'zoom': 14},
    'sarcelles': {'lat': 49.0023, 'lng': 2.3781, 'nom': 'Sarcelles', 'zoom': 14},
    'ivry-sur-seine': {'lat': 48.8139, 'lng': 2.3838, 'nom': 'Ivry-sur-Seine', 'zoom': 14},
    'saint-maur-des-fossés': {'lat': 48.8007, 'lng': 2.4888, 'nom': 'Saint-Maur-des-Fossés'},
    'drancy': {'lat': 48.9239, 'lng': 2.4453, 'nom': 'Drancy'},
    'issy-les-moulineaux': {'lat': 48.8245, 'lng': 2.2730, 'nom': 'Issy-les-Moulineaux'},
    'levallois-perret': {'lat': 48.8970, 'lng': 2.2877, 'nom': 'Levallois-Perret'},
    'neuilly-sur-seine': {'lat': 48.8847, 'lng': 2.2697, 'nom': 'Neuilly-sur-Seine'},
    'antony': {'lat': 48.7545, 'lng': 2.2976, 'nom': 'Antony'},
    'noisy-le-grand': {'lat': 48.8387, 'lng': 2.5528, 'nom': 'Noisy-le-Grand'},
    'versailles': {'lat': 48.8014, 'lng': 2.1301, 'nom': 'Versailles'},
    'clichy': {'lat': 48.9028, 'lng': 2.3069, 'nom': 'Clichy'},
    'sarcelles': {'lat': 49.0011, 'lng': 2.3781, 'nom': 'Sarcelles'},
    'clamart': {'lat': 48.8005, 'lng': 2.2669, 'nom': 'Clamart'},
    'maisons-alfort': {'lat': 48.8052, 'lng': 2.4331, 'nom': 'Maisons-Alfort'},
    'chelles': {'lat': 48.8803, 'lng': 2.5905, 'nom': 'Chelles'},
    'meaux': {'lat': 48.9606, 'lng': 2.8786, 'nom': 'Meaux'},
    'melun': {'lat': 48.5396, 'lng': 2.6610, 'nom': 'Melun'},
    'pontault-combault': {'lat': 48.8033, 'lng': 2.6108, 'nom': 'Pontault-Combault'},
    'savigny-sur-orge': {'lat': 48.6840, 'lng': 2.3425, 'nom': 'Savigny-sur-Orge'},
    'villejuif': {'lat': 48.7936, 'lng': 2.3662, 'nom': 'Villejuif'},
    'la-courneuve': {'lat': 48.9242, 'lng': 2.3928, 'nom': 'La Courneuve'},
    'houilles': {'lat': 48.9278, 'lng': 2.1884, 'nom': 'Houilles'},
    'épinay-sur-seine': {'lat': 48.9538, 'lng': 2.3094, 'nom': 'Épinay-sur-Seine'},
    'vincennes': {'lat': 48.8478, 'lng': 2.4363, 'nom': 'Vincennes'},
    'choisy-le-roi': {'lat': 48.7655, 'lng': 2.4094, 'nom': 'Choisy-le-Roi'},
    'fontenay-sous-bois': {'lat': 48.8479, 'lng': 2.4711, 'nom': 'Fontenay-sous-Bois'},
    'bondy': {'lat': 48.9023, 'lng': 2.4832, 'nom': 'Bondy'},
    'malakoff': {'lat': 48.8176, 'lng': 2.2997, 'nom': 'Malakoff'},
    'rosny-sous-bois': {'lat': 48.8709, 'lng': 2.4836, 'nom': 'Rosny-sous-Bois'},
    'livry-gargan': {'lat': 48.9138, 'lng': 2.5347, 'nom': 'Livry-Gargan'},
    'alfortville': {'lat': 48.8057, 'lng': 2.4195, 'nom': 'Alfortville'},
    'sevran': {'lat': 48.9402, 'lng': 2.5331, 'nom': 'Sevran'},
    'villemomble': {'lat': 48.8839, 'lng': 2.5107, 'nom': 'Villemomble'},
    'charenton-le-pont': {'lat': 48.8224, 'lng': 2.4096, 'nom': 'Charenton-le-Pont'},
    'franconville': {'lat': 48.9889, 'lng': 2.2264, 'nom': 'Franconville'},
    'gagny': {'lat': 48.8825, 'lng': 2.5353, 'nom': 'Gagny'},
    'goussainville': {'lat': 49.0178, 'lng': 2.4644, 'nom': 'Goussainville'},
    'herblay': {'lat': 49.0117, 'lng': 2.1636, 'nom': 'Herblay'},
    'thiais': {'lat': 48.7628, 'lng': 2.3975, 'nom': 'Thiais'},
    'villeneuve-saint-georges': {'lat': 48.7339, 'lng': 2.4447, 'nom': 'Villeneuve-Saint-Georges'},
    'villiers-sur-marne': {'lat': 48.8265, 'lng': 2.5410, 'nom': 'Villiers-sur-Marne'},
    'palaiseau': {'lat': 48.7146, 'lng': 2.2477, 'nom': 'Palaiseau'},
    'sucy-en-brie': {'lat': 48.7700, 'lng': 2.5217, 'nom': 'Sucy-en-Brie'},
    'garges-lès-gonesse': {'lat': 48.9722, 'lng': 2.3983, 'nom': 'Garges-lès-Gonesse'},
    'bagneux': {'lat': 48.7959, 'lng': 2.3113, 'nom': 'Bagneux'},
    'cergy': {'lat': 49.0369, 'lng': 2.0778, 'nom': 'Cergy'},
    'pontoise': {'lat': 49.0515, 'lng': 2.0944, 'nom': 'Pontoise'},
    'conflans-sainte-honorine': {'lat': 49.0003, 'lng': 2.0997, 'nom': 'Conflans-Sainte-Honorine'},
    'montfermeil': {'lat': 48.8983, 'lng': 2.5703, 'nom': 'Montfermeil'},
    'tremblay-en-france': {'lat': 48.9505, 'lng': 2.5714, 'nom': 'Tremblay-en-France'},
    'villeneuve-la-garenne': {'lat': 48.9370, 'lng': 2.3246, 'nom': 'Villeneuve-la-Garenne'},
    'bobigny': {'lat': 48.9075, 'lng': 2.4447, 'nom': 'Bobigny'},
    'stains': {'lat': 48.9548, 'lng': 2.3825, 'nom': 'Stains'},
    'pantin': {'lat': 48.8944, 'lng': 2.4028, 'nom': 'Pantin'},
    'ivry-sur-seine': {'lat': 48.8137, 'lng': 2.3854, 'nom': 'Ivry-sur-Seine'},
    'saint-ouen': {'lat': 48.9047, 'lng': 2.3339, 'nom': 'Saint-Ouen'},
    'creteil': {'lat': 48.7903, 'lng': 2.4555, 'nom': 'Créteil'},
    'bagnolet': {'lat': 48.8697, 'lng': 2.4169, 'nom': 'Bagnolet'},
    'romainville': {'lat': 48.8842, 'lng': 2.4335, 'nom': 'Romainville'},
    'les-lilas': {'lat': 48.8794, 'lng': 2.4181, 'nom': 'Les Lilas'},
    'le-pre-saint-gervais': {'lat': 48.8856, 'lng': 2.4047, 'nom': 'Le Pré-Saint-Gervais'},
    'pierrefitte-sur-seine': {'lat': 48.9647, 'lng': 2.3622, 'nom': 'Pierrefitte-sur-Seine'},
    'villetaneuse': {'lat': 48.9595, 'lng': 2.3447, 'nom': 'Villetaneuse'},
    'dugny': {'lat': 48.9533, 'lng': 2.4194, 'nom': 'Dugny'},
    'le-blanc-mesnil': {'lat': 48.9403, 'lng': 2.4586, 'nom': 'Le Blanc-Mesnil'},
    'noisy-le-sec': {'lat': 48.8925, 'lng': 2.4589, 'nom': 'Noisy-le-Sec'},
    'les-pavillons-sous-bois': {'lat': 48.9058, 'lng': 2.5089, 'nom': 'Les Pavillons-sous-Bois'},
    'saint-mandé': {'lat': 48.8447, 'lng': 2.4181, 'nom': 'Saint-Mandé'},
    'joinville-le-pont': {'lat': 48.8197, 'lng': 2.4689, 'nom': 'Joinville-le-Pont'},
    'nogent-sur-marne': {'lat': 48.8372, 'lng': 2.4831, 'nom': 'Nogent-sur-Marne'},
    'perreux-sur-marne': {'lat': 48.8433, 'lng': 2.5047, 'nom': 'Le Perreux-sur-Marne'},
    'bry-sur-marne': {'lat': 48.8397, 'lng': 2.5222, 'nom': 'Bry-sur-Marne'},
    'chennevieres-sur-marne': {'lat': 48.7975, 'lng': 2.5333, 'nom': 'Chennevières-sur-Marne'},
    'ormesson-sur-marne': {'lat': 48.7867, 'lng': 2.5394, 'nom': 'Ormesson-sur-Marne'},
    'la-queue-en-brie': {'lat': 48.7889, 'lng': 2.5761, 'nom': 'La Queue-en-Brie'},
    'roissy-en-brie': {'lat': 48.7944, 'lng': 2.6519, 'nom': 'Roissy-en-Brie'},
    'ozoir-la-ferrière': {'lat': 48.7647, 'lng': 2.6744, 'nom': 'Ozoir-la-Ferrière'},
    'grigny': {'lat': 48.6531, 'lng': 2.3825, 'nom': 'Grigny'},
    'viry-chatillon': {'lat': 48.6711, 'lng': 2.3781, 'nom': 'Viry-Châtillon'},
    'athis-mons': {'lat': 48.7103, 'lng': 2.3889, 'nom': 'Athis-Mons'},
    'juvisy-sur-orge': {'lat': 48.6889, 'lng': 2.3747, 'nom': 'Juvisy-sur-Orge'},
    'paray-vieille-poste': {'lat': 48.7131, 'lng': 2.3669, 'nom': 'Paray-Vieille-Poste'},
    'brunoy': {'lat': 48.6972, 'lng': 2.5019, 'nom': 'Brunoy'},
    'yerres': {'lat': 48.7131, 'lng': 2.4889, 'nom': 'Yerres'},
    'montgeron': {'lat': 48.7019, 'lng': 2.4617, 'nom': 'Montgeron'},
    'draveil': {'lat': 48.6842, 'lng': 2.4139, 'nom': 'Draveil'},
    'vigneux-sur-seine': {'lat': 48.7014, 'lng': 2.4189, 'nom': 'Vigneux-sur-Seine'},
    'corbeil-essonnes': {'lat': 48.6111, 'lng': 2.4781, 'nom': 'Corbeil-Essonnes'},
    'evry': {'lat': 48.6289, 'lng': 2.4456, 'nom': 'Évry'},
    'ris-orangis': {'lat': 48.6514, 'lng': 2.4133, 'nom': 'Ris-Orangis'},
    'sainte-genevieve-des-bois': {'lat': 48.6456, 'lng': 2.3269, 'nom': 'Sainte-Geneviève-des-Bois'},
    'massy': {'lat': 48.7306, 'lng': 2.2700, 'nom': 'Massy'},
    'longjumeau': {'lat': 48.6956, 'lng': 2.2944, 'nom': 'Longjumeau'},
    'chilly-mazarin': {'lat': 48.7011, 'lng': 2.3153, 'nom': 'Chilly-Mazarin'},
    'morangis': {'lat': 48.7042, 'lng': 2.3306, 'nom': 'Morangis'},
    'verrières-le-buisson': {'lat': 48.7469, 'lng': 2.2694, 'nom': 'Verrières-le-Buisson'},
    'wissous': {'lat': 48.7306, 'lng': 2.3244, 'nom': 'Wissous'},
    'fresnes': {'lat': 48.7578, 'lng': 2.3289, 'nom': 'Fresnes'},
    'rungis': {'lat': 48.7506, 'lng': 2.3519, 'nom': 'Rungis'},
    'chevilly-larue': {'lat': 48.7681, 'lng': 2.3469, 'nom': 'Chevilly-Larue'},
    'l-hay-les-roses': {'lat': 48.7789, 'lng': 2.3333, 'nom': 'L\'Haÿ-les-Roses'},
    'cachan': {'lat': 48.7911, 'lng': 2.3289, 'nom': 'Cachan'},
    'arcueil': {'lat': 48.8044, 'lng': 2.3331, 'nom': 'Arcueil'},
    'gentilly': {'lat': 48.8131, 'lng': 2.3442, 'nom': 'Gentilly'},
    'kremlin-bicetre': {'lat': 48.8089, 'lng': 2.3606, 'nom': 'Le Kremlin-Bicêtre'},
    'chatillon': {'lat': 48.8044, 'lng': 2.2944, 'nom': 'Châtillon'},
    'montrouge': {'lat': 48.8178, 'lng': 2.3194, 'nom': 'Montrouge'},
    'vanves': {'lat': 48.8233, 'lng': 2.2944, 'nom': 'Vanves'},
    'bourg-la-reine': {'lat': 48.7789, 'lng': 2.3156, 'nom': 'Bourg-la-Reine'},
    'sceaux': {'lat': 48.7789, 'lng': 2.2944, 'nom': 'Sceaux'},
    'fontenay-aux-roses': {'lat': 48.7911, 'lng': 2.2856, 'nom': 'Fontenay-aux-Roses'},
    'le-plessis-robinson': {'lat': 48.7789, 'lng': 2.2631, 'nom': 'Le Plessis-Robinson'},
    'chatenay-malabry': {'lat': 48.7669, 'lng': 2.2681, 'nom': 'Châtenay-Malabry'},
    'ville-d-avray': {'lat': 48.8244, 'lng': 2.1906, 'nom': 'Ville-d\'Avray'},
    'sevres': {'lat': 48.8244, 'lng': 2.2081, 'nom': 'Sèvres'},
    'chaville': {'lat': 48.8089, 'lng': 2.1856, 'nom': 'Chaville'},
    'viroflay': {'lat': 48.8044, 'lng': 2.1719, 'nom': 'Viroflay'},
    'meudon': {'lat': 48.8089, 'lng': 2.2356, 'nom': 'Meudon'},
    'bellevue': {'lat': 48.8244, 'lng': 2.2244, 'nom': 'Bellevue'},
    'saint-cloud': {'lat': 48.8433, 'lng': 2.2181, 'nom': 'Saint-Cloud'},
    'garches': {'lat': 48.8433, 'lng': 2.1856, 'nom': 'Garches'},
    'vaucresson': {'lat': 48.8389, 'lng': 2.1581, 'nom': 'Vaucresson'},
    'marnes-la-coquette': {'lat': 48.8356, 'lng': 2.1681, 'nom': 'Marnes-la-Coquette'},
    'suresnes': {'lat': 48.8681, 'lng': 2.2294, 'nom': 'Suresnes'},
    'puteaux': {'lat': 48.8844, 'lng': 2.2381, 'nom': 'Puteaux'},
    'courbevoie': {'lat': 48.8972, 'lng': 2.2550, 'nom': 'Courbevoie'},
    'la-garenne-colombes': {'lat': 48.9075, 'lng': 2.2469, 'nom': 'La Garenne-Colombes'},
    'bois-colombes': {'lat': 48.9186, 'lng': 2.2681, 'nom': 'Bois-Colombes'},
    'gennevilliers': {'lat': 48.9333, 'lng': 2.2969, 'nom': 'Gennevilliers'},
    'villeneuve-la-garenne': {'lat': 48.9370, 'lng': 2.3246, 'nom': 'Villeneuve-la-Garenne'},
    'saint-gratien': {'lat': 48.9667, 'lng': 2.2856, 'nom': 'Saint-Gratien'},
    'enghien-les-bains': {'lat': 48.9708, 'lng': 2.3081, 'nom': 'Enghien-les-Bains'},
    'montmorency': {'lat': 48.9889, 'lng': 2.3244, 'nom': 'Montmorency'},
    'deuil-la-barre': {'lat': 48.9708, 'lng': 2.3244, 'nom': 'Deuil-la-Barre'},
    'groslay': {'lat': 49.0069, 'lng': 2.3444, 'nom': 'Groslay'},
    'montlignon': {'lat': 49.0111, 'lng': 2.3000, 'nom': 'Montlignon'},
    'soisy-sous-montmorency': {'lat': 48.9889, 'lng': 2.3019, 'nom': 'Soisy-sous-Montmorency'},
    'andilly': {'lat': 49.0069, 'lng': 2.2981, 'nom': 'Andilly'},
    'margency': {'lat': 49.0069, 'lng': 2.2881, 'nom': 'Margency'},
    'eaubonne': {'lat': 48.9889, 'lng': 2.2781, 'nom': 'Eaubonne'},
    'ermont': {'lat': 49.0069, 'lng': 2.2581, 'nom': 'Ermont'},
    'saint-leu-la-foret': {'lat': 49.0153, 'lng': 2.2456, 'nom': 'Saint-Leu-la-Forêt'},
    'taverny': {'lat': 49.0264, 'lng': 2.2181, 'nom': 'Taverny'},
    'beauchamp': {'lat': 49.0153, 'lng': 2.1981, 'nom': 'Beauchamp'},
    'pierrelaye': {'lat': 49.0208, 'lng': 2.1531, 'nom': 'Pierrelaye'},
    'bessancourt': {'lat': 49.0347, 'lng': 2.2031, 'nom': 'Bessancourt'},
    'frépillon': {'lat': 49.0458, 'lng': 2.2031, 'nom': 'Frépillon'},
    'méry-sur-oise': {'lat': 49.0625, 'lng': 2.1831, 'nom': 'Méry-sur-Oise'},
    'auvers-sur-oise': {'lat': 49.0708, 'lng': 2.1706, 'nom': 'Auvers-sur-Oise'},
    'valmondois': {'lat': 49.0903, 'lng': 2.1856, 'nom': 'Valmondois'},
    'l-isle-adam': {'lat': 49.1125, 'lng': 2.2244, 'nom': 'L\'Isle-Adam'},
    'parmain': {'lat': 49.1181, 'lng': 2.2006, 'nom': 'Parmain'},
    'champagne-sur-oise': {'lat': 49.1347, 'lng': 2.2081, 'nom': 'Champagne-sur-Oise'},
    'persan': {'lat': 49.1514, 'lng': 2.2744, 'nom': 'Persan'},
    'beaumont-sur-oise': {'lat': 49.1431, 'lng': 2.2906, 'nom': 'Beaumont-sur-Oise'},
    'nointel': {'lat': 49.1806, 'lng': 2.1031, 'nom': 'Nointel'},
    'saint-martin-du-tertre': {'lat': 49.1569, 'lng': 2.3231, 'nom': 'Saint-Martin-du-Tertre'},
    'mours': {'lat': 49.1431, 'lng': 2.0831, 'nom': 'Mours'},
    'bernes-sur-oise': {'lat': 49.1514, 'lng': 2.2931, 'nom': 'Bernes-sur-Oise'},
    'bruyeres-sur-oise': {'lat': 49.1597, 'lng': 2.3244, 'nom': 'Bruyères-sur-Oise'},
    'viarmes': {'lat': 49.1264, 'lng': 2.3731, 'nom': 'Viarmes'},
    'luzarches': {'lat': 49.1097, 'lng': 2.4194, 'nom': 'Luzarches'},
    'chaumontel': {'lat': 49.1319, 'lng': 2.4244, 'nom': 'Chaumontel'},
    'fosses': {'lat': 49.0958, 'lng': 2.5181, 'nom': 'Fosses'},
    'roissy-en-france': {'lat': 49.0083, 'lng': 2.5181, 'nom': 'Roissy-en-France'},
    'le-mesnil-amelot': {'lat': 49.0153, 'lng': 2.5856, 'nom': 'Le Mesnil-Amelot'},
    'villeron': {'lat': 49.0347, 'lng': 2.5431, 'nom': 'Villeron'},
    'saint-witz': {'lat': 49.0903, 'lng': 2.5681, 'nom': 'Saint-Witz'},
    'plailly': {'lat': 49.1042, 'lng': 2.5931, 'nom': 'Plailly'},
    'mortefontaine': {'lat': 49.1319, 'lng': 2.6044, 'nom': 'Mortefontaine'},
    'ville-juif': {'lat': 48.7936, 'lng': 2.3662, 'nom': 'Villejuif'},
    'villejuif': {'lat': 48.7936, 'lng': 2.3662, 'nom': 'Villejuif'},
    
    # Grandes villes françaises
    'marseille': {'lat': 43.2965, 'lng': 5.3698, 'nom': 'Marseille'},
    'lyon': {'lat': 45.7640, 'lng': 4.8357, 'nom': 'Lyon'},
    'toulouse': {'lat': 43.6047, 'lng': 1.4442, 'nom': 'Toulouse'},
    'nice': {'lat': 43.7102, 'lng': 7.2620, 'nom': 'Nice'},
    'nantes': {'lat': 47.2184, 'lng': -1.5536, 'nom': 'Nantes'},
    'strasbourg': {'lat': 48.5734, 'lng': 7.7521, 'nom': 'Strasbourg'},
    'montpellier': {'lat': 43.6110, 'lng': 3.8767, 'nom': 'Montpellier'},
    'bordeaux': {'lat': 44.8378, 'lng': -0.5792, 'nom': 'Bordeaux'},
    'lille': {'lat': 50.6292, 'lng': 3.0573, 'nom': 'Lille'},
    'rennes': {'lat': 48.1173, 'lng': -1.6778, 'nom': 'Rennes'},
    'reims': {'lat': 49.2583, 'lng': 4.0317, 'nom': 'Reims'},
    'le-havre': {'lat': 49.4944, 'lng': 0.1079, 'nom': 'Le Havre'},
    'saint-étienne': {'lat': 45.4397, 'lng': 4.3872, 'nom': 'Saint-Étienne'},
    'toulon': {'lat': 43.1242, 'lng': 5.9280, 'nom': 'Toulon'},
    'angers': {'lat': 47.4784, 'lng': -0.5632, 'nom': 'Angers'},
    'grenoble': {'lat': 45.1885, 'lng': 5.7245, 'nom': 'Grenoble'},
    'dijon': {'lat': 47.3220, 'lng': 5.0415, 'nom': 'Dijon'},
    'nîmes': {'lat': 43.8367, 'lng': 4.3601, 'nom': 'Nîmes'},
    'aix-en-provence': {'lat': 43.5297, 'lng': 5.4474, 'nom': 'Aix-en-Provence'},
    'saint-quentin-en-yvelines': {'lat': 48.7685, 'lng': 2.0448, 'nom': 'Saint-Quentin-en-Yvelines'},
    'le-mans': {'lat': 48.0061, 'lng': 0.1996, 'nom': 'Le Mans'},
    'brest': {'lat': 48.3904, 'lng': -4.4861, 'nom': 'Brest'},
    'tours': {'lat': 47.3941, 'lng': 0.6848, 'nom': 'Tours'},
    'amiens': {'lat': 49.8941, 'lng': 2.2958, 'nom': 'Amiens'},
    'limoges': {'lat': 45.8336, 'lng': 1.2611, 'nom': 'Limoges'},
    'annecy': {'lat': 45.8992, 'lng': 6.1294, 'nom': 'Annecy'},
    'perpignan': {'lat': 42.6886, 'lng': 2.8948, 'nom': 'Perpignan'},
    'boulogne-sur-mer': {'lat': 50.7264, 'lng': 1.6147, 'nom': 'Boulogne-sur-Mer'},
    'metz': {'lat': 49.1193, 'lng': 6.1757, 'nom': 'Metz'},
    'besançon': {'lat': 47.2380, 'lng': 6.0243, 'nom': 'Besançon'},
    'orléans': {'lat': 47.9029, 'lng': 1.9039, 'nom': 'Orléans'},
    'mulhouse': {'lat': 47.7508, 'lng': 7.3359, 'nom': 'Mulhouse'},
    'rouen': {'lat': 49.4431, 'lng': 1.0993, 'nom': 'Rouen'},
    'caen': {'lat': 49.1829, 'lng': -0.3707, 'nom': 'Caen'},
    'nancy': {'lat': 48.6921, 'lng': 6.1844, 'nom': 'Nancy'},
    'argenteuil': {'lat': 48.9474, 'lng': 2.2482, 'nom': 'Argenteuil'},
    'saint-paul': {'lat': -21.0099, 'lng': 55.2708, 'nom': 'Saint-Paul'},
    'roubaix': {'lat': 50.6942, 'lng': 3.1746, 'nom': 'Roubaix'},
    'tourcoing': {'lat': 50.7236, 'lng': 3.1609, 'nom': 'Tourcoing'},
    'nanterre': {'lat': 48.8923, 'lng': 2.2069, 'nom': 'Nanterre'},
    'avignon': {'lat': 43.9493, 'lng': 4.8059, 'nom': 'Avignon'},
    'créteil': {'lat': 48.7903, 'lng': 2.4555, 'nom': 'Créteil'},
    'dunkerque': {'lat': 51.0347, 'lng': 2.3770, 'nom': 'Dunkerque'},
    'poitiers': {'lat': 46.5802, 'lng': 0.3404, 'nom': 'Poitiers'},
    'fort-de-france': {'lat': 14.6037, 'lng': -61.0594, 'nom': 'Fort-de-France'},
    'courbevoie': {'lat': 48.8972, 'lng': 2.2550, 'nom': 'Courbevoie'},
    'versailles': {'lat': 48.8014, 'lng': 2.1301, 'nom': 'Versailles'},
    'pau': {'lat': 43.2951, 'lng': -0.3707, 'nom': 'Pau'},
    'la-rochelle': {'lat': 46.1603, 'lng': -1.1511, 'nom': 'La Rochelle'},
    'calais': {'lat': 50.9513, 'lng': 1.8587, 'nom': 'Calais'},
    'cannes': {'lat': 43.5528, 'lng': 7.0174, 'nom': 'Cannes'},
    'antibes': {'lat': 43.5804, 'lng': 7.1251, 'nom': 'Antibes'},
    'saint-nazaire': {'lat': 47.2734, 'lng': -2.2136, 'nom': 'Saint-Nazaire'},
    'colmar': {'lat': 48.0794, 'lng': 7.3580, 'nom': 'Colmar'},
    'quimper': {'lat': 47.9960, 'lng': -4.1020, 'nom': 'Quimper'},
    'valence': {'lat': 44.9334, 'lng': 4.8924, 'nom': 'Valence'},
    'bourges': {'lat': 47.0810, 'lng': 2.3987, 'nom': 'Bourges'},
    'saint-brieuc': {'lat': 48.5144, 'lng': -2.7650, 'nom': 'Saint-Brieuc'},
    'la-roche-sur-yon': {'lat': 46.6707, 'lng': -1.4268, 'nom': 'La Roche-sur-Yon'},
    'saint-malo': {'lat': 48.6500, 'lng': -2.0247, 'nom': 'Saint-Malo'},
    'chambéry': {'lat': 45.5646, 'lng': 5.9178, 'nom': 'Chambéry'},
    'biarritz': {'lat': 43.4832, 'lng': -1.5586, 'nom': 'Biarritz'},
    'auxerre': {'lat': 47.7985, 'lng': 3.5731, 'nom': 'Auxerre'},
    'blois': {'lat': 47.5868, 'lng': 1.3350, 'nom': 'Blois'},
    'troyes': {'lat': 48.2973, 'lng': 4.0744, 'nom': 'Troyes'},
    'niort': {'lat': 46.3236, 'lng': -0.4594, 'nom': 'Niort'},
    'lorient': {'lat': 47.7482, 'lng': -3.3669, 'nom': 'Lorient'},
    'belfort': {'lat': 47.6377, 'lng': 6.8632, 'nom': 'Belfort'},
    'chalon-sur-saone': {'lat': 46.7806, 'lng': 4.8537, 'nom': 'Chalon-sur-Saône'},
    'lens': {'lat': 50.4329, 'lng': 2.8270, 'nom': 'Lens'},
    'montluçon': {'lat': 46.3408, 'lng': 2.6038, 'nom': 'Montluçon'},
    'vannes': {'lat': 47.6584, 'lng': -2.7606, 'nom': 'Vannes'},
    'fréjus': {'lat': 43.4330, 'lng': 6.7369, 'nom': 'Fréjus'},
    'arles': {'lat': 43.6761, 'lng': 4.6306, 'nom': 'Arles'},
    'narbonne': {'lat': 43.1839, 'lng': 3.0044, 'nom': 'Narbonne'},
    'grasse': {'lat': 43.6584, 'lng': 6.9226, 'nom': 'Grasse'},
    'villeurbanne': {'lat': 45.7665, 'lng': 4.8798, 'nom': 'Villeurbanne'},
    'saint-denis': {'lat': 48.9362, 'lng': 2.3574, 'nom': 'Saint-Denis'},
    'saint-pierre': {'lat': -21.3393, 'lng': 55.4781, 'nom': 'Saint-Pierre'},
    'cayenne': {'lat': 4.9346, 'lng': -52.3303, 'nom': 'Cayenne'},
    'nouméa': {'lat': -22.2758, 'lng': 166.4581, 'nom': 'Nouméa'},
    'papeete': {'lat': -17.5516, 'lng': -149.5585, 'nom': 'Papeete'},
    'mamoudzou': {'lat': -12.7806, 'lng': 45.2278, 'nom': 'Mamoudzou'},
    'saint-barthélemy': {'lat': 17.9000, 'lng': -62.8333, 'nom': 'Saint-Barthélemy'},
    'saint-martin': {'lat': 18.0708, 'lng': -63.0501, 'nom': 'Saint-Martin'},
    'wallis-et-futuna': {'lat': -13.7687, 'lng': -177.1562, 'nom': 'Wallis-et-Futuna'},
    'clipperton': {'lat': 10.3019, 'lng': -109.2158, 'nom': 'Clipperton'},
    'saint-pierre-et-miquelon': {'lat': 46.8852, 'lng': -56.3159, 'nom': 'Saint-Pierre-et-Miquelon'},
    'terres-australes': {'lat': -49.3500, 'lng': 70.2167, 'nom': 'Terres australes et antarctiques françaises'},
    
    # Coordonnées par défaut pour la France
    'france': {'lat': 46.603354, 'lng': 1.8883335, 'nom': 'France'},
    'default': {'lat': 46.603354, 'lng': 1.8883335, 'nom': 'France'}
}


def obtenir_coordonnees_ville(ville_nom):
    """
    Obtient les coordonnées géographiques d'une ville
    
    Args:
        ville_nom: Nom de la ville (sera normalisé)
        
    Returns:
        dict: Contient lat, lng et nom de la ville
    """
    if not ville_nom:
        return VILLES_COORDONNEES['default']
    
    # Normaliser le nom de la ville
    ville_norm = ville_nom.lower().strip()
    
    # Remplacements communs
    ville_norm = ville_norm.replace(' ', '-')
    ville_norm = ville_norm.replace('_', '-')
    ville_norm = ville_norm.replace("'", '-')
    ville_norm = ville_norm.replace('é', 'e')
    ville_norm = ville_norm.replace('è', 'e')
    ville_norm = ville_norm.replace('ê', 'e')
    ville_norm = ville_norm.replace('ë', 'e')
    ville_norm = ville_norm.replace('à', 'a')
    ville_norm = ville_norm.replace('â', 'a')
    ville_norm = ville_norm.replace('ä', 'a')
    ville_norm = ville_norm.replace('ç', 'c')
    ville_norm = ville_norm.replace('î', 'i')
    ville_norm = ville_norm.replace('ï', 'i')
    ville_norm = ville_norm.replace('ô', 'o')
    ville_norm = ville_norm.replace('ö', 'o')
    ville_norm = ville_norm.replace('ù', 'u')
    ville_norm = ville_norm.replace('û', 'u')
    ville_norm = ville_norm.replace('ü', 'u')
    ville_norm = ville_norm.replace('ÿ', 'y')
    
    # Rechercher directement
    if ville_norm in VILLES_COORDONNEES:
        return VILLES_COORDONNEES[ville_norm]
    
    # Rechercher par correspondance partielle
    for ville_key, coordonnees in VILLES_COORDONNEES.items():
        if ville_key != 'default' and ville_key != 'france':
            if ville_norm in ville_key or ville_key in ville_norm:
                return coordonnees
    
    # Rechercher sans tirets
    ville_sans_tiret = ville_norm.replace('-', '')
    for ville_key, coordonnees in VILLES_COORDONNEES.items():
        if ville_key != 'default' and ville_key != 'france':
            ville_key_sans_tiret = ville_key.replace('-', '')
            if ville_sans_tiret == ville_key_sans_tiret:
                return coordonnees
    
    # Si aucune correspondance trouvée, retourner les coordonnées par défaut
    return VILLES_COORDONNEES['default']


def obtenir_coordonnees_multiples_villes(villes_list):
    """
    Obtient les coordonnées pour plusieurs villes
    
    Args:
        villes_list: Liste des noms de villes
        
    Returns:
        dict: Dictionnaire avec les coordonnées pour chaque ville
    """
    coordonnees = {}
    
    for ville in villes_list:
        if ville:
            coordonnees[ville] = obtenir_coordonnees_ville(ville)
    
    return coordonnees


def calculer_centre_geographique(coordonnees_list):
    """
    Calcule le centre géographique d'une liste de coordonnées
    
    Args:
        coordonnees_list: Liste de dictionnaires avec 'lat' et 'lng'
        
    Returns:
        dict: Centre géographique avec 'lat' et 'lng'
    """
    if not coordonnees_list:
        return VILLES_COORDONNEES['default']
    
    if len(coordonnees_list) == 1:
        return coordonnees_list[0]
    
    # Calculer la moyenne des coordonnées
    total_lat = sum(coord['lat'] for coord in coordonnees_list)
    total_lng = sum(coord['lng'] for coord in coordonnees_list)
    
    centre = {
        'lat': total_lat / len(coordonnees_list),
        'lng': total_lng / len(coordonnees_list),
        'nom': f'Centre de {len(coordonnees_list)} villes'
    }
    
    return centre

def normaliser_nom_ville_pour_recherche(nom_ville):
    """
    Normalise le nom d'une ville pour la recherche dans la base de données
    
    Args:
        nom_ville: Nom de la ville à normaliser
        
    Returns:
        str: Nom normalisé pour la recherche
    """
    if not nom_ville:
        return None
    
    # Convertir en minuscules et nettoyer
    nom_normalise = nom_ville.lower().strip()
    
    # Remplacements spécifiques
    remplacements = {
        ' ': '-',
        '_': '-',
        'saint ': 'saint-',
        'sainte ': 'sainte-',
        'le ': 'le-',
        'la ': 'la-',
        'les ': 'les-',
        'sur ': 'sur-',
        'sous ': 'sous-',
        'en ': 'en-',
        'de ': 'de-',
        'du ': 'du-',
        'des ': 'des-',
        'd\'': 'd-',
        'l\'': 'l-'
    }
    
    for ancien, nouveau in remplacements.items():
        nom_normalise = nom_normalise.replace(ancien, nouveau)
    
    # Nettoyer les tirets multiples
    while '--' in nom_normalise:
        nom_normalise = nom_normalise.replace('--', '-')
    
    # Retirer les tirets en début et fin
    nom_normalise = nom_normalise.strip('-')
    
    return nom_normalise

def obtenir_coordonnees_ville_amelioree(nom_ville):
    """
    Version améliorée pour obtenir les coordonnées d'une ville
    Utilise plusieurs stratégies de recherche
    
    Args:
        nom_ville: Nom de la ville
        
    Returns:
        dict: Coordonnées complètes avec métadonnées
    """
    if not nom_ville:
        return {
            'lat': 48.8566,  # Paris par défaut
            'lng': 2.3522,
            'zoom': 10,
            'nom': 'Paris (défaut)',
            'ville_trouvee': False,
            'ville_recherchee': nom_ville
        }
    
    # Stratégie 1: Recherche directe avec normalisation
    nom_normalise = normaliser_nom_ville_pour_recherche(nom_ville)
    
    if nom_normalise and nom_normalise in VILLES_COORDONNEES:
        coordonnees = VILLES_COORDONNEES[nom_normalise]
        return {
            'lat': coordonnees['lat'],
            'lng': coordonnees['lng'],
            'zoom': coordonnees.get('zoom', 14),
            'nom': coordonnees['nom'],
            'ville_trouvee': True,
            'ville_recherchee': nom_ville,
            'ville_normalisee': nom_normalise,
            'methode_recherche': 'normalisation'
        }
    
    # Stratégie 2: Recherche avec variantes
    variantes = [
        nom_ville.lower(),
        nom_ville.lower().replace(' ', '-'),
        nom_ville.lower().replace('_', '-'),
        nom_ville.lower().replace('saint ', 'saint-'),
        nom_ville.lower().replace('sainte ', 'sainte-'),
        nom_ville.lower().replace(' sur ', '-sur-'),
        nom_ville.lower().replace(' sous ', '-sous-'),
        nom_ville.lower().replace(' en ', '-en-'),
        nom_ville.lower().replace(' de ', '-de-'),
        nom_ville.lower().replace(' le ', '-le-'),
        nom_ville.lower().replace(' la ', '-la-'),
        nom_ville.lower().replace(' les ', '-les-')
    ]
    
    for variante in variantes:
        if variante in VILLES_COORDONNEES:
            coordonnees = VILLES_COORDONNEES[variante]
            return {
                'lat': coordonnees['lat'],
                'lng': coordonnees['lng'],
                'zoom': coordonnees.get('zoom', 14),
                'nom': coordonnees['nom'],
                'ville_trouvee': True,
                'ville_recherchee': nom_ville,
                'ville_normalisee': variante,
                'methode_recherche': 'variante'
            }
    
    # Stratégie 3: Recherche partielle (contient le nom)
    for ville_key, coordonnees in VILLES_COORDONNEES.items():
        if (nom_ville.lower() in ville_key.lower() or 
            ville_key.lower() in nom_ville.lower()):
            return {
                'lat': coordonnees['lat'],
                'lng': coordonnees['lng'],
                'zoom': coordonnees.get('zoom', 14),
                'nom': coordonnees['nom'],
                'ville_trouvee': True,
                'ville_recherchee': nom_ville,
                'ville_normalisee': ville_key,
                'methode_recherche': 'partielle'
            }
    
    # Aucune correspondance trouvée, retourner Paris par défaut
    print(f"[WARNING] Ville '{nom_ville}' non trouvée dans la base de données géographiques")
    return {
        'lat': 48.8566,  # Paris
        'lng': 2.3522,
        'zoom': 10,
        'nom': f'Paris (ville "{nom_ville}" non trouvée)',
        'ville_trouvee': False,
        'ville_recherchee': nom_ville,
        'ville_normalisee': nom_normalise,
        'methode_recherche': 'defaut'
    }

def obtenir_coordonnees_pour_carte_mairie(ville_mairie):
    """
    Spécialement conçu pour le dashboard des mairies
    Retourne les coordonnées optimisées pour l'affichage de carte
    
    Args:
        ville_mairie: Nom de la ville de la mairie
        
    Returns:
        dict: Coordonnées complètes pour l'affichage carte
    """
    coordonnees = obtenir_coordonnees_ville_amelioree(ville_mairie)
    
    # Ajuster le zoom en fonction du type de ville
    if coordonnees['ville_trouvee']:
        # Si c'est une petite commune, zoom plus serré
        if ville_mairie and len(ville_mairie) > 15:  # Noms longs = petites communes souvent
            coordonnees['zoom'] = max(coordonnees['zoom'], 15)
        
        # Si c'est une grande ville, zoom moins serré
        grandes_villes = ['paris', 'lyon', 'marseille', 'toulouse', 'nice', 'nantes', 'strasbourg', 'montpellier', 'bordeaux', 'lille']
        if any(gv in ville_mairie.lower() for gv in grandes_villes):
            coordonnees['zoom'] = min(coordonnees['zoom'], 12)
    
    return coordonnees

def lister_villes_disponibles():
    """
    Retourne la liste des villes disponibles dans la base de données
    
    Returns:
        list: Liste des noms de villes avec leurs coordonnées
    """
    villes = []
    for ville_key, coordonnees in VILLES_COORDONNEES.items():
        if ville_key not in ['default', 'france']:
            villes.append({
                'cle': ville_key,
                'nom': coordonnees['nom'],
                'coordonnees': {
                    'lat': coordonnees['lat'],
                    'lng': coordonnees['lng'],
                    'zoom': coordonnees.get('zoom', 14)
                }
            })
    
    return sorted(villes, key=lambda x: x['nom'])

def ajouter_ville_dynamique(nom_ville, latitude, longitude, zoom=14):
    """
    Ajoute dynamiquement une nouvelle ville à la base de données
    Utile pour les mairies de petites communes non répertoriées
    
    Args:
        nom_ville: Nom de la ville
        latitude: Latitude GPS
        longitude: Longitude GPS
        zoom: Niveau de zoom par défaut
        
    Returns:
        dict: Résultat de l'ajout
    """
    nom_normalise = normaliser_nom_ville_pour_recherche(nom_ville)
    
    if not nom_normalise:
        return {
            'success': False,
            'message': 'Nom de ville invalide'
        }
    
    if nom_normalise in VILLES_COORDONNEES:
        return {
            'success': False,
            'message': f'La ville "{nom_ville}" existe déjà dans la base de données'
        }
    
    try:
        # Valider les coordonnées
        lat = float(latitude)
        lng = float(longitude)
        zoom = int(zoom)
        
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            return {
                'success': False,
                'message': 'Coordonnées GPS invalides'
            }
        
        # Ajouter à la base de données (en mémoire)
        VILLES_COORDONNEES[nom_normalise] = {
            'lat': lat,
            'lng': lng,
            'zoom': zoom,
            'nom': nom_ville
        }
        
        return {
            'success': True,
            'message': f'Ville "{nom_ville}" ajoutée avec succès',
            'ville_normalisee': nom_normalise,
            'coordonnees': VILLES_COORDONNEES[nom_normalise]
        }
        
    except (ValueError, TypeError):
        return {
            'success': False,
            'message': 'Coordonnées ou zoom invalides'
        }
