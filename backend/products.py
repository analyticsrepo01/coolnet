"""CoolNest product catalog"""

CATEGORIES = {
    "refrigerators":    {"name": "Refrigerators",      "icon": "🧊", "specialist": "frosty",  "subcategories": ["French Door", "Side-by-Side", "4-Door", "Counter-Depth"]},
    "tvs":              {"name": "Televisions",         "icon": "📺", "specialist": "pixel",   "subcategories": ["OLED", "QLED", "Full HD"]},
    "washing_machines": {"name": "Washing Machines",    "icon": "🌀", "specialist": "frosty",  "subcategories": ["Front Load", "Top Load"]},
    "dryers":           {"name": "Dryers",              "icon": "♨️", "specialist": "breeze",  "subcategories": ["Heat Pump", "Condenser"]},
    "air_conditioners": {"name": "Air Conditioners",    "icon": "❄️", "specialist": "breeze",  "subcategories": ["Split", "Portable"]},
    "fans":             {"name": "Fans",                "icon": "💨", "specialist": "breeze",  "subcategories": ["Ceiling", "Tower", "Pedestal"]},
    "kitchen_hobs":     {"name": "Kitchen Hobs",        "icon": "🍳", "specialist": "cora",    "subcategories": ["Induction", "Gas", "Ceramic"]},
    "microwaves":       {"name": "Microwaves",          "icon": "📡", "specialist": "cora",    "subcategories": ["Solo", "Grill", "Convection"]},
    "vacuum_cleaners":  {"name": "Vacuum Cleaners",     "icon": "🤖", "specialist": "cora",    "subcategories": ["Robot", "Cordless Stick", "Canister"]},
    "dishwashers":      {"name": "Dishwashers",         "icon": "🫧", "specialist": "cora",    "subcategories": ["Freestanding", "Built-in"]},
    "small_appliances": {"name": "Small Appliances",    "icon": "☕", "specialist": "cora",    "subcategories": ["Coffee Makers", "Blenders", "Toasters"]},
}

PRODUCTS = {
    # ── Refrigerators ─────────────────────────────────────────────────────
    "CN-CFD-3006": {
        "sku": "CN-CFD-3006", "image": "products/CN-CFD-3006.jpg",
        "name": "CoolNest FrostMaster 655L Door-in-Door French Door",
        "brand": "CoolNest Platinum Series",
        "category": "refrigerators", "subcategory": "French Door",
        "price": 3199, "price_original": 3799, "discount_pct": 16,
        "rating": 4.7, "review_count": 203, "in_stock": True, "specialist_id": "frosty",
        "description": "Premium 655L French Door with InstaView Door-in-Door — knock twice to see inside without losing cold air. CraftIce maker produces slow-melting round ice. Linear Inverter Compressor runs whisper-quiet at 35 dB.",
        "specs": {"Capacity": "655L (476L fridge + 179L freezer)", "Type": "French Door with Door-in-Door", "Energy Rating": "5-Star Inverter", "Noise Level": "35 dB", "Dimensions": "178×91×73 cm", "Compressor Warranty": "10 years", "WiFi": "Yes — SmartThinQ app", "Ice Type": "CraftIce round + standard cubes"},
        "highlights": ["InstaView knock-to-see panel", "CraftIce slow-melt round ice", "6 custom temp zones", "WiFi & app controlled"],
        "emoji": "🧊", "energy_rating": 5,
    },
    "CN-CEL-2810": {
        "sku": "CN-CEL-2810", "image": "products/CN-CEL-2810.jpg",
        "name": "CoolNest ArtiCool 617L 3-Door French Door",
        "brand": "CoolNest Elite Series",
        "category": "refrigerators", "subcategory": "French Door",
        "price": 2499, "price_original": 2899, "discount_pct": 14,
        "rating": 4.6, "review_count": 318, "in_stock": True, "specialist_id": "frosty",
        "description": "617L 3-door French Door with Multi-Air Flow — 10 vents push cold air to every shelf for even cooling. Dedicated Fresh Zone keeps produce crisp up to 7 days longer.",
        "specs": {"Capacity": "617L (432L fridge + 185L freezer)", "Type": "3-Door French Door", "Energy Rating": "5-Star Inverter", "Noise Level": "36 dB", "Dimensions": "185×90×75 cm", "Compressor Warranty": "10 years", "Cooling": "Multi-Air Flow (10 vents)", "Fresh Zone": "Yes — dedicated compartment"},
        "highlights": ["Multi-vented 10-point air flow", "Fresh Zone extends produce life", "Smart Diagnosis via WiFi", "10-year compressor warranty"],
        "emoji": "🧊", "energy_rating": 5,
    },
    "CN-CBE-2900": {
        "sku": "CN-CBE-2900", "image": "products/CN-CBE-2900.jpg", "pdf_url": "pdfs/CN-CBE-2900.pdf",
        "name": "CoolNest Bespoke 648L 4-Door with Beverage Center",
        "brand": "CoolNest Bespoke Series",
        "category": "refrigerators", "subcategory": "4-Door",
        "price": 4199, "price_original": 4799, "discount_pct": 12,
        "rating": 4.8, "review_count": 156, "in_stock": True, "specialist_id": "frosty",
        "description": "Our most intelligent fridge. 648L 4-door with a 32\" AI Family Hub touch screen that manages food inventory, recipes, and grocery lists. Beverage Center with Autofill Pitcher. Mix-and-match custom panel colors.",
        "specs": {"Capacity": "648L (477L fridge + 171L freezer)", "Type": "4-Door French Door", "Energy Rating": "5-Star Inverter+", "Noise Level": "42 dB", "Dimensions": "183×91×71 cm", "Display": "32\" AI Family Hub", "Beverage Center": "Autofill pitcher + can rack", "Custom Panels": "8 color choices"},
        "highlights": ["32\" AI Family Hub smart screen", "Beverage Center with auto-fill", "Custom Bespoke panel colors", "AI-powered food inventory"],
        "emoji": "🧊", "energy_rating": 5,
    },
    "CN-CPS-2530": {
        "sku": "CN-CPS-2530", "image": "products/CN-CPS-2530.jpg",
        "name": "CoolNest FrostGuard 591L Side-by-Side",
        "brand": "CoolNest Pro Series",
        "category": "refrigerators", "subcategory": "Side-by-Side",
        "price": 1699, "price_original": 1999, "discount_pct": 15,
        "rating": 4.5, "review_count": 489, "in_stock": True, "specialist_id": "frosty",
        "description": "591L side-by-side with easy eye-level access to both fridge and freezer. FrostGuard eliminates ice build-up automatically. External ice and filtered water dispenser. Best value side-by-side for families of 4–5.",
        "specs": {"Capacity": "591L (308L fridge + 283L freezer)", "Type": "Side-by-Side", "Energy Rating": "4-Star", "Noise Level": "38 dB", "Dimensions": "177×91×71 cm", "Warranty": "5 yr compressor, 2 yr parts", "Dispenser": "External ice & filtered water", "FrostGuard": "Yes — auto defrost"},
        "highlights": ["FrostGuard no-frost technology", "External ice & water dispenser", "LED mood interior lighting", "6th Sense adaptive cooling"],
        "emoji": "🧊", "energy_rating": 4,
    },
    "CN-CPR-2500": {
        "sku": "CN-CPR-2500", "image": "products/CN-CPR-2500.jpg", "pdf_url": "pdfs/CN-CPR-2500.pdf",
        "name": "CoolNest FlexChill 580L French Door Bottom Freezer",
        "brand": "CoolNest Pro Series",
        "category": "refrigerators", "subcategory": "French Door",
        "price": 1999, "price_original": 2299, "discount_pct": 13,
        "rating": 4.5, "review_count": 267, "in_stock": True, "specialist_id": "frosty",
        "description": "580L French Door with a unique Flex Drawer that converts between fridge (2°C), wine (7°C), or soft-freeze (−3°C) at the touch of a button. All-Around Cooling sends air to every corner.",
        "specs": {"Capacity": "580L (341L fridge + 147L freezer + 92L flex drawer)", "Type": "French Door Bottom Freezer", "Energy Rating": "5-Star Inverter", "Flex Drawer": "3-mode (fridge / wine / soft-freeze)", "Noise Level": "35 dB", "Compressor Warranty": "10 years", "Cooling": "All-Around Cooling"},
        "highlights": ["Flex drawer: fridge / wine / soft-freeze", "All-Around Cooling technology", "Easy-access bottom pull-out freezer", "Triple zone temperature control"],
        "emoji": "🧊", "energy_rating": 5,
    },
    "CN-CLC-2260": {
        "sku": "CN-CLC-2260", "image": "products/CN-CLC-2260.jpg",
        "name": "CoolNest Preserva 543L Counter-Depth Side-by-Side",
        "brand": "CoolNest Classic Series",
        "category": "refrigerators", "subcategory": "Counter-Depth",
        "price": 2199, "price_original": 2699, "discount_pct": 19,
        "rating": 4.6, "review_count": 184, "in_stock": True, "specialist_id": "frosty",
        "description": "Flush counter-depth design (68cm deep) integrates seamlessly with kitchen cabinets. Preserva dual-cooling system uses separate compressors for fridge and freezer — no flavour transfer. Built-in wine rack and water dispenser.",
        "specs": {"Capacity": "543L (308L fridge + 235L freezer)", "Type": "Counter-Depth Side-by-Side", "Energy Rating": "5-Star Inverter", "Depth": "68 cm (counter-flush)", "Noise Level": "41 dB", "Cooling": "Dual Preserva system (2 compressors)", "Wine Rack": "Yes — 6 bottle", "Water Dispenser": "External filtered"},
        "highlights": ["Flush counter-depth (68 cm)", "Dual Preserva cooling — no odour mix", "Built-in 6-bottle wine rack", "External filtered water dispenser"],
        "emoji": "🧊", "energy_rating": 5,
    },
    "CN-CPF-2600": {
        "sku": "CN-CPF-2600", "image": "products/CN-CPF-2600.jpg",
        "name": "CoolNest QuickIce Pro 605L French Door Bottom Mount",
        "brand": "CoolNest Pro Series",
        "category": "refrigerators", "subcategory": "French Door",
        "price": 2099, "price_original": 2499, "discount_pct": 16,
        "rating": 4.7, "review_count": 312, "in_stock": True, "specialist_id": "frosty",
        "description": "605L French Door Bottom Mount with industry-leading QuickIce Pro ice maker producing 6 kg of ice per day. 5-in-1 convertible compartment switches between modes for ultimate flexibility. Smart WiFi with remote diagnostics.",
        "specs": {"Capacity": "605L (422L fridge + 183L freezer)", "Type": "French Door Bottom Mount", "Energy Rating": "5-Star Inverter", "Ice Production": "QuickIce Pro 6 kg/day", "Noise Level": "37 dB", "WiFi": "Yes — remote diagnostics", "Convertible Drawer": "5 modes (fridge/freeze/wine/veg/off)", "Compressor Warranty": "10 years"},
        "highlights": ["QuickIce Pro — 6 kg ice/day", "5-in-1 convertible compartment", "WiFi with smart diagnostics", "Humidity-controlled FreshBox"],
        "emoji": "🧊", "energy_rating": 5,
    },

    # ── Televisions ────────────────────────────────────────────────────────
    "CN-TV65O": {
        "sku": "CN-TV65O", "name": "CoolNest VividMax 65\" OLED 4K",
        "category": "tvs", "subcategory": "OLED",
        "price": 1499, "price_original": 1999, "discount_pct": 25,
        "rating": 4.8, "review_count": 203, "in_stock": True, "specialist_id": "pixel",
        "description": "True OLED perfection — infinite contrast, 120Hz gaming mode, Dolby Vision IQ, and a 65\" canvas that transforms any room.",
        "specs": {"Screen": "65\" OLED 4K (3840×2160)", "Refresh Rate": "120Hz", "HDR": "Dolby Vision IQ + HDR10+", "HDMI Ports": "4 (2× HDMI 2.1)", "Audio": "50W Dolby Atmos", "Smart OS": "CoolNest OS 3.0", "Warranty": "3 years"},
        "highlights": ["Self-lit OLED pixels", "Infinite contrast ratio", "120Hz HDMI 2.1 for gaming", "Dolby Vision IQ"],
        "emoji": "📺",
    },
    "CN-TV55Q": {
        "sku": "CN-TV55Q", "name": "CoolNest BrightWave 55\" QLED 4K",
        "category": "tvs", "subcategory": "QLED",
        "price": 799, "price_original": 1099, "discount_pct": 27,
        "rating": 4.6, "review_count": 567, "in_stock": True, "specialist_id": "pixel",
        "description": "Quantum dot brilliance at an accessible price. 1500 nits peak brightness makes it the best choice for bright living rooms.",
        "specs": {"Screen": "55\" QLED 4K (3840×2160)", "Refresh Rate": "120Hz", "HDR": "HDR10+", "HDMI Ports": "3 (1× HDMI 2.1)", "Audio": "40W", "Smart OS": "CoolNest OS 3.0", "Warranty": "2 years"},
        "highlights": ["Quantum dot technology", "1500-nit peak brightness", "Anti-glare coating", "Voice control built-in"],
        "emoji": "📺",
    },
    "CN-TV43F": {
        "sku": "CN-TV43F", "name": "CoolNest ClearView 43\" FHD",
        "category": "tvs", "subcategory": "Full HD",
        "price": 349, "price_original": 449, "discount_pct": 22,
        "rating": 4.2, "review_count": 1204, "in_stock": True, "specialist_id": "pixel",
        "description": "Crisp 43\" Full HD for bedrooms, kitchens, and offices. Built-in streaming apps, zero-border design, wall-mount included.",
        "specs": {"Screen": "43\" FHD (1920×1080)", "Refresh Rate": "60Hz", "HDR": "HDR10", "HDMI Ports": "2", "Audio": "20W", "Smart OS": "CoolNest OS 3.0", "Warranty": "2 years"},
        "highlights": ["Wall mount included", "Zero-border design", "Built-in Netflix & YouTube", "Great bedroom size"],
        "emoji": "📺",
    },

    # ── Washing Machines ───────────────────────────────────────────────────
    "CN-CFW-3400": {
        "sku": "CN-CFW-3400", "image": "products/CN-CFW-3400.jpg", "name": "CoolNest ColdWash Pro 9kg Front Load",
        "brand": "CoolNest Pro Series",
        "category": "washing_machines", "subcategory": "Front Load",
        "price": 1099, "price_original": 1299, "discount_pct": 15,
        "rating": 4.6, "review_count": 412, "in_stock": True, "specialist_id": "frosty",
        "description": "9kg front-loader with AI Direct Drive motor that senses fabric type and adjusts wash motion automatically. ColdWash technology cleans effectively in cold water, saving 30% energy. True Steam eliminates 99.9% of allergens.",
        "specs": {"Capacity": "9 kg", "Type": "Front Load", "Max Spin": "1300 RPM", "Energy Rating": "5-Star Inverter", "Noise": "47 dB wash / 73 dB spin", "Cycles": "14 wash programs", "Motor Warranty": "10 years", "Steam": "True Steam allergen cycle"},
        "highlights": ["AI Direct Drive motor (senses fabric)", "ColdWash saves 30% energy", "True Steam — 99.9% allergen free", "10-year motor warranty"],
        "emoji": "🌀", "energy_rating": 5,
    },
    "CN-CEL-4500": {
        "sku": "CN-CEL-4500", "image": "products/CN-CEL-4500.jpg", "pdf_url": "pdfs/CN-CEL-4500.pdf", "name": "CoolNest SilentSteam 9kg Front Load",
        "brand": "CoolNest Elite Series",
        "category": "washing_machines", "subcategory": "Front Load",
        "price": 1299, "price_original": 1499, "discount_pct": 13,
        "rating": 4.7, "review_count": 287, "in_stock": True, "specialist_id": "frosty",
        "description": "9kg front-loader with VRT Plus vibration reduction — 40% quieter than standard washers. EcoBubble technology activates detergent in cold water for powerful cleaning. SmartCare app runs 27 self-diagnostic checks.",
        "specs": {"Capacity": "9 kg", "Type": "Front Load", "Max Spin": "1400 RPM", "Energy Rating": "5-Star Inverter", "Noise": "40 dB wash / 65 dB spin", "Cycles": "16 wash programs", "Motor Warranty": "10 years", "Special Tech": "EcoBubble + VRT Plus"},
        "highlights": ["VRT Plus — 40% quieter operation", "EcoBubble cold-water activation", "SmartCare 27-point app diagnostic", "Steam Wash hygiene cycle"],
        "emoji": "🌀", "energy_rating": 5,
    },
    "CN-CTP-7000": {
        "sku": "CN-CTP-7000", "image": "products/CN-CTP-7000.jpg", "name": "CoolNest TurboDrum 8kg Top Load",
        "brand": "CoolNest Pro Series",
        "category": "washing_machines", "subcategory": "Top Load",
        "price": 799, "price_original": 999, "discount_pct": 20,
        "rating": 4.4, "review_count": 678, "in_stock": True, "specialist_id": "frosty",
        "description": "8kg top-loader with TurboDrum — the drum and pulsator spin in opposite directions for a powerful yet gentle wash. 6Motion technology uses 6 different wash movements to care for all fabric types.",
        "specs": {"Capacity": "8 kg", "Type": "Top Load", "Max Spin": "800 RPM", "Energy Rating": "5-Star Inverter", "Noise": "51 dB", "Cycles": "12 wash programs", "Motor Warranty": "10 years", "Special Tech": "TurboDrum + 6Motion"},
        "highlights": ["TurboDrum: drum + pulsator counter-spin", "6Motion wash patterns", "Tub self-cleaning program", "Smart Diagnosis wireless"],
        "emoji": "🌀", "energy_rating": 5,
    },
    "CN-CCP-5000": {
        "sku": "CN-CCP-5000", "image": "products/CN-CCP-5000.jpg", "pdf_url": "pdfs/CN-CCP-5000.pdf", "name": "CoolNest SuperSpeed 10kg Top Load",
        "brand": "CoolNest Classic Series",
        "category": "washing_machines", "subcategory": "Top Load",
        "price": 999, "price_original": 1199, "discount_pct": 17,
        "rating": 4.5, "review_count": 345, "in_stock": True, "specialist_id": "frosty",
        "description": "10kg top-loader with Super Speed — washes a full 10kg load in just 36 minutes without sacrificing cleanliness. EZ Access door tilts for easier loading. Self Clean+ sanitizes the drum with no chemicals needed.",
        "specs": {"Capacity": "10 kg", "Type": "Top Load", "Max Spin": "700 RPM", "Energy Rating": "4-Star", "Noise": "54 dB", "Cycles": "9 wash programs", "Motor Warranty": "5 years", "Super Speed": "36 min full-load wash"},
        "highlights": ["Super Speed: 10 kg in 36 minutes", "EZ Access tilt-door for easy loading", "Self Clean+ drum sanitize", "Large family capacity"],
        "emoji": "🌀", "energy_rating": 4,
    },
    "CN-CSH-5300": {
        "sku": "CN-CSH-5300", "image": "products/CN-CSH-5300.jpg", "name": "CoolNest FlexWash 11kg Top Load — Removable Agitator",
        "brand": "CoolNest Premium Series",
        "category": "washing_machines", "subcategory": "Top Load",
        "price": 1099, "price_original": 1299, "discount_pct": 15,
        "rating": 4.5, "review_count": 298, "in_stock": True, "specialist_id": "frosty",
        "description": "11kg top-loader with 2-in-1 Removable Agitator — use it for heavily soiled loads or remove it for bulky items like comforters. Load&Go XL holds 50 doses of detergent so you only fill it once a month.",
        "specs": {"Capacity": "11 kg", "Type": "Top Load", "Max Spin": "840 RPM", "Energy Rating": "5-Star", "Noise": "53 dB", "Cycles": "36 wash cycles", "Motor Warranty": "10 years", "Load&Go XL": "50-dose auto-dispenser", "Agitator": "2-in-1 removable"},
        "highlights": ["2-in-1 removable agitator (more space)", "Load&Go XL 50-dose dispenser", "36 wash cycles for all fabrics", "CleanWave ozone sanitize"],
        "emoji": "🌀", "energy_rating": 5,
    },
    "CN-CMP-6500": {
        "sku": "CN-CMP-6500", "image": "products/CN-CMP-6500.jpg", "name": "CoolNest PetCare Pro 11kg Top Load",
        "brand": "CoolNest Pro Series",
        "category": "washing_machines", "subcategory": "Top Load",
        "price": 1049, "price_original": 1249, "discount_pct": 16,
        "rating": 4.4, "review_count": 234, "in_stock": True, "specialist_id": "frosty",
        "description": "Designed for pet owners. The PetPro filter captures pet hair before it clogs your drain. AllergyPlus steam cycle eliminates dander and dust mites. Extra rinse ensures all pet hair is flushed away.",
        "specs": {"Capacity": "11 kg", "Type": "Top Load", "Max Spin": "700 RPM", "Energy Rating": "4-Star", "Noise": "55 dB", "Cycles": "12 standard + dedicated pet cycles", "PetPro Filter": "Reusable lint + pet hair trap", "Steam": "AllergyPlus steam sanitize"},
        "highlights": ["PetPro filter captures pet hair", "AllergyPlus steam sanitize", "Extra rinse for complete hair removal", "Vibration Reduction Technology"],
        "emoji": "🌀", "energy_rating": 4,
    },
    "CN-CHC-7232": {
        "sku": "CN-CHC-7232", "image": "products/CN-CHC-7232.jpg", "pdf_url": "pdfs/CN-CHC-7232.pdf", "name": "CoolNest SteamDeep 11kg Top Load",
        "brand": "CoolNest Classic Series",
        "category": "washing_machines", "subcategory": "Top Load",
        "price": 949, "price_original": 1149, "discount_pct": 17,
        "rating": 4.3, "review_count": 412, "in_stock": True, "specialist_id": "frosty",
        "description": "11kg top-loader with steam-enhanced deep cleaning and 42 wash cycles — the widest cycle selection in its class. HydroWave wash action is gentler than a traditional agitator. AutoSoak pre-treats tough stains automatically.",
        "specs": {"Capacity": "11 kg", "Type": "Top Load", "Max Spin": "700 RPM", "Energy Rating": "4-Star", "Noise": "54 dB", "Cycles": "42 wash cycles", "Motor Warranty": "5 years", "Steam": "Steam-enhanced deep clean", "AutoSoak": "Automatic pre-treatment"},
        "highlights": ["42 wash cycles — widest selection", "HydroWave gentle agitation", "AutoSoak auto stain pre-treatment", "End-of-cycle notification"],
        "emoji": "🌀", "energy_rating": 4,
    },

    # ── Dryers ─────────────────────────────────────────────────────────────
    "CN-DH7": {
        "sku": "CN-DH7", "name": "CoolNest EcoDry 7kg Heat Pump Dryer",
        "category": "dryers", "subcategory": "Heat Pump",
        "price": 799, "price_original": 999, "discount_pct": 20,
        "rating": 4.7, "review_count": 156, "in_stock": True, "specialist_id": "breeze",
        "description": "Heat-pump technology uses 50% less energy than conventional dryers. Gentle on fabrics, tough on moisture.",
        "specs": {"Capacity": "7 kg", "Type": "Heat Pump", "Energy Rating": "5-Star (A+++)", "Temperature Control": "Smart sensor dry", "Noise": "64 dB", "Warranty": "3 years"},
        "highlights": ["50% less energy vs conventional", "Gentle heat-pump drying", "Sensor auto-stop", "A+++ energy class"],
        "emoji": "♨️",
    },
    "CN-DC6": {
        "sku": "CN-DC6", "name": "CoolNest QuickDry 6kg Condenser Dryer",
        "category": "dryers", "subcategory": "Condenser",
        "price": 499, "price_original": 649, "discount_pct": 23,
        "rating": 4.3, "review_count": 289, "in_stock": True, "specialist_id": "breeze",
        "description": "No external venting needed — condenser design collects water in a tank. Perfect for apartments.",
        "specs": {"Capacity": "6 kg", "Type": "Condenser", "Energy Rating": "3-Star", "Warranty": "2 years"},
        "highlights": ["No external vent needed", "Apartment-friendly", "Water tank easy to empty", "9 drying programs"],
        "emoji": "♨️",
    },

    # ── Air Conditioners ───────────────────────────────────────────────────
    "CN-AC12": {
        "sku": "CN-AC12", "name": "CoolNest ArcticSplit 12000 BTU",
        "category": "air_conditioners", "subcategory": "Split",
        "price": 899, "price_original": 1199, "discount_pct": 25,
        "rating": 4.6, "review_count": 521, "in_stock": True, "specialist_id": "breeze",
        "description": "12000 BTU inverter split AC for rooms up to 20m². Cools to 16°C in under 8 minutes. Ultra-quiet indoor unit at 20 dB.",
        "specs": {"Cooling Power": "12000 BTU (3.5kW)", "Type": "Inverter Split", "Room Size": "Up to 20m²", "Energy Rating": "5-Star Inverter", "Noise (Indoor)": "20 dB", "WiFi Control": "Yes", "Warranty": "5 yr compressor, 2 yr parts"},
        "highlights": ["20 dB ultra-quiet", "WiFi & app control", "5-Star inverter", "Cool in 8 minutes"],
        "emoji": "❄️",
    },
    "CN-AC9P": {
        "sku": "CN-AC9P", "name": "CoolNest PortaCool 9000 BTU Portable",
        "category": "air_conditioners", "subcategory": "Portable",
        "price": 549, "price_original": 699, "discount_pct": 21,
        "rating": 4.1, "review_count": 367, "in_stock": True, "specialist_id": "breeze",
        "description": "No installation needed — just plug in, vent the exhaust hose, and enjoy cool air in minutes. Rolls between rooms.",
        "specs": {"Cooling Power": "9000 BTU (2.6kW)", "Type": "Portable", "Room Size": "Up to 14m²", "Energy Rating": "3-Star", "Noise": "52 dB", "Warranty": "2 years"},
        "highlights": ["Zero installation", "Rolls between rooms", "Dehumidifier mode", "Remote control"],
        "emoji": "❄️",
    },

    # ── Fans ───────────────────────────────────────────────────────────────
    "CN-CF52": {
        "sku": "CN-CF52", "name": "CoolNest BreezeMax 52\" Ceiling Fan",
        "category": "fans", "subcategory": "Ceiling",
        "price": 199, "price_original": 269, "discount_pct": 26,
        "rating": 4.5, "review_count": 678, "in_stock": True, "specialist_id": "breeze",
        "description": "52\" ceiling fan with DC motor, 6 speeds, reversible direction, and built-in LED lighting. WiFi-enabled.",
        "specs": {"Blade Span": "52\"", "Motor": "DC Inverter", "Speeds": "6 forward + 6 reverse", "LED Light": "24W (warm/cool switchable)", "WiFi": "Yes", "Warranty": "3 years"},
        "highlights": ["DC motor (70% less energy)", "Built-in LED light", "WiFi + app control", "Whisper-quiet"],
        "emoji": "💨",
    },
    "CN-TF42": {
        "sku": "CN-TF42", "name": "CoolNest SlimBreeze 42\" Tower Fan",
        "category": "fans", "subcategory": "Tower",
        "price": 129, "price_original": 179, "discount_pct": 28,
        "rating": 4.4, "review_count": 934, "in_stock": True, "specialist_id": "breeze",
        "description": "Slim tower fan with 70° oscillation, 8 speeds, sleep timer, and ionizer. Bladeless-safe design ideal for homes with kids.",
        "specs": {"Height": "42\"", "Oscillation": "70°", "Speeds": "8", "Ionizer": "Yes", "Timer": "0.5–8 hours", "Warranty": "2 years"},
        "highlights": ["Bladeless-safe design", "Built-in ionizer", "Sleep mode", "8-hour timer"],
        "emoji": "💨",
    },

    # ── Kitchen Hobs ───────────────────────────────────────────────────────
    "CN-IH4": {
        "sku": "CN-IH4", "name": "CoolNest InductaMaster 4-Zone Hob",
        "category": "kitchen_hobs", "subcategory": "Induction",
        "price": 449, "price_original": 599, "discount_pct": 25,
        "rating": 4.7, "review_count": 423, "in_stock": True, "specialist_id": "cora",
        "description": "4-zone induction hob with bridge function, boost mode (boils 1L water in 90s), and child lock. FlexiZone lets you combine two zones for large pots.",
        "specs": {"Zones": "4 induction + bridge function", "Boost Power": "3.7kW per zone", "Control": "Touch + slider", "Safety": "Child lock + auto shut-off", "Dimensions": "60×52 cm", "Warranty": "2 years"},
        "highlights": ["Boils 1L in 90 seconds", "FlexiZone bridge function", "Touch control", "Child lock safety"],
        "emoji": "🍳",
    },
    "CN-GH4": {
        "sku": "CN-GH4", "name": "CoolNest FlameChef 4-Burner Gas Hob",
        "category": "kitchen_hobs", "subcategory": "Gas",
        "price": 299, "price_original": 399, "discount_pct": 25,
        "rating": 4.5, "review_count": 712, "in_stock": True, "specialist_id": "cora",
        "description": "Cast-iron 4-burner gas hob with auto-ignition, wok burner (4.5kW), and tempered glass surface. Works with any cookware.",
        "specs": {"Burners": "4 (1× wok 4.5kW, 2× standard 1.75kW, 1× auxiliary 1kW)", "Surface": "Tempered glass", "Ignition": "Auto-ignition", "Compatible": "All cookware", "Warranty": "2 years"},
        "highlights": ["4.5kW power wok burner", "Auto-ignition all burners", "Easy-clean glass surface", "Works with all cookware"],
        "emoji": "🍳",
    },

    # ── Vacuum Cleaners ────────────────────────────────────────────────────
    "CN-RV1": {
        "sku": "CN-RV1", "name": "CoolNest RoboSweep Pro Robot Vacuum + Mop",
        "category": "vacuum_cleaners", "subcategory": "Robot",
        "price": 399, "price_original": 599, "discount_pct": 33,
        "rating": 4.6, "review_count": 891, "in_stock": True, "specialist_id": "cora",
        "description": "3-in-1 robot that vacuums, sweeps, and mops. LiDAR mapping, zone cleaning, and 150-min battery. Empties itself at the auto-dock.",
        "specs": {"Functions": "Vacuum + Sweep + Mop", "Navigation": "LiDAR + AI mapping", "Suction": "3000 Pa", "Battery": "150 min runtime", "Auto-dock": "Yes (auto-empty bin)", "App": "CoolNest Home app", "Warranty": "2 years"},
        "highlights": ["Vacuums + mops simultaneously", "LiDAR precision mapping", "150-min battery", "Auto-empty dock"],
        "emoji": "🤖",
    },
    "CN-SV2": {
        "sku": "CN-SV2", "name": "CoolNest FlexVac 2-in-1 Cordless Stick",
        "category": "vacuum_cleaners", "subcategory": "Cordless Stick",
        "price": 249, "price_original": 349, "discount_pct": 29,
        "rating": 4.5, "review_count": 634, "in_stock": True, "specialist_id": "cora",
        "description": "Converts from upright stick to handheld in one click. 60-min runtime, tangle-free motorhead, HEPA filtration.",
        "specs": {"Type": "2-in-1 Cordless Stick/Handheld", "Suction": "25000 Pa", "Runtime": "60 min", "Filtration": "HEPA H13", "Weight": "2.9 kg", "Warranty": "2 years"},
        "highlights": ["60-min cordless runtime", "Converts to handheld", "HEPA H13 filtration", "Tangle-free motorhead"],
        "emoji": "🤖",
    },

    # ── Dishwashers ────────────────────────────────────────────────────────
    "CN-DW13": {
        "sku": "CN-DW13", "name": "CoolNest SparkleWash 13-Place Dishwasher",
        "category": "dishwashers", "subcategory": "Freestanding",
        "price": 699, "price_original": 899, "discount_pct": 22,
        "rating": 4.5, "review_count": 312, "in_stock": True, "specialist_id": "cora",
        "description": "13-place freestanding dishwasher with 60°C sanitize wash, half-load function, and ultra-quiet 44 dB operation.",
        "specs": {"Place Settings": "13", "Energy Rating": "5-Star", "Noise": "44 dB", "Programs": "8 wash programs", "Dimensions": "85×60×60 cm", "Warranty": "2 years"},
        "highlights": ["60°C sanitize wash", "44 dB ultra-quiet", "Half-load function", "Delay start up to 24h"],
        "emoji": "🫧",
    },

    # ── Small Appliances ───────────────────────────────────────────────────
    "CN-CF1": {
        "sku": "CN-CF1", "name": "CoolNest BrewMaster Pro Coffee Maker",
        "category": "small_appliances", "subcategory": "Coffee Makers",
        "price": 129, "price_original": 179, "discount_pct": 28,
        "rating": 4.6, "review_count": 1567, "in_stock": True, "specialist_id": "cora",
        "description": "Brews a perfect 12-cup pot or a single strong espresso shot. Built-in grinder, programmable 24h timer, thermal carafe.",
        "specs": {"Capacity": "12 cups / 1.5L", "Grinder": "Built-in conical burr", "Timer": "24h programmable", "Carafe": "Thermal stainless", "Warranty": "2 years"},
        "highlights": ["Built-in burr grinder", "12-cup thermal carafe", "Programmable brew timer", "Single-serve mode"],
        "emoji": "☕",
    },
    "CN-BL3": {
        "sku": "CN-BL3", "name": "CoolNest PowerBlend 1500W Blender",
        "category": "small_appliances", "subcategory": "Blenders",
        "price": 89, "price_original": 129, "discount_pct": 31,
        "rating": 4.4, "review_count": 2341, "in_stock": True, "specialist_id": "cora",
        "description": "1500W professional blender that crushes ice, blends smoothies, and makes hot soup. Self-cleaning in 30 seconds.",
        "specs": {"Power": "1500W", "Capacity": "1.5L BPA-free jug", "Speeds": "6 speeds + pulse", "Programs": "Smoothie, Ice Crush, Hot Soup", "Warranty": "3 years"},
        "highlights": ["Crushes ice effortlessly", "Hot soup function", "30-sec self-clean", "BPA-free jug"],
        "emoji": "🥤",
    },
    "CN-MV30": {
        "sku": "CN-MV30", "name": "CoolNest QuickHeat 30L Convection Microwave",
        "category": "microwaves", "subcategory": "Convection",
        "price": 189, "price_original": 249, "discount_pct": 24,
        "rating": 4.4, "review_count": 879, "in_stock": True, "specialist_id": "cora",
        "description": "30L convection microwave that also grills and bakes. Auto-cook menus, child lock, and sensor cooking.",
        "specs": {"Capacity": "30L", "Power": "900W microwave + 1800W grill + 2300W convection", "Auto-cook": "30 preset menus", "Safety": "Child lock", "Warranty": "2 years"},
        "highlights": ["3-in-1: microwave + grill + oven", "30L family size", "Auto-cook sensor", "Child lock"],
        "emoji": "📡",
    },
}


def get_category_products(category: str, subcategory: str = None) -> list:
    """Return list of products for a category, optionally filtered by subcategory."""
    return [
        p for p in PRODUCTS.values()
        if p["category"] == category
        and (subcategory is None or p["subcategory"].lower() == subcategory.lower())
    ]


def search_products(query: str, category: str = None, max_price: float = None) -> list:
    """Simple keyword search across products."""
    query_lower = query.lower()
    results = []
    for p in PRODUCTS.values():
        if category and p["category"] != category:
            continue
        if max_price and p["price"] > max_price:
            continue
        searchable = f"{p['name']} {p['description']} {p['category']} {p['subcategory']}".lower()
        if any(word in searchable for word in query_lower.split()):
            results.append(p)
    return results
