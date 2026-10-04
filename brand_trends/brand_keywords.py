"""
Lookvest | Brand Virality Keyword Universe
------------------------------------------
Brand keywords for Google Trends, TikTok Creative Center trends and Pinterest
Trends, grouped as industry -> competitor set -> brands so every brand is
tracked next to its direct rivals.

Usage:
    python brand_keywords.py            # writes CSV, JSON and Google Trends batches
    from brand_keywords import BRANDS, iter_rows
"""
import csv
import json
import re
import unicodedata
from pathlib import Path

BRANDS = {
    "Restaurants": {
        "Burgers": ["McDonald's", "Burger King", "Wendy's", "Five Guys", "Shake Shack", "In-N-Out", "Whataburger", "Culver's", "Smashburger", "Jack in the Box", "Carl's Jr", "Hardee's", "Sonic Drive-In", "Freddy's Frozen Custard", "Steak 'n Shake", "White Castle", "Checkers"],
        "Chicken": ["Chick-fil-A", "Popeyes", "KFC", "Raising Cane's", "Wingstop", "Zaxby's", "Bojangles", "Church's Chicken", "Dave's Hot Chicken", "Buffalo Wild Wings", "El Pollo Loco", "Slim Chickens", "Bonchon", "PDQ"],
        "Pizza": ["Domino's", "Pizza Hut", "Papa John's", "Little Caesars", "Marco's Pizza", "Papa Murphy's", "MOD Pizza", "Blaze Pizza", "Jet's Pizza", "Hungry Howie's", "Sbarro"],
        "Mexican & Fast Casual": ["Chipotle", "Taco Bell", "Qdoba", "Moe's Southwest Grill", "Del Taco", "Taco Bueno", "Torchy's Tacos", "Cava", "Sweetgreen", "Panera Bread", "Noodles & Company", "Panda Express", "Potbelly", "Mendocino Farms", "Tender Greens", "Just Salad", "Dig"],
        "Sandwiches & Subs": ["Subway", "Jersey Mike's", "Jimmy John's", "Firehouse Subs", "Arby's", "Wawa", "Sheetz", "Which Wich", "Jason's Deli", "McAlister's Deli", "Schlotzsky's"],
        "Coffee & Beverages": ["Starbucks", "Dunkin'", "Dutch Bros", "Tim Hortons", "Peet's Coffee", "Caribou Coffee", "Scooter's Coffee", "Biggby Coffee", "7 Brew", "Black Rifle Coffee", "Blue Bottle Coffee", "Swig", "Tropical Smoothie Cafe", "Smoothie King", "Jamba", "Kung Fu Tea", "Gong Cha", "Sharetea"],
        "Desserts & Bakery": ["Crumbl Cookies", "Insomnia Cookies", "Krispy Kreme", "Dairy Queen", "Baskin-Robbins", "Cold Stone Creamery", "Nothing Bundt Cakes", "Cinnabon", "Auntie Anne's", "Rita's Italian Ice", "Menchie's", "Sprinkles", "Duck Donuts", "Salt & Straw", "Van Leeuwen", "Jeni's Splendid Ice Creams"],
        "Casual Dining": ["Applebee's", "Chili's", "Olive Garden", "Texas Roadhouse", "Red Lobster", "Outback Steakhouse", "LongHorn Steakhouse", "TGI Fridays", "Red Robin", "Cheesecake Factory", "Cracker Barrel", "IHOP", "Denny's", "Waffle House", "First Watch", "Buffalo Wild Wings", "Hooters", "Twin Peaks", "BJ's Restaurant", "Yard House", "Dave & Buster's", "P.F. Chang's", "Benihana", "Carrabba's", "Bob Evans", "Golden Corral"],
        "Upscale Chains": ["Ruth's Chris", "Morton's", "Capital Grille", "Fogo de Chao", "STK", "Del Frisco's", "Seasons 52", "Eddie V's", "Kura Sushi", "Nobu"],
    },
    "Snacks, Food & Beverage CPG": {
        "Soda & Soft Drinks": ["Coca-Cola", "Pepsi", "Dr Pepper", "Sprite", "Mountain Dew", "Olipop", "Poppi", "Celsius", "Prime Hydration", "Liquid Death", "LaCroix", "Bubly", "Spindrift", "Zevia"],
        "Energy Drinks": ["Red Bull", "Monster Energy", "Celsius Energy", "Bang Energy", "Ghost Energy", "C4 Energy", "Alani Nu", "Reign", "Rockstar", "Prime Energy", "Lucky Energy", "3D Energy"],
        "Snacks": ["Doritos", "Takis", "Cheetos", "Lay's", "Pringles", "Goldfish", "Oreo", "Chips Ahoy", "Little Debbie", "Hostess", "SkinnyPop", "Smartfood", "Siete Foods", "Quest Chips", "Utz", "Kettle Brand", "Cape Cod Chips"],
        "Candy": ["Hershey's", "Reese's", "M&M's", "Skittles", "Sour Patch Kids", "Swedish Fish", "Trolli", "Haribo", "Kit Kat", "Snickers", "Twix", "Nerds", "Jolly Rancher", "Lindt", "Ghirardelli", "Feastables", "Hi-Chew", "Warheads", "Jelly Belly"],
        "Better-for-You & Protein": ["Quest Nutrition", "RXBAR", "KIND", "Clif Bar", "Built Bar", "Barebells", "Fairlife", "Premier Protein", "Chobani", "Oatly", "Magic Spoon", "Kodiak Cakes", "Sweet Loren's", "Bloom Nutrition", "Liquid I.V.", "AG1", "Ghost Protein"],
        "Alcohol & Spirits": ["Bud Light", "Michelob Ultra", "Coors Light", "Modelo", "Corona", "White Claw", "Truly", "High Noon", "Sun Cruiser", "Surfside", "Casamigos", "Don Julio", "Patron", "Teremana", "Tito's", "Jack Daniel's", "Crown Royal", "Fireball", "Athletic Brewing", "Cann"],
    },
    "Retailers": {
        "Big Box & Mass": ["Walmart", "Target", "Costco", "Sam's Club", "BJ's Wholesale", "Kroger", "Meijer", "Fred Meyer", "Dollar General", "Dollar Tree", "Five Below", "Family Dollar", "Big Lots", "Ollie's Bargain Outlet"],
        "Grocery": ["Trader Joe's", "Whole Foods", "Aldi", "Lidl", "Publix", "H-E-B", "Wegmans", "Sprouts", "Safeway", "Albertsons", "Erewhon", "Hy-Vee", "Food Lion", "Giant Eagle"],
        "Department Stores": ["Macy's", "Nordstrom", "Kohl's", "JCPenney", "Dillard's", "Bloomingdale's", "Saks Fifth Avenue", "Neiman Marcus", "Belk", "Nordstrom Rack", "Saks Off 5th"],
        "Off-Price": ["TJ Maxx", "Marshalls", "Ross Dress for Less", "Burlington", "HomeGoods", "Sierra", "Tuesday Morning", "Gabe's"],
        "Home & Furniture": ["IKEA", "Wayfair", "Home Depot", "Lowe's", "Bed Bath & Beyond", "Pottery Barn", "West Elm", "Crate & Barrel", "RH", "Ashley Furniture", "Article", "Joybird", "Burrow", "Living Spaces", "Rooms To Go", "At Home", "Kirkland's", "World Market", "Container Store", "Menards", "Ace Hardware"],
        "Beauty Retail": ["Sephora", "Ulta Beauty", "Sally Beauty", "Bluemercury", "Space NK"],
        "Electronics Retail": ["Best Buy", "Micro Center", "B&H Photo", "GameStop", "Newegg", "Apple Store"],
        "Sporting Goods & Outdoor": ["Dick's Sporting Goods", "Academy Sports", "REI", "Bass Pro Shops", "Cabela's", "Scheels", "Big 5", "Hibbett", "Foot Locker", "JD Sports", "Champs Sports", "Finish Line", "Fleet Feet"],
        "Crafts, Party & Specialty": ["Michaels", "Hobby Lobby", "Joann", "Party City", "Spirit Halloween", "Barnes & Noble", "Books-A-Million", "Bath & Body Works", "Yankee Candle", "Lush", "Build-A-Bear", "Claire's", "Spencer's", "Hot Topic", "BoxLunch", "Urban Outfitters"],
        "Pharmacy & Convenience": ["CVS", "Walgreens", "Rite Aid", "7-Eleven", "Buc-ee's", "QuikTrip", "Casey's", "Circle K", "Wawa"],
        "Pet": ["Chewy", "Petco", "PetSmart", "BarkBox", "The Farmer's Dog", "Ollie"],
    },
    "E-commerce & Marketplaces": {
        "Marketplaces": ["Amazon", "Temu", "Shein", "AliExpress", "eBay", "Etsy", "Walmart Marketplace", "Wish", "TikTok Shop", "Mercari", "Poshmark", "Depop", "Vinted", "ThredUp", "The RealReal", "Vestiaire Collective", "Rebag", "Whatnot", "StockX", "GOAT", "Grailed", "Fanatics", "Facebook Marketplace", "OfferUp", "Kickstarter"],
        "Ecommerce Platforms": ["Shopify", "BigCommerce", "WooCommerce", "Wix", "Squarespace", "Klarna", "Afterpay", "Affirm", "Shop Pay", "Sezzle", "Zip Pay"],
        "Delivery & Subscription": ["DoorDash", "Uber Eats", "Instacart", "Grubhub", "Gopuff", "Postmates", "HelloFresh", "Factor", "Home Chef", "Blue Apron", "Hungryroot", "Daily Harvest", "Thrive Market", "Misfits Market", "Imperfect Foods", "Walmart+", "Amazon Prime", "Target Circle 360", "Costco Same-Day"],
        "DTC Home & Sleep": ["Casper", "Purple", "Tempur-Pedic", "Saatva", "Nectar", "Tuft & Needle", "Sleep Number", "Brooklinen", "Parachute", "Bombas", "Our Place", "Caraway", "HexClad", "Made In", "Stanley", "Owala", "Hydro Flask", "YETI", "Simple Modern", "Brumate", "Solo Stove", "Ninja", "Dyson", "Shark", "iRobot Roomba", "Vitamix", "Traeger", "Blackstone Griddle", "Keurig", "Nespresso", "Breville", "KitchenAid", "Cuisinart", "Instant Pot", "Cosori", "Beautiful by Drew Barrymore"],
    },
    "Apparel & Footwear": {
        "Athletic Apparel": ["Nike", "Adidas", "Under Armour", "Lululemon", "Puma", "Reebok", "New Balance", "Alo Yoga", "Vuori", "Gymshark", "Fabletics", "Athleta", "Outdoor Voices", "Rhone", "Ten Thousand", "Set Active", "Girlfriend Collective", "Beyond Yoga", "Champion", "Fila", "Asics", "Mizuno"],
        "Running & Sneakers": ["Hoka", "On Running", "Brooks Running", "Saucony", "Asics", "Allbirds", "Vans", "Converse", "Skechers", "Salomon", "Altra", "Veja", "Golden Goose", "Axel Arigato", "Jordan Brand", "Yeezy", "Crocs", "Birkenstock", "Ugg", "Dr. Martens", "Timberland", "Steve Madden", "Sam Edelman", "Teva", "Hey Dude", "Clarks", "Keen", "Merrell"],
        "Fast Fashion & Mall": ["Zara", "H&M", "Uniqlo", "Forever 21", "Shein", "Fashion Nova", "PrettyLittleThing", "Boohoo", "ASOS", "Mango", "Princess Polly", "Edikted", "Aritzia", "Abercrombie & Fitch", "Hollister", "American Eagle", "Aerie", "Gap", "Old Navy", "Banana Republic", "J.Crew", "Madewell", "Express", "Garage", "Brandy Melville", "PacSun", "Zumiez", "Tilly's", "Cider", "Halara", "Quince", "Everlane", "Free People", "Anthropologie", "Lulus", "Revolve", "Petal & Pup", "Hello Molly", "Showpo", "Oh Polly", "Meshki", "White Fox Boutique"],
        "Denim & Basics": ["Levi's", "Wrangler", "Lee Jeans", "AG Jeans", "Agolde", "Citizens of Humanity", "Mother Denim", "Re/Done", "True Religion", "Hanes", "Fruit of the Loom", "Comfort Colors", "Pact", "Cuyana", "Mack Weldon", "Buck Mason", "Jenni Kayne"],
        "Shapewear & Intimates": ["Skims", "Spanx", "Victoria's Secret", "Savage X Fenty", "Parade", "Honeylove", "Knix", "Thirdlove", "CUUP", "Lively", "Calvin Klein Underwear", "Shapermint", "Yitty", "Pair of Thieves", "Tommy John", "MeUndies"],
        "Outdoor & Workwear": ["The North Face", "Patagonia", "Columbia", "Arc'teryx", "Canada Goose", "Moncler", "Carhartt", "Dickies", "Duluth Trading", "L.L.Bean", "Eddie Bauer", "Marmot", "Cotopaxi", "Kuhl", "Fjallraven", "Helly Hansen", "Mountain Hardwear", "Stio", "Filson", "Wolverine"],
        "Streetwear": ["Supreme", "Stussy", "Palace", "Kith", "Essentials Fear of God", "Corteiz", "Sp5der", "Hellstar", "Broken Planet", "Trapstar", "Denim Tears", "Aime Leon Dore", "Bape", "Off-White", "Rhude", "Gallery Dept", "Eric Emanuel", "Chrome Hearts", "Represent", "Pleasures", "Madhappy", "Cole Buxton", "Carsicko", "Minus Two", "Godspeed"],
        "Kids & Baby Apparel": ["Carter's", "OshKosh", "Children's Place", "Gap Kids", "Janie and Jack", "Hanna Andersson", "Primary", "Kyte Baby", "Little Sleepies", "Posh Peanut", "Bamboo Babies", "Burt's Bees Baby", "Mini Boden"],
    },
    "Luxury & Fashion Houses": {
        "Luxury Houses": ["Louis Vuitton", "Gucci", "Chanel", "Hermes", "Prada", "Dior", "Balenciaga", "Saint Laurent", "Fendi", "Bottega Veneta", "Burberry", "Loewe", "Celine", "Givenchy", "Valentino", "Versace", "Miu Miu", "Alaia", "The Row", "Jacquemus", "Khaite", "Jil Sander", "Maison Margiela", "Rick Owens", "Alexander McQueen", "Tom Ford", "Dolce & Gabbana", "Moschino", "Ferragamo", "Chloe", "Marni", "Acne Studios", "Ganni", "Toteme"],
        "Contemporary & Accessible Luxury": ["Coach", "Kate Spade", "Michael Kors", "Tory Burch", "Marc Jacobs", "Ralph Lauren", "Tommy Hilfiger", "Calvin Klein", "Polo Ralph Lauren", "Lacoste", "Hugo Boss", "Vince", "Reformation", "Sezane", "Rouje", "Staud", "Cult Gaia", "Mansur Gavriel", "Polene", "Longchamp", "JW Pei", "Telfar", "Brandon Blackwood", "Dagne Dover", "Senreve", "Kurt Geiger", "Rothy's", "Sarah Flint"],
        "Jewelry & Watches": ["Tiffany & Co", "Cartier", "Van Cleef & Arpels", "Bulgari", "Pandora", "Mejuri", "Kendra Scott", "David Yurman", "Alex and Ani", "Gorjana", "Ana Luisa", "Missoma", "Monica Vinader", "Brilliant Earth", "Blue Nile", "Kay Jewelers", "Zales", "Jared", "Rolex", "Omega", "Tag Heuer", "Patek Philippe", "Audemars Piguet", "Seiko", "Casio", "G-Shock", "Citizen", "Fossil", "Daniel Wellington", "Swatch", "MoonSwatch", "Tudor", "Longines", "Hamilton", "Tissot"],
        "Eyewear": ["Ray-Ban", "Oakley", "Warby Parker", "Gentle Monster", "Quay", "Sunglass Hut", "Zenni", "Costa Del Mar", "Maui Jim", "Persol", "Goodr", "Meta Ray-Ban"],
    },
    "Beauty, Fragrance & Personal Care": {
        "Fragrance (Designer & Niche)": ["Dior Sauvage", "Chanel No 5", "Bleu de Chanel", "YSL Libre", "Baccarat Rouge 540", "Maison Francis Kurkdjian", "Le Labo", "Byredo", "Jo Malone", "Tom Ford Beauty", "Creed", "Parfums de Marly", "Kilian", "Diptyque", "Glossier You", "Phlur", "Sol de Janeiro", "Ellis Brooklyn", "Kayali", "Juliette Has A Gun", "Viktor & Rolf", "Lancome La Vie Est Belle", "Carolina Herrera Good Girl", "Prada Paradoxe", "Valentino Born in Roma", "Gucci Flora", "Burberry Goddess", "Armani Acqua di Gio", "Versace Eros", "Paco Rabanne", "Rabanne 1 Million", "Jean Paul Gaultier Le Male", "Ariana Grande Perfume", "Billie Eilish Eilish", "Lattafa", "Armaf", "Afnan", "Rasasi", "Dossier", "Alt Fragrances", "Henry Rose", "Snif", "Bath & Body Works Fragrance", "Victoria's Secret Bombshell", "Dedcool", "Commodity", "Maison Margiela Replica", "Essential Parfums", "Mancera", "Montale", "Xerjoff", "Initio", "Amouage", "Nishane", "Memo Paris", "Frederic Malle", "Penhaligon's", "Acqua di Parma", "Hermes Fragrance", "Goldfield & Banks", "Arabiyat"],
        "Makeup": ["Rare Beauty", "Fenty Beauty", "Charlotte Tilbury", "Huda Beauty", "Glossier", "Rhode", "Kylie Cosmetics", "e.l.f.", "Maybelline", "L'Oreal Paris", "NYX", "Too Faced", "Urban Decay", "Benefit Cosmetics", "MAC Cosmetics", "Nars", "Makeup by Mario", "Patrick Ta", "Hourglass", "Ilia Beauty", "Saie", "Merit Beauty", "Tower 28", "Kosas", "Milk Makeup", "Haus Labs", "Danessa Myricks", "One/Size", "Anastasia Beverly Hills", "Morphe", "Colourpop", "Wet n Wild", "Revlon", "CoverGirl", "Essence Cosmetics", "Physicians Formula", "Laura Mercier", "Armani Beauty", "Dior Beauty", "YSL Beauty", "Chanel Beauty", "Summer Fridays", "Lancome", "Estee Lauder", "Clinique", "Bobbi Brown", "Smashbox", "Tarte", "IT Cosmetics", "Valentino Beauty", "Prada Beauty", "Westman Atelier", "Victoria Beckham Beauty", "Dibs Beauty", "Kaja", "Romand", "Peripera", "Hince"],
        "Skincare": ["CeraVe", "La Roche-Posay", "The Ordinary", "Drunk Elephant", "Paula's Choice", "Glow Recipe", "Sunday Riley", "Tatcha", "Augustinus Bader", "Skinceuticals", "Olay", "Neutrogena", "Cetaphil", "Eucerin", "Aveeno", "First Aid Beauty", "Bubble Skincare", "Starface", "Hero Cosmetics", "Peace Out", "Supergoop", "Kiehl's", "Clarins", "Shiseido", "Laneige", "COSRX", "Beauty of Joseon", "Anua", "Medicube", "Skin1004", "Round Lab", "Torriden", "Biodance", "Numbuzin", "Innisfree", "Sulwhasoo", "Dr. Jart+", "Byoma", "Naturium", "The Inkey List", "Good Molecules", "Topicals", "Youth to the People", "Krave Beauty", "Dieux", "Medik8", "Dr. Dennis Gross", "Murad", "Peter Thomas Roth", "Tula", "Fresh", "La Mer", "Estee Lauder Advanced Night Repair", "Clinique Moisture Surge", "Kopari", "Necessaire", "Bioderma", "Vanicream", "Aquaphor", "Vaseline", "Curology", "Hims", "Hers", "Ro", "Agency", "Musely"],
        "Hair Care & Tools": ["Olaplex", "K18", "Moroccanoil", "Ouai", "Briogeo", "Amika", "Kerastase", "Redken", "Living Proof", "Prose", "Function of Beauty", "Gisou", "Mielle", "Pattern Beauty", "Bread Beauty", "Color Wow", "Dae", "Kristin Ess", "Verb", "Davines", "Aveda", "Pureology", "Dyson Airwrap", "Shark FlexStyle", "Revlon One-Step", "T3", "GHD", "Chi", "Bio Ionic", "Coco & Eve", "Not Your Mother's", "Dove", "Head & Shoulders", "Pantene", "Tresemme", "Herbal Essences", "Nutrafol", "Vegamour"],
        "Body, Bath & Grooming": ["Sol de Janeiro Bum Bum", "Tree Hut", "Dove Body Wash", "Native Deodorant", "Old Spice", "Dr. Squatch", "Harry's", "Dollar Shave Club", "Gillette", "Billie", "Manscaped", "Philips Norelco", "Braun", "Every Man Jack", "Duke Cannon", "Lume", "Salt & Stone", "Megababe", "Touchland", "Bath & Body Works", "Lush Cosmetics", "Eos", "Quip", "Hismile", "Crest Whitestrips", "Burst Oral Care", "Waterpik", "Oral-B", "Sonicare", "Lumineux", "Moon Oral Care"],
        "Nails & Lashes": ["OPI", "Essie", "Olive & June", "Dazzle Dry", "Kiara Sky", "Glamnetic", "Static Nails", "Kiss Nails", "imPRESS Nails", "Lashify", "Lilly Lashes", "Ardell", "Lash Boost", "Grande Lash", "RevitaLash", "Sally Hansen", "DND Gel", "Gelish", "Aprés Nail"],
    },
    "Toys, Kids & Collectibles": {
        "Toy Makers": ["LEGO", "Mattel", "Hasbro", "Barbie", "Hot Wheels", "Fisher-Price", "Nerf", "Play-Doh", "Melissa & Doug", "VTech", "LeapFrog", "Spin Master", "Paw Patrol", "Magna-Tiles", "Picasso Tiles", "Bluey Toys", "MGA Entertainment", "L.O.L. Surprise", "Bratz", "Rainbow High", "Little Tikes", "Step2", "Radio Flyer", "Yoto Player", "Tonies", "Lovevery", "Crayola", "Squishmallows", "Jellycat", "Funko Pop", "Pop Mart", "Labubu", "Sonny Angel", "Smiski", "Hatchimals", "Zuru", "Bunch O Balloons", "Gabby's Dollhouse", "Disney Princess Toys", "Monster High", "Polly Pocket", "American Girl", "Our Generation", "Calico Critters", "Playmobil", "Mega Bloks", "K'NEX", "Hape", "Kidkraft", "Power Wheels", "Peppa Pig Toys", "Cocomelon Toys", "Beyblade", "Tamagotchi", "Furby", "Shashibo", "Needoh", "Stanley Kids", "Bitzee", "Ty Beanie Babies"],
        "Trading Cards & Collectibles": ["Pokemon Cards", "Pokemon TCG", "Magic The Gathering", "Yu-Gi-Oh", "Topps", "Panini", "Upper Deck", "One Piece Card Game", "Disney Lorcana", "Funko", "Hirono", "Skullpanda", "Crybaby", "Mofusand", "Sanrio", "Hello Kitty", "Kuromi", "Pochacco", "Tokidoki", "Kidrobot", "Bearbrick", "Fanatics Collectibles", "Sorcery TCG", "Star Wars Unlimited", "Flesh and Blood TCG"],
        "Baby Gear": ["UPPAbaby", "Doona", "Nuna", "Bugaboo", "Graco", "Chicco", "Evenflo", "Britax", "Baby Brezza", "Owlet", "Nanit", "Hatch Baby", "Snoo", "Frida Baby", "Elvie", "Willow Pump", "Spectra", "Momcozy", "Lalo", "Tushbaby", "Ergobaby", "Solly Baby", "Babybjorn", "Coterie Diapers", "Huggies", "Pampers", "Hello Bello", "Kudos Diapers"],
    },
    "Consumer Electronics": {
        "Smartphones": ["iPhone", "Samsung Galaxy", "Google Pixel", "OnePlus", "Motorola", "Nothing Phone", "Xiaomi", "Galaxy Z Fold", "Galaxy Z Flip", "Motorola Razr", "Sony Xperia", "Huawei", "Oppo", "Vivo", "Honor", "Realme", "Asus ROG Phone", "Fairphone", "TCL", "Light Phone", "Punkt", "Wisephone"],
        "Wireless Carriers": ["Verizon", "AT&T", "T-Mobile", "Mint Mobile", "Visible", "Cricket Wireless", "Metro by T-Mobile", "Boost Mobile", "US Mobile", "Google Fi", "Xfinity Mobile", "Spectrum Mobile", "Straight Talk", "Tello", "Total Wireless"],
        "Wearables & Audio": ["Apple Watch", "AirPods", "AirPods Pro", "Galaxy Watch", "Pixel Watch", "Fitbit", "Garmin", "Whoop", "Oura Ring", "Ultrahuman Ring", "Samsung Galaxy Ring", "Bose", "Sony WH-1000XM", "Beats", "Jabra", "Sennheiser", "JBL", "Skullcandy", "Shokz", "Nothing Ear", "Soundcore", "Sonos", "Marshall", "Bang & Olufsen", "Meta Quest", "Apple Vision Pro", "Meta Ray-Ban Display", "Xreal", "Viture", "Rabbit R1", "Humane AI Pin", "Plaud", "Friend Pendant", "Even Realities"],
        "Laptops & Tablets": ["MacBook", "MacBook Air", "MacBook Pro", "iPad", "iPad Pro", "Dell XPS", "Dell Alienware", "HP Spectre", "HP Omen", "Lenovo ThinkPad", "Lenovo Legion", "Lenovo Yoga", "Asus ROG", "Asus Zenbook", "Acer Predator", "Microsoft Surface", "Razer Blade", "MSI Laptop", "Framework Laptop", "Galaxy Tab", "Galaxy Book", "Chromebook", "Kindle", "Kindle Scribe", "reMarkable", "Boox", "Kobo", "Copilot+ PC", "Snapdragon X Elite"],
        "Smart Home & TV": ["Amazon Echo", "Alexa+", "Google Nest", "Ring", "Arlo", "Wyze", "SimpliSafe", "ADT", "Eufy", "Blink", "Philips Hue", "Govee", "Nanoleaf", "Ecobee", "August Lock", "Yale Lock", "Roku", "Fire TV", "Apple TV", "Chromecast", "Samsung TV", "LG OLED", "Sony Bravia", "TCL TV", "Hisense", "Vizio", "Samsung Frame TV", "Roborock", "Ecovacs", "Dreame", "Eufy Robot Vacuum", "Tineco", "Bissell", "Meross", "SwitchBot", "Aqara"],
        "Cameras & Drones": ["GoPro", "DJI", "DJI Osmo Pocket", "Insta360", "Canon", "Nikon", "Sony Alpha", "Fujifilm", "Fujifilm X100", "Leica", "Ricoh GR", "Kodak", "Polaroid", "Instax", "Panasonic Lumix", "Skydio", "Snap Pixy", "Kodak Charmera", "Camp Snap"],
    },
    "PC Hardware & Gaming Hardware": {
        "Chips & GPUs": ["Nvidia", "AMD", "Intel", "Qualcomm Snapdragon", "Apple Silicon", "RTX 5090", "RTX 5080", "RTX 5070", "Radeon RX 9070", "Intel Arc", "Ryzen 9", "Ryzen 7 9800X3D", "Core Ultra", "Nvidia DGX Spark", "Arm", "MediaTek", "Cerebras", "Groq", "SambaNova", "Tenstorrent"],
        "Components & Boards": ["Asus", "MSI", "Gigabyte", "ASRock", "EVGA", "Zotac", "PNY", "Sapphire", "PowerColor", "XFX", "Corsair", "NZXT", "Lian Li", "Fractal Design", "Cooler Master", "be quiet!", "Noctua", "Thermaltake", "Phanteks", "Hyte", "Deepcool", "Arctic", "Seasonic", "EKWB", "Samsung SSD", "WD Black", "Crucial", "Kingston", "Seagate", "Sabrent", "SK Hynix", "G.Skill", "TeamGroup", "Lexar", "Synology", "QNAP", "Ugreen NAS", "Raspberry Pi", "Arduino", "Minisforum", "Beelink", "GMKtec"],
        "Peripherals": ["Logitech", "Logitech G", "Razer", "SteelSeries", "HyperX", "Turtle Beach", "Elgato", "Keychron", "Wooting", "Glorious", "Ducky", "Nuphy", "Finalmouse", "Pulsar", "Lamzu", "Zowie", "Secretlab", "Branch Furniture", "Autonomous Desk", "Flexispot", "Uplift Desk", "Samsung Odyssey", "LG UltraGear", "Alienware Monitor", "Asus ROG Swift", "BenQ Zowie", "Dell UltraSharp", "Apple Studio Display", "Anker", "Belkin", "Ugreen", "Baseus", "CalDigit", "OWC", "Satechi", "Twelve South", "Nomad", "Peak Design", "Mous", "Otterbox", "Casetify", "Dbrand", "Spigen", "Zagg", "Pitaka", "Burga", "Sonix", "Wildflower Cases", "Loopy Cases", "Popsockets"],
        "Consoles & Handhelds": ["PlayStation 5", "PS5 Pro", "Xbox Series X", "Xbox Game Pass", "Nintendo Switch 2", "Nintendo Switch", "Steam Deck", "Valve Steam Machine", "Steam Frame", "Asus ROG Ally", "ROG Xbox Ally", "Lenovo Legion Go", "MSI Claw", "Ayaneo", "Anbernic", "Retroid Pocket", "Analogue Pocket", "Playdate", "Meta Quest 3", "PlayStation Portal", "PlayStation VR2", "Backbone Controller", "8BitDo", "Gamesir", "Scuf", "DualSense Edge"],
    },
    "AI Agents & AI Products": {
        "Frontier AI Assistants": ["ChatGPT", "OpenAI", "Claude", "Anthropic", "Gemini", "Google Gemini", "Microsoft Copilot", "Meta AI", "Grok", "xAI", "Perplexity", "DeepSeek", "Mistral AI", "Le Chat", "Qwen", "Kimi", "Character.AI", "Pi AI", "Poe", "Apple Intelligence", "Siri", "Alexa+", "Amazon Nova", "Llama", "Sora", "Veo", "Nano Banana", "Midjourney", "Flux AI", "Ideogram", "Leonardo AI", "Stable Diffusion", "Adobe Firefly", "Canva AI", "Runway", "Pika", "Luma AI", "Kling AI", "Hailuo AI", "Higgsfield", "HeyGen", "Synthesia", "Captions App", "CapCut", "ElevenLabs", "Suno", "Udio", "NotebookLM", "Granola", "Otter.ai", "Fireflies.ai", "Grammarly", "Jasper AI", "Copy.ai", "Notion AI", "Gamma AI", "Tome", "Beautiful.ai", "Replika", "Talkie AI", "Janitor AI", "SpicyChat", "Chai AI", "Nomi AI", "Kindroid", "Sesame AI"],
        "AI Agents & Agentic Tools": ["ChatGPT Agent", "OpenAI Operator", "OpenAI Codex", "Claude Code", "Claude Cowork", "Gemini Agent", "Project Mariner", "Jules Google", "Devin AI", "Cognition AI", "Cursor", "Windsurf", "GitHub Copilot", "Replit Agent", "Lovable", "Bolt.new", "v0", "Vercel", "Base44", "Genspark", "Manus AI", "Comet Browser", "ChatGPT Atlas", "Dia Browser", "Opera Neon", "Arc Browser", "Browser Use", "MultiOn", "Adept AI", "Lindy AI", "Relevance AI", "Zapier Agents", "n8n", "Make.com", "CrewAI", "LangChain", "LlamaIndex", "AutoGPT", "OpenClaw", "Agentforce", "Salesforce Agentforce", "Microsoft Copilot Studio", "Google Agentspace", "AWS Bedrock Agents", "Sierra AI", "Decagon", "Intercom Fin", "Harvey AI", "Hebbia", "Glean", "Writer AI", "Cohere", "Hugging Face", "Databricks Mosaic AI", "Snowflake Cortex", "Firecrawl", "Apify", "Bright Data", "Browserbase", "Exa AI", "Tavily", "Factory AI", "Augment Code", "Kiro", "Warp", "Zed", "Amp Code", "Cline", "Roo Code", "Kilo Code", "OpenCode"],
        "AI Hardware & Companions": ["Rabbit R1", "Humane AI Pin", "Limitless AI", "Plaud NotePin", "Bee Wearable", "Meta Ray-Ban Display", "io OpenAI device", "Brilliant Labs Frame", "Halliday Glasses", "Even G2", "Ray-Ban Meta Gen 2", "Oakley Meta", "Google Android XR", "Samsung Galaxy XR", "Tesla Optimus", "Figure AI", "1X Neo", "Unitree", "Boston Dynamics", "Roborock Saros", "Ropet", "Moflin", "Loona Robot", "Vector Robot", "Eilik"],
    },
    "Hotels & Travel": {
        "Hotel Chains": ["Marriott", "Hilton", "Hyatt", "IHG", "Wyndham", "Choice Hotels", "Best Western", "Accor", "Four Seasons", "Ritz-Carlton", "St. Regis", "W Hotels", "Westin", "Sheraton", "Courtyard by Marriott", "Residence Inn", "Fairfield Inn", "Hampton Inn", "Embassy Suites", "DoubleTree", "Waldorf Astoria", "Conrad", "Canopy by Hilton", "Tempo by Hilton", "Holiday Inn", "Holiday Inn Express", "Kimpton", "InterContinental", "Six Senses", "Park Hyatt", "Andaz", "Hyatt Place", "Grand Hyatt", "Thompson Hotels", "Aman", "Rosewood", "Mandarin Oriental", "Peninsula Hotels", "Edition Hotels", "Soho House", "Ace Hotel", "Virgin Hotels", "Moxy Hotels", "citizenM", "Motel 6", "La Quinta", "Red Roof Inn", "Super 8", "Days Inn", "Extended Stay America", "Graduate Hotels", "Auberge Resorts", "Montage", "1 Hotels", "Nobu Hotel", "Sonder", "Selina", "Pod Hotels", "Life House", "Kasa Living", "Mint House"],
        "Resorts & Casinos": ["MGM Grand", "Bellagio", "Caesars Palace", "Wynn Las Vegas", "Venetian", "Fontainebleau Las Vegas", "Resorts World Las Vegas", "Cosmopolitan Las Vegas", "Atlantis Bahamas", "Sandals", "Beaches Resorts", "Club Med", "Great Wolf Lodge", "Kalahari Resorts", "Disney Resorts", "Universal Orlando Hotels", "Gaylord Hotels", "Margaritaville Resort", "Excellence Resorts", "Secrets Resorts", "Hard Rock Hotel", "Mohegan Sun", "Foxwoods"],
        "Booking & Rentals": ["Airbnb", "Vrbo", "Booking.com", "Expedia", "Hotels.com", "Priceline", "Kayak", "Trivago", "Hopper", "Google Travel", "TripAdvisor", "Agoda", "Hostelworld", "Hipcamp", "Marriott Bonvoy", "Hilton Honors", "World of Hyatt", "IHG One Rewards", "Inspirato", "Evolve", "Vacasa", "Mindtrip", "Layla AI travel"],
        "Airlines": ["Delta", "United Airlines", "American Airlines", "Southwest", "JetBlue", "Alaska Airlines", "Spirit Airlines", "Frontier Airlines", "Allegiant", "Hawaiian Airlines", "Breeze Airways", "Sun Country", "Avelo", "Emirates", "Qatar Airways", "Singapore Airlines", "Air France", "British Airways", "Lufthansa", "Turkish Airlines", "Virgin Atlantic", "Icelandair", "JSX", "Blade", "Joby Aviation", "Archer Aviation", "Wheels Up"],
        "Cruises": ["Royal Caribbean", "Carnival Cruise", "Norwegian Cruise Line", "Disney Cruise Line", "Princess Cruises", "Celebrity Cruises", "MSC Cruises", "Virgin Voyages", "Viking Cruises", "Holland America", "Icon of the Seas", "Star of the Seas", "Utopia of the Seas", "Carnival Celebration", "Oceania Cruises", "Regent Seven Seas", "Silversea", "Explora Journeys", "Ritz-Carlton Yacht Collection", "Four Seasons Yachts"],
        "Rental Cars & Mobility": ["Hertz", "Enterprise", "Avis", "Budget", "National Car Rental", "Alamo", "Sixt", "Turo", "Uber", "Lyft", "Waymo", "Zoox", "Tesla Robotaxi", "Getaround", "Lime", "Bird", "Revel", "Amtrak", "Brightline", "Greyhound", "FlixBus"],
    },
    "Entertainment & Experiences": {
        "Theme Parks": ["Disney World", "Disneyland", "Universal Studios", "Epic Universe", "Universal Orlando", "Six Flags", "Cedar Point", "SeaWorld", "Busch Gardens", "Knott's Berry Farm", "Legoland", "Dollywood", "Hersheypark", "Kings Island", "Carowinds", "Silver Dollar City", "Kennywood", "Holiday World", "Great Wolf Lodge", "Kalahari Waterpark", "Volcano Bay", "Typhoon Lagoon", "Schlitterbahn", "Meow Wolf", "Museum of Ice Cream", "Color Factory", "Sphere Las Vegas", "Area15", "Universal Horror Unleashed", "Halloween Horror Nights", "Wizarding World of Harry Potter", "Super Nintendo World", "Galaxy's Edge"],
        "Family Entertainment Centers": ["Dave & Buster's", "Topgolf", "Chuck E. Cheese", "Main Event", "Round1", "Bowlero", "Lucky Strike", "Puttshack", "Drive Shack", "Flight Club", "Pinstripes", "Urban Air", "Sky Zone", "Altitude Trampoline Park", "iFly", "Andretti Indoor Karting", "K1 Speed", "Painted Pin", "Punch Bowl Social", "Pinballz", "Escape Room", "Activate Games", "Electric Shuffle", "Chicken N Pickle", "Pickleball Kingdom", "Dink Pickleball", "Big Air Trampoline", "Two Bit Circus", "Crayola Experience", "Lego Discovery Center", "Sea Life Aquarium", "Madame Tussauds", "Van Gogh Immersive", "Lighthouse Immersive", "Candytopia", "The Museum of Illusions", "Smash Room", "Axe Throwing", "Bad Axe Throwing", "Urban Axes"],
        "Cinema & Live Events": ["AMC Theatres", "Regal Cinemas", "Cinemark", "Alamo Drafthouse", "Marcus Theatres", "Harkins Theatres", "IMAX", "Dolby Cinema", "AMC Stubs A-List", "Regal Unlimited", "Fathom Events", "Ticketmaster", "Live Nation", "StubHub", "SeatGeek", "Vivid Seats", "Eventbrite", "Dice", "AXS", "Gametime", "Fever", "Candlelight Concerts", "Broadway", "Cirque du Soleil", "Disney on Ice", "WWE", "UFC", "Monster Jam", "Harlem Globetrotters", "Coachella", "Lollapalooza", "Bonnaroo", "Stagecoach", "EDC Las Vegas", "Rolling Loud", "Governors Ball", "Austin City Limits", "Outside Lands"],
        "Streaming Video": ["Netflix", "Disney+", "Hulu", "HBO Max", "Amazon Prime Video", "Apple TV+", "Paramount+", "Peacock", "YouTube TV", "Sling TV", "Fubo", "Tubi", "Pluto TV", "Roku Channel", "Crunchyroll", "ESPN+", "ESPN Unlimited", "Fox One", "DAZN", "Starz", "MGM+", "AMC+", "BritBox", "Shudder", "Philo", "Frndly TV", "Kick", "Twitch", "YouTube", "Rumble"],
        "Music & Audio Streaming": ["Spotify", "Apple Music", "YouTube Music", "Amazon Music", "Tidal", "Pandora", "SoundCloud", "Deezer", "Audible", "Libby", "Kindle Unlimited", "Pocket FM", "Everand", "SiriusXM", "iHeartRadio", "Calm", "Headspace", "Endel"],
        "Video Games & Publishers": ["Fortnite", "Roblox", "Minecraft", "Call of Duty", "GTA 6", "Grand Theft Auto", "EA Sports FC", "Madden NFL", "NBA 2K", "College Football 26", "Pokemon Legends Z-A", "Mario Kart World", "Donkey Kong Bananza", "Zelda", "Animal Crossing", "Valorant", "League of Legends", "Apex Legends", "Overwatch", "Marvel Rivals", "Battlefield 6", "Elden Ring", "Elden Ring Nightreign", "Hollow Knight Silksong", "Ghost of Yotei", "Borderlands 4", "Monster Hunter Wilds", "Clair Obscur Expedition 33", "Death Stranding 2", "Silent Hill f", "Splitgate", "Arc Raiders", "Deadlock", "Schedule I", "Peak game", "R.E.P.O.", "Steal a Brainrot", "Grow a Garden", "99 Nights in the Forest", "Dress to Impress", "Genshin Impact", "Honkai Star Rail", "Zenless Zone Zero", "Wuthering Waves", "Pokemon Go", "Monopoly Go", "Royal Match", "Candy Crush", "Clash Royale", "Brawl Stars", "Squad Busters", "Stardew Valley", "Hades 2", "Helldivers 2", "The Sims", "Project Rene", "inZOI", "Paralives", "Palworld", "Baldur's Gate 3", "Cyberpunk 2077", "The Witcher 4", "Hogwarts Legacy", "Epic Games", "Electronic Arts", "Activision Blizzard", "Ubisoft", "Take-Two", "Rockstar Games", "Nintendo", "Sony Interactive", "Xbox Game Studios", "Bandai Namco", "Square Enix", "Capcom", "Sega", "Konami", "Riot Games", "Valve", "Steam", "Epic Games Store"],
        "Fitness & Wellness Chains": ["Planet Fitness", "LA Fitness", "Crunch Fitness", "Anytime Fitness", "24 Hour Fitness", "Equinox", "Life Time Fitness", "Gold's Gym", "EoS Fitness", "Orangetheory", "F45", "Barry's", "SoulCycle", "CorePower Yoga", "Pure Barre", "Club Pilates", "Solidcore", "Hotworx", "Xponential", "Peloton", "Tonal", "Hydrow", "Zwift", "Strava", "Echelon", "Bowflex", "NordicTrack", "Rogue Fitness", "Hyrox", "CrossFit", "Ladder App", "Alo Moves", "Sculpt Society", "Restore Hyper Wellness", "Othership", "Bathhouse", "Remedy Place", "The Lodge Sauna", "Massage Envy", "Hand & Stone", "European Wax Center", "Drybar", "Glamsquad", "Function Health", "Prenuvo", "Superpower", "Eight Sleep", "Therabody", "Hyperice", "Hims Weight Loss", "Noom", "WeightWatchers", "Calibrate"],
    },
    "Automotive & Mobility": {
        "Automakers": ["Tesla", "Ford", "Chevrolet", "Toyota", "Honda", "Hyundai", "Kia", "Nissan", "Subaru", "Mazda", "Jeep", "Ram Trucks", "GMC", "Cadillac", "Lexus", "BMW", "Mercedes-Benz", "Audi", "Porsche", "Volkswagen", "Volvo", "Polestar", "Rivian", "Lucid", "Scout Motors", "Slate Auto", "BYD", "Genesis", "Acura", "Lincoln", "Dodge", "Buick", "Mini Cooper", "Land Rover", "Ferrari", "Lamborghini", "McLaren", "Bentley", "Rolls-Royce", "Aston Martin", "Cybertruck", "Model Y", "Ford Bronco", "Ford Maverick", "F-150 Lightning", "Toyota 4Runner", "Toyota Tacoma", "Honda Prelude", "Kia EV9", "Hyundai Ioniq 5", "Chevy Equinox EV", "Rivian R2", "Ferrari Luce"],
        "Auto Retail & Services": ["Carvana", "CarMax", "Vroom", "Cars.com", "Autotrader", "CarGurus", "Bring a Trailer", "Cars & Bids", "Copart", "AutoZone", "O'Reilly Auto Parts", "Advance Auto Parts", "NAPA", "Jiffy Lube", "Valvoline", "Discount Tire", "Tesla Supercharger", "ChargePoint", "Electrify America", "EVgo"],
        "Micromobility & Powersports": ["Super73", "Rad Power Bikes", "Aventon", "Lectric eBikes", "VanMoof", "Specialized", "Trek", "Cannondale", "Onewheel", "Segway", "Ninebot", "Boosted", "Sur-Ron", "Talaria", "Polaris", "Can-Am", "Harley-Davidson", "LiveWire", "Zero Motorcycles", "Yamaha", "Kawasaki", "Ducati", "KTM", "Sea-Doo", "Jetson One"],
    },
    "Financial & Consumer Apps": {
        "Fintech & Payments": ["Venmo", "Cash App", "Zelle", "PayPal", "Apple Pay", "Google Pay", "Chime", "SoFi", "Robinhood", "Webull", "Coinbase", "Kraken", "Gemini Exchange", "Binance", "Crypto.com", "Kalshi", "Polymarket", "DraftKings", "FanDuel", "PrizePicks", "Underdog Fantasy", "Fanatics Sportsbook", "BetMGM", "Caesars Sportsbook", "Bilt Rewards", "Apple Card", "Amex Platinum", "Chase Sapphire", "Capital One Venture X", "Discover", "Rocket Money", "Monarch Money", "YNAB", "Credit Karma", "NerdWallet", "Acorns", "Stash", "Wealthfront", "Betterment", "Public.com", "Moomoo", "Revolut", "Wise", "Klarna Card", "Step Card", "Greenlight", "Current", "Dave App", "Brigit", "Earnin", "MoneyLion"],
        "Social & Creator Platforms": ["TikTok", "Instagram", "Threads", "Bluesky", "X Twitter", "Snapchat", "Pinterest", "Reddit", "BeReal", "Lemon8", "Discord", "Telegram", "WhatsApp", "Facebook", "LinkedIn", "Substack", "Patreon", "OnlyFans", "Fanvue", "Linktree", "Beacons", "Stan Store", "LTK", "ShopMy", "Amazon Influencer", "Whop", "Skool", "Kajabi", "Teachable", "Gumroad", "Fanfix", "Passes", "Twitch", "Hinge", "Bumble", "Tinder", "Raya", "Feeld", "Grindr", "Duolingo", "Letterboxd", "Goodreads", "Fable App", "Partiful", "Luma Events", "Timeleft", "222 App", "Locket Widget", "Sora App"],
        "Productivity & SaaS (consumer-facing)": ["Notion", "Canva", "Figma", "Adobe Express", "Microsoft 365", "Google Workspace", "Slack", "Zoom", "Dropbox", "Todoist", "Obsidian", "Superhuman", "Raycast", "1Password", "Bitwarden", "NordVPN", "ExpressVPN", "Surfshark", "Proton", "Incogni", "DeleteMe", "Aura", "LifeLock", "Life360", "Tile", "AirTag", "Chipolo"],
    },
}

# Keyword modifiers that signal launch-driven virality when paired with a brand.
LAUNCH_MODIFIERS = [
    "new", "drop", "release date", "launch", "restock", "sold out", "review",
    "unboxing", "dupe", "viral", "tiktok", "collab", "limited edition",
    "near me", "price", "waitlist", "leak", "vs",
]


# Brands whose plain name is a common word or another entity. TikTok and Pinterest
# have no "topic" disambiguation, so these get a qualifier there. Google Trends keeps
# the plain name; select the brand's Topic (needs_topic=True) instead.
QUALIFIED = {
    # Names that read badly once "&", "+" or "/" are stripped
    "H&M": "hm clothing", "M&M's": "mms candy", "Re/Done": "redone jeans",
    "B&H Photo": "bh photo video", "AT&T": "att wireless",
    # Leaders whose name is also a place, word or other entity
    "Goldfish": "goldfish crackers", "Sprite": "sprite drink", "RH": "rh furniture",
    "Columbia": "columbia sportswear", "Patagonia": "patagonia clothing", "Hermes": "hermes bag",
    "Valentino": "valentino fashion", "K18": "k18 hair", "Mielle": "mielle hair oil", "Ouai": "ouai hair",
    "Step2": "step2 toys", "ADT": "adt security", "Sapphire": "sapphire gpu", "Corsair": "corsair pc",
    "xAI": "xai grok", "F45": "f45 training", "Kraken": "kraken crypto", "Xponential": "xponential fitness",
    "Vroom": "vroom cars", "Chewy": "chewy pets", "Kith": "kith clothing", "Hellstar": "hellstar clothing",
    "Trapstar": "trapstar clothing", "Sp5der": "sp5der hoodie", "Salomon": "salomon shoes",
    "Veja": "veja sneakers", "Harry's": "harrys razor", "IHG": "ihg hotels", "Wyndham": "wyndham hotel",
    "DoubleTree": "doubletree hotel", "Carter's": "carters baby", "Puma": "puma shoes",
    "Chili's": "chilis restaurant", "Domino's": "dominos pizza",
    # Restaurants & food
    "Dig": "dig restaurant", "Truly": "truly hard seltzer", "Corona": "corona beer",
    "Reign": "reign energy drink", "Cann": "cann drink", "Modelo": "modelo beer",
    "Celsius": "celsius drink", "KIND": "kind bar", "Ghost Energy": "ghost energy drink",
    "Wawa": "wawa store", "Sonic Drive-In": "sonic drive in", "Popeyes": "popeyes chicken",
    "Subway": "subway restaurant", "Arby's": "arbys restaurant", "Sharetea": "sharetea boba",
    "Swig": "swig drinks", "Morton's": "mortons steakhouse", "STK": "stk steakhouse",
    "Nobu": "nobu restaurant", "Hooters": "hooters restaurant", "Twin Peaks": "twin peaks restaurant",
    "Seasons 52": "seasons 52 restaurant", "Utz": "utz snacks", "Fairlife": "fairlife milk",
    "Built Bar": "built protein bar", "Bloom Nutrition": "bloom energy drink",
    # Retail & ecommerce
    "Target": "target store", "Gap": "gap clothing", "Express": "express clothing",
    "Garage": "garage clothing", "Sierra": "sierra store", "Burlington": "burlington store",
    "Michaels": "michaels craft store", "Belk": "belk store", "Sprouts": "sprouts farmers market",
    "Safeway": "safeway grocery", "Ross Dress for Less": "ross store", "Big 5": "big 5 sporting goods",
    "Scheels": "scheels store", "REI": "rei outdoor", "Ollie": "ollie dog food",
    "Wish": "wish app", "Whatnot": "whatnot app", "Article": "article furniture",
    "Burrow": "burrow furniture", "Casper": "casper mattress", "Purple": "purple mattress",
    "Nectar": "nectar mattress", "Saatva": "saatva mattress", "Ninja": "ninja kitchen",
    "Shark": "shark vacuum", "Stanley": "stanley tumbler", "Owala": "owala water bottle",
    "Our Place": "our place pan", "Made In": "made in cookware", "Factor": "factor meals",
    "Gopuff": "gopuff delivery", "Shop Pay": "shop pay", "Zip Pay": "zip pay later",
    "Joann": "joann fabrics", "At Home": "at home store", "Living Spaces": "living spaces furniture",
    "Parachute": "parachute home", "Container Store": "the container store",
    # Apparel, fashion, jewelry
    "Champion": "champion clothing", "Mango": "mango clothing", "Cider": "cider clothing",
    "Quince": "quince clothing", "Keen": "keen shoes", "Coach": "coach bag", "Vince": "vince clothing",
    "Primary": "primary kids clothes", "Lively": "lively bra", "Parade": "parade underwear",
    "Pact": "pact clothing", "Reformation": "reformation clothing", "Fossil": "fossil watch",
    "Citizen": "citizen watch", "Omega": "omega watch", "Tudor": "tudor watch",
    "Hamilton": "hamilton watch", "Swatch": "swatch watch", "Quay": "quay sunglasses",
    "Goodr": "goodr sunglasses", "Ganni": "ganni clothing", "Celine": "celine bag",
    "Loewe": "loewe bag", "Polene": "polene bag", "Represent": "represent clothing",
    "Pleasures": "pleasures clothing", "Palace": "palace skateboards", "Supreme": "supreme clothing",
    "Champs Sports": "champs sports", "On Running": "on running shoes", "Vans": "vans shoes",
    "Brooks Running": "brooks running shoes", "Altra": "altra shoes",
    "Toteme": "toteme clothing", "The Row": "the row fashion", "Khaite": "khaite fashion",
    "Staud": "staud clothing", "Knix": "knix underwear", "Agolde": "agolde jeans", "Mother Denim": "mother denim",
    # Beauty
    "Fresh": "fresh beauty", "Tula": "tula skincare", "Agency": "agency skincare",
    "Ro": "ro health", "Hers": "hers health", "Hims": "hims health", "Prose": "prose hair",
    "Verb": "verb hair", "Dae": "dae hair", "Billie": "billie razor",
    "Quip": "quip toothbrush", "Dove": "dove beauty", "Commodity": "commodity fragrance",
    "Dossier": "dossier perfume", "Snif": "snif fragrance", "Phlur": "phlur perfume",
    "Kayali": "kayali perfume", "Creed": "creed perfume", "Kilian": "kilian perfume",
    "Initio": "initio perfume", "Amouage": "amouage perfume", "Mancera": "mancera perfume",
    "Montale": "montale perfume", "Lattafa": "lattafa perfume", "Armaf": "armaf perfume",
    "Afnan": "afnan perfume", "Rasasi": "rasasi perfume", "Memo Paris": "memo paris perfume",
    "Byredo": "byredo perfume", "Le Labo": "le labo perfume", "Diptyque": "diptyque perfume",
    "Henry Rose": "henry rose perfume", "Merit Beauty": "merit beauty", "Saie": "saie beauty",
    "Kosas": "kosas makeup", "Nars": "nars makeup", "Hourglass": "hourglass makeup",
    "Benefit Cosmetics": "benefit cosmetics", "Rhode": "rhode skin", "e.l.f.": "elf cosmetics",
    "Starface": "starface pimple patch", "Bubble Skincare": "bubble skincare",
    "Topicals": "topicals skincare", "Dieux": "dieux skin", "Biodance": "biodance mask",
    "Anua": "anua skincare", "Medicube": "medicube", "Kaja": "kaja beauty", "Romand": "romand lip",
    "Hince": "hince makeup", "Peripera": "peripera lip", "Gisou": "gisou hair oil",
    "Amika": "amika hair", "Color Wow": "color wow hair", "Olaplex": "olaplex",
    "Pattern Beauty": "pattern beauty", "One/Size": "one size beauty", "Lume": "lume deodorant",
    "Touchland": "touchland hand sanitizer", "Megababe": "megababe", "Burst Oral Care": "burst toothbrush",
    "Moon Oral Care": "moon toothpaste", "Static Nails": "static nails", "Ardell": "ardell lashes",
    "Chi": "chi hair tools", "T3": "t3 hair tools", "GHD": "ghd hair",
    "Musely": "musely skincare", "Curology": "curology skincare", "Eos": "eos lotion",
    "Necessaire": "necessaire body", "Kopari": "kopari beauty", "Braun": "braun shaver",
    # Toys & baby
    "Hape": "hape toys", "Ty Beanie Babies": "beanie babies",
    "Owlet": "owlet baby monitor", "Nanit": "nanit baby monitor", "Hatch Baby": "hatch baby",
    "Snoo": "snoo bassinet", "Doona": "doona stroller", "Nuna": "nuna stroller",
    "Bugaboo": "bugaboo stroller", "Elvie": "elvie pump", "Spectra": "spectra breast pump",
    "Lalo": "lalo baby", "Coterie Diapers": "coterie diapers", "Yoto Player": "yoto player",
    "Tonies": "tonies box", "Topps": "topps cards", "Panini": "panini cards",
    "Upper Deck": "upper deck cards", "Crybaby": "crybaby pop mart", "Hirono": "hirono pop mart",
    "Skullpanda": "skullpanda pop mart", "Labubu": "labubu", "Smiski": "smiski",
    "Zuru": "zuru toys", "Needoh": "needoh", "Bitzee": "bitzee pet", "Frida Baby": "frida baby",
    # Electronics & PC
    "Ring": "ring doorbell", "Blink": "blink camera", "Arlo": "arlo camera", "Tile": "tile tracker",
    "Nothing Phone": "nothing phone", "Light Phone": "light phone", "Punkt": "punkt phone",
    "Honor": "honor phone", "Oppo": "oppo phone", "Vivo": "vivo phone", "Realme": "realme phone",
    "Visible": "visible wireless", "Cricket Wireless": "cricket wireless", "Mint Mobile": "mint mobile",
    "Whoop": "whoop band", "Garmin": "garmin watch", "Beats": "beats headphones",
    "Marshall": "marshall speaker", "Jabra": "jabra earbuds", "Shokz": "shokz headphones",
    "Sonos": "sonos speaker", "Kindle": "kindle", "Boox": "boox tablet", "Kobo": "kobo ereader",
    "Roku": "roku tv", "Hisense": "hisense tv", "Vizio": "vizio tv", "TCL": "tcl phone",
    "Govee": "govee lights", "Nanoleaf": "nanoleaf lights", "Ecobee": "ecobee thermostat",
    "Canon": "canon camera", "Nikon": "nikon camera", "Leica": "leica camera",
    "Ricoh GR": "ricoh gr camera", "Kodak": "kodak camera", "Polaroid": "polaroid camera",
    "Arm": "arm holdings", "AMD": "amd", "Intel": "intel", "Groq": "groq ai", "Cerebras": "cerebras ai",
    "Asus": "asus", "MSI": "msi", "Arctic": "arctic cooling", "Hyte": "hyte pc case",
    "Crucial": "crucial ssd", "Kingston": "kingston ssd", "Pulsar": "pulsar gaming mouse",
    "Glorious": "glorious gaming", "Ducky": "ducky keyboard", "Nuphy": "nuphy keyboard",
    "Keychron": "keychron keyboard", "Wooting": "wooting keyboard", "Nomad": "nomad goods",
    "Mous": "mous case", "Burga": "burga case", "Peak Design": "peak design",
    "Zagg": "zagg screen protector", "Pitaka": "pitaka case", "Sonix": "sonix case",
    "Belkin": "belkin charger", "Ugreen": "ugreen charger", "Baseus": "baseus charger",
    "be quiet!": "be quiet pc", "Seasonic": "seasonic psu", "Phanteks": "phanteks case",
    "Scuf": "scuf controller", "Backbone Controller": "backbone controller", "Playdate": "playdate console",
    "Ayaneo": "ayaneo handheld", "Anbernic": "anbernic handheld", "Retroid Pocket": "retroid pocket",
    "Analogue Pocket": "analogue pocket", "Raspberry Pi": "raspberry pi",
    # AI
    "Claude": "claude ai", "Anthropic": "anthropic ai", "Gemini": "gemini ai", "Grok": "grok ai",
    "Perplexity": "perplexity ai", "Mistral AI": "mistral ai", "Le Chat": "le chat mistral",
    "Qwen": "qwen ai", "Kimi": "kimi ai", "Poe": "poe ai", "Llama": "llama ai",
    "Sora": "sora ai", "Veo": "google veo", "Nano Banana": "nano banana ai",
    "Runway": "runway ai", "Pika": "pika ai", "Kling AI": "kling ai", "Higgsfield": "higgsfield ai",
    "Suno": "suno ai", "Udio": "udio ai", "Granola": "granola ai", "Cursor": "cursor ai",
    "Windsurf": "windsurf ai", "Lovable": "lovable ai", "Bolt.new": "bolt new ai", "v0": "v0 vercel",
    "Replit Agent": "replit agent", "Base44": "base44 ai", "Genspark": "genspark ai",
    "Comet Browser": "comet browser", "Dia Browser": "dia browser", "Arc Browser": "arc browser",
    "Glean": "glean ai", "Cohere": "cohere ai", "Decagon": "decagon ai",
    "Sierra AI": "sierra ai", "Warp": "warp terminal", "Zed": "zed editor", "Kiro": "kiro ai",
    "Cline": "cline ai", "Factory AI": "factory ai", "Make.com": "make com automation",
    "n8n": "n8n automation", "Tome": "tome ai", "Gamma AI": "gamma ai", "Captions App": "captions app",
    "Character.AI": "character ai", "Pi AI": "pi ai", "Replika": "replika ai", "Chai AI": "chai ai",
    "Nomi AI": "nomi ai", "Kindroid": "kindroid ai", "Talkie AI": "talkie ai",
    "Midjourney": "midjourney", "Flux AI": "flux ai", "Writer AI": "writer ai",
    "Unitree": "unitree robot", "Figure AI": "figure ai robot", "1X Neo": "1x neo robot",
    "Ropet": "ropet robot", "Moflin": "moflin robot", "Plaud": "plaud ai", "Plaud NotePin": "plaud notepin",
    "Even Realities": "even realities glasses", "Rabbit R1": "rabbit r1",
    # Travel & hotels
    "Delta": "delta airlines", "Southwest": "southwest airlines", "Frontier Airlines": "frontier airlines",
    "Spirit Airlines": "spirit airlines", "Allegiant": "allegiant air", "Breeze Airways": "breeze airways",
    "Emirates": "emirates airline", "JSX": "jsx airline", "Blade": "blade helicopter",
    "Four Seasons": "four seasons hotel", "Aman": "aman resort", "Rosewood": "rosewood hotel",
    "Montage": "montage hotel", "Conrad": "conrad hotel", "Andaz": "andaz hotel",
    "Westin": "westin hotel", "Sheraton": "sheraton hotel", "Hyatt": "hyatt hotel",
    "Hilton": "hilton hotel", "Marriott": "marriott hotel", "Accor": "accor hotels",
    "Sandals": "sandals resort", "Venetian": "venetian las vegas", "Bellagio": "bellagio las vegas",
    "Atlantis Bahamas": "atlantis bahamas", "Excellence Resorts": "excellence resorts",
    "Secrets Resorts": "secrets resorts", "Hopper": "hopper app", "Evolve": "evolve vacation rental",
    "Kayak": "kayak travel", "Sonder": "sonder hotel", "Selina": "selina hostel",
    "Edition Hotels": "edition hotel", "Graduate Hotels": "graduate hotel", "Kasa Living": "kasa hotel",
    "Mint House": "mint house hotel", "Inspirato": "inspirato travel", "Mindtrip": "mindtrip ai",
    "Enterprise": "enterprise rent a car", "National Car Rental": "national car rental",
    "Alamo": "alamo car rental", "Budget": "budget car rental", "Hertz": "hertz car rental",
    "Avis": "avis car rental", "Sixt": "sixt car rental", "Lime": "lime scooter", "Bird": "bird scooter",
    "Revel": "revel rideshare", "Brightline": "brightline train", "Zoox": "zoox robotaxi",
    "Virgin Voyages": "virgin voyages cruise", "Viking Cruises": "viking cruise",
    "Explora Journeys": "explora journeys cruise", "Silversea": "silversea cruise",
    # Entertainment & fitness
    "Kick": "kick streaming", "Starz": "starz streaming", "Philo": "philo tv",
    "Shudder": "shudder streaming", "Fubo": "fubo tv", "Tubi": "tubi tv", "Peacock": "peacock tv",
    "Calm": "calm app", "Headspace": "headspace app", "Libby": "libby app", "Everand": "everand app",
    "Endel": "endel app", "Pandora": "pandora music", "Tidal": "tidal music", "Deezer": "deezer music",
    "Dice": "dice tickets", "Fever": "fever experiences", "AXS": "axs tickets", "Gametime": "gametime tickets",
    "Broadway": "broadway show", "Sphere Las Vegas": "sphere las vegas", "Area15": "area15 las vegas",
    "Meow Wolf": "meow wolf", "Dollywood": "dollywood", "Cedar Point": "cedar point",
    "Kings Island": "kings island", "Carowinds": "carowinds", "Kennywood": "kennywood",
    "Holiday World": "holiday world", "Silver Dollar City": "silver dollar city",
    "Main Event": "main event entertainment", "Round1": "round1 arcade", "Flight Club": "flight club darts",
    "Pinstripes": "pinstripes bowling", "Urban Air": "urban air trampoline", "Sky Zone": "sky zone trampoline",
    "iFly": "ifly indoor skydiving", "Escape Room": "escape room", "Painted Pin": "painted pin bowling",
    "Activate Games": "activate games", "Electric Shuffle": "electric shuffle",
    "Steam": "steam games", "Valve": "valve games", "Zelda": "zelda game", "Sega": "sega games",
    "Deadlock": "deadlock game", "Peak game": "peak game", "Schedule I": "schedule 1 game",
    "R.E.P.O.": "repo game", "Splitgate": "splitgate game", "Arc Raiders": "arc raiders game",
    "Palworld": "palworld", "Paralives": "paralives game", "inZOI": "inzoi game",
    "Hades 2": "hades 2 game", "Overwatch": "overwatch game", "Valorant": "valorant",
    "Battlefield 6": "battlefield 6", "Monster Hunter Wilds": "monster hunter wilds",
    "Grow a Garden": "grow a garden roblox", "Steal a Brainrot": "steal a brainrot roblox",
    "99 Nights in the Forest": "99 nights in the forest roblox", "Dress to Impress": "dress to impress roblox",
    "Royal Match": "royal match game",
    "Equinox": "equinox gym", "Barry's": "barrys bootcamp", "Solidcore": "solidcore pilates",
    "Hotworx": "hotworx", "Tonal": "tonal gym", "Hydrow": "hydrow rower",
    "Echelon": "echelon bike", "Hyrox": "hyrox", "Ladder App": "ladder fitness app",
    "Othership": "othership sauna", "Bathhouse": "bathhouse spa", "Remedy Place": "remedy place",
    "Function Health": "function health", "Superpower": "superpower health", "Prenuvo": "prenuvo scan",
    "Eight Sleep": "eight sleep", "Noom": "noom diet", "Calibrate": "calibrate weight loss",
    # Auto
    "Genesis": "genesis car", "Lucid": "lucid motors", "Polestar": "polestar car", "Mini Cooper": "mini cooper",
    "Scout Motors": "scout motors", "Slate Auto": "slate truck", "Rivian": "rivian",
    "Specialized": "specialized bikes", "Trek": "trek bikes", "Cannondale": "cannondale bike",
    "Segway": "segway scooter", "Ninebot": "ninebot scooter", "Boosted": "boosted board",
    "Polaris": "polaris offroad", "Copart": "copart auction", "Discount Tire": "discount tire",
    "Ram Trucks": "ram truck", "Model Y": "tesla model y", "Cybertruck": "tesla cybertruck",
    # Fintech & apps
    "Discover": "discover card", "Current": "current banking app", "Wise": "wise money transfer",
    "Public.com": "public investing app", "Stash": "stash investing", "Step Card": "step card",
    "Dave App": "dave app", "Brigit": "brigit app", "Earnin": "earnin app", "Chime": "chime bank",
    "Gemini Exchange": "gemini crypto", "Kalshi": "kalshi", "Threads": "threads app",
    "X Twitter": "twitter", "Discord": "discord app", "Telegram": "telegram app",
    "Notion": "notion app", "Obsidian": "obsidian app", "Superhuman": "superhuman email",
    "Proton": "proton vpn", "Aura": "aura identity protection", "Raycast": "raycast app",
    "Todoist": "todoist app", "Zoom": "zoom app", "Slack": "slack app", "Skool": "skool community",
    "Whop": "whop app", "Passes": "passes creator app", "Fanfix": "fanfix app", "Beacons": "beacons ai",
    "Partiful": "partiful", "Timeleft": "timeleft app", "222 App": "222 app", "Fable App": "fable book app",
    "Hinge": "hinge app", "Bumble": "bumble app", "Raya": "raya app", "Feeld": "feeld app",
    "Locket Widget": "locket app", "Sora App": "sora app", "Life360": "life360 app",
}

# Spelling used on every platform when stripping punctuation gives the wrong word.
SEARCH_NAME = {"Dr. Jart+": "dr jart", "Re/Done": "redone", "Dunkin'": "dunkin"}

# TikTok hashtag spellings that differ from simply removing spaces.
TIKTOK_HASHTAG = {
    "M&M's": "mms", "H&M": "hm", "AT&T": "att", "X Twitter": "twitter",
}


def clean_keyword(text):
    """Lowercase, strip accents/punctuation; safe for Google, TikTok and Pinterest inputs.

    'McDonald's' -> 'mcdonalds', 'Chick-fil-A' -> 'chick fil a', 'Disney+' -> 'disney plus',
    'Bath & Body Works' -> 'bath and body works', 'AT&T' -> 'att', 'e.l.f.' -> 'elf'.
    """
    s = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    s = s.lower()
    s = re.sub(r"['’`]", "", s)                    # McDonald's -> mcdonalds
    s = re.sub(r"(?<=\w)&(?=\w)", "", s)                # AT&T -> att, H&M -> hm
    s = s.replace("&", " and ")
    s = re.sub(r"\+", " plus ", s)                      # Disney+ -> disney plus
    s = re.sub(r"[^a-z0-9]+", " ", s).strip()
    # Re-join dotted initials split into single letters: "e l f" -> "elf", "p f changs" -> "pf changs"
    s = re.sub(r"\b(?:[a-z] ){1,}[a-z]\b", lambda m: m.group(0).replace(" ", ""), s)
    return re.sub(r"\s+", " ", s)


def platform_keywords(brand):
    """Return the paste-ready keyword for each platform.

    google_trends_keyword: plain brand (select the Topic in Google Trends when needs_topic).
    pinterest_keyword:     brand + qualifier where the name alone is ambiguous.
    tiktok_hashtag:        qualified keyword with spaces removed (no '#').
    """
    plain = clean_keyword(SEARCH_NAME.get(brand, brand))
    qualified = clean_keyword(QUALIFIED.get(brand, SEARCH_NAME.get(brand, brand)))
    return {
        "google_trends_keyword": plain,
        "pinterest_keyword": qualified,
        "tiktok_hashtag": TIKTOK_HASHTAG.get(brand, qualified.replace(" ", "")),
        "needs_topic": qualified != plain,
    }


CORE_LIMIT = 1000   # max unique keywords in the core tier
CORE_MIN_PER_SET = 6


def _core_quotas(limit=CORE_LIMIT):
    """Largest per-set quota (leader-first) that keeps unique core keywords <= limit."""
    lo, hi = 0.0, 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        picked = set()
        for sets in BRANDS.values():
            for brands in sets.values():
                brands = list(dict.fromkeys(brands))
                q = min(len(brands), max(CORE_MIN_PER_SET, round(len(brands) * mid)))
                picked.update(b.lower() for b in brands[:q])
        lo, hi = (mid, hi) if len(picked) <= limit else (lo, mid)
    return lo


def iter_rows():
    """Yield one row per (brand, industry, competitor_set) with a core/extended tier.

    Lists are ordered leader-first, so the core tier keeps each set's top brands.
    """
    scale = _core_quotas()
    for industry, sets in BRANDS.items():
        for comp_set, brands in sets.items():
            brands = list(dict.fromkeys(brands))
            q = min(len(brands), max(CORE_MIN_PER_SET, round(len(brands) * scale)))
            for rank, brand in enumerate(brands, 1):
                yield {"keyword": brand, **platform_keywords(brand), "industry": industry,
                       "competitor_set": comp_set, "set_rank": rank,
                       "tier": "core" if rank <= q else "extended"}


def unique_keywords(tier=None):
    return sorted({r["keyword"] for r in iter_rows() if tier in (None, r["tier"])}, key=str.lower)


def trends_batches(anchor=None, size=5, tier="core"):
    """Chunk each competitor set into Google Trends-sized groups (max 5 terms).

    Pass an `anchor` (e.g. the set leader) to repeat it in every batch so
    relative interest scores can be stitched together across batches.
    """
    groups = {}
    for r in iter_rows():
        if tier in (None, r["tier"]):
            groups.setdefault((r["industry"], r["competitor_set"]), []).append(r["google_trends_keyword"])
    for (industry, comp_set), brands in groups.items():
        lead = anchor or brands[0]
        rest = [b for b in brands if b != lead]
        step = size - 1
        for i in range(0, len(rest), step):
            yield {"industry": industry, "competitor_set": comp_set,
                   "anchor": lead, "terms": [lead] + rest[i:i + step]}


def export(out_dir="."):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rows = list(iter_rows())
    fields = ["keyword", "google_trends_keyword", "pinterest_keyword", "tiktok_hashtag",
              "needs_topic", "industry", "competitor_set", "set_rank", "tier"]
    for name, subset in [("brand_keywords_core.csv", [r for r in rows if r["tier"] == "core"]),
                         ("brand_keywords_all.csv", rows)]:
        with open(out / name, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            w.writerows(subset)
    (out / "brand_keywords.json").write_text(json.dumps(BRANDS, indent=2, ensure_ascii=False), encoding="utf-8")
    template = Path(__file__).with_name("explorer_template.html")
    if template.exists():
        html = template.read_text(encoding="utf-8")
        html = html.replace("/*DATA*/[]", json.dumps(rows, ensure_ascii=False))
        html = html.replace("/*GEN*/", f"{len(unique_keywords('core'))} core / {len(unique_keywords())} total keywords")
        (out / "lookvest_brand_radar.html").write_text(html, encoding="utf-8")
    (out / "google_trends_batches.json").write_text(json.dumps(list(trends_batches()), indent=2, ensure_ascii=False), encoding="utf-8")
    return rows


if __name__ == "__main__":
    rows = export(Path(__file__).parent)
    print(f"Lookvest | core: {len(unique_keywords('core'))} unique keywords | "
          f"all: {len(unique_keywords())} | {sum(len(s) for s in BRANDS.values())} competitor sets "
          f"across {len(BRANDS)} industries")
