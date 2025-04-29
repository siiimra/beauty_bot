import sqlite3

products = [
    # (brand, product, category, skin_type, finish, price_range, concerns, image_url, purchase_link)
    ("Fenty Beauty", "Pro Filt'r Soft Matte Longwear Foundation", "Foundation", "Oily", "Matte", "High-end", "All" , "https://www.sephora.com/productimages/sku/s1925387-main-hero.jpg", "https://www.sephora.com/product/pro-filtr-soft-matte-longwear-foundation-P87985432"),
    ("Estée Lauder", "Double Wear Stay-in-Place Foundation", "Foundation", "Oily to Combination", "Matte", "High-end", "All" ,"https://m.esteelauder.com/media/export/cms/products/640x640/el_sku_YA6F66_640x640_0.jpg", "https://www.esteelauder.com/product/643/22830/product-catalog/makeup/face/foundation/double-wear/stay-in-place-foundation"),
    ("Dior", "Forever Skin Glow Foundation", "Foundation", "Normal to Dry", "Dewy", "High-end", "All" ,"https://www.dior.com/dw/image/v2/BGXS_PRD/on/demandware.static/-/Sites-master_dior/default/dwb7132f03/Y0996398/Y0996398_C023650020_E01_GHC.jpg?sw=1850&sh=1850", "https://www.dior.com/en_us/beauty/products/dior-forever-skin-glow-Y0996398.html"),
    ("Maybelline", "Fit Me Dewy + Smooth Foundation", "Foundation", "Dry", "Dewy", "Drugstore","All" , "https://media.ulta.com/i/ulta/2225223?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/fit-me-dewy-smooth-foundation-xlsImpprod2980151?sku=2225223"),
    ("e.l.f. Cosmetics", "Halo Glow Liquid Filter", "Foundation", "Dry", "Dewy", "Drugstore", "All" ,"https://media.ulta.com/i/ulta/2604924?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/halo-glow-liquid-filter-pimprod2036949?sku=2604924"),
    ("L'Oréal Paris", "Infallible Pro-Matte Foundation", "Foundation", "Oily", "Matte", "Drugstore", "All" ,"https://media.ulta.com/i/ulta/2283483?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/infallible-pro-matte-liquid-longwear-foundation-xlsImpprod11861081?sku=2283483"),
    ("NARS", "Radiant Creamy Concealer", "Concealer", "All", "Natural", "High-end", "All" ,"https://www.sephora.com/productimages/sku/s1478379-main-hero.jpg", "https://www.sephora.com/product/radiant-creamy-concealer-P377873"),
    ("Fenty Beauty", "Pro Filt’r Instant Retouch Concealer", "Concealer", "All", "Matte", "High-end", "All" ,"https://www.sephora.com/productimages/sku/s2173367-main-zoom.jpg?imwidth=315", "https://www.sephora.com/product/pro-filt-r-instant-retouch-concealer-P88779809"),
    ("Tarte", "Shape Tape Concealer", "Concealer", "Combination to Oily", "Matte", "High-end", "All" ,"https://media.ulta.com/i/ulta/2501218?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/shape-tape-concealer-xlsImpprod14251035?sku=2501218"),
    ("Maybelline", "Instant Age Rewind Eraser Concealer", "Concealer", "All", "Natural", "Drugstore", "All" ,"https://media.ulta.com/i/ulta/2547762?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/instant-age-rewind-eraser-dark-circle-treatment-concealer-xlsImpprod3490149?sku=2547762"),
    ("L'Oréal Paris", "Infallible Full Wear Concealer", "Concealer", "All", "Full Coverage Matte", "Drugstore", "All" ,"https://media.ulta.com/i/ulta/2538176?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/infallible-full-wear-waterproof-concealer-pimprod2002563?sku=2538176"),
    ("Laura Mercier", "Translucent Loose Setting Powder", "Powder", "Combination to Oily", "Matte", "High-end", "All" ,"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRV3HSQsuI8Cq56zXjBQ3ZvBpLrFPhYR0oTZA&s", "https://www.sephora.com/product/translucent-loose-setting-powder-P109908"),
    ("Huda Beauty", "Easy Bake Loose Setting Powder", "Powder", "All", "Matte", "High-end", "All" ,"https://hudabeauty.com/dw/image/v2/BCNC_PRD/on/demandware.static/-/Sites-huda-master-catalog/default/dw4a4bd147/images/Easy_Bake_2023_Update/HB-EasyBake-6BananaBread-Packshots-2.jpg?sw=1242&sh=1242&sm=fit", "https://www.sephora.com/product/easy-bake-loose-baking-setting-powder-P433402"),
    ("Charlotte Tilbury", "Airbrush Flawless Finish Powder", "Powder", "Oily", "Matte", "High-end", "All" ,"https://www.sephora.com/productimages/sku/s2605988-main-zoom.jpg?imwidth=315", "https://www.sephora.com/product/airbrush-flawless-finish-setting-powder-P433526"),
    ("e.l.f. Cosmetics", "Halo Glow Setting Powder", "Powder", "All", "Dewy", "Drugstore", "All" ,"https://media.ulta.com/i/ulta/2574627?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/halo-glow-setting-powder-pimprod2020785?sku=2574627"),
    ("Maybelline", "Fit Me Matte + Poreless Pressed Powder", "Powder", "Oily", "Matte", "Drugstore", "All" ,"https://media.ulta.com/i/ulta/2537847?w=800&h=800&fmt=auto", "https://www.ulta.com/p/fit-me-matte-poreless-powder-xlsImpprod11851143?sku=2537847"),
    ("Fenty Beauty", "Cheeks Out Freestyle Cream Bronzer", "Bronzer", "All", "Natural", "High-end", "All" ,"https://www.sephora.com/productimages/sku/s2352862-main-zoom.jpg", "https://www.sephora.com/product/fenty-beauty-rihanna-cheeks-out-freestyle-cream-bronzer-P31870457"),
    ("Benefit Cosmetics", "Hoola Matte Bronzer", "Bronzer", "All", "Matte", "High-end", "All" ,"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQSRx4ju28flMvjj8Ub57bTsEQ-S82Rbdsa5Q&s", "https://www.ulta.com/p/hoola-matte-powder-bronzer-jumbo-pimprod2045528?sku=2624547"),
    ("Physicians Formula", "Butter Bronzer", "Bronzer", "All", "Natural", "Drugstore", "All" ,"https://media.ulta.com/i/ulta/2294340?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/butter-bronzer-murumuru-butter-bronzer-xlsImpprod13621011?sku=2294340"),
    ("Rare Beauty", "Soft Pinch Liquid Blush", "Blush", "All", "Dewy", "High-end", "All" ,"https://www.sephora.com/productimages/sku/s2362085-main-zoom.jpg?imwidth=315", "https://www.sephora.com/product/rare-beauty-by-selena-gomez-soft-pinch-liquid-blush-P97989778"),
    ("Tower 28", "BeachPlease Lip + Cheek Cream Blush", "Blush", "All", "Dewy", "High-end", "All" ,"https://www.sephora.com/productimages/sku/s2811750-main-zoom.jpg?imwidth=315", "https://www.sephora.com/product/beachplease-tinted-balm-blush-P449342"),
    ("NARS", "Powder Blush", "Blush", "All", "Natural", "High-end", "All" ,"https://media.ulta.com/i/ulta/2621271?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/blush-pimprod2044741?sku=2621271"),
    ("Milani", "Baked Blush", "Blush", "All", "Radiant", "Drugstore", "All" ,"https://www.milanicosmetics.com/cdn/shop/files/7_BakedBlush_01_PDP_OpenProduct_4_large.png?v=1729206843", "https://www.ulta.com/p/baked-blush-radiant-powder-blush-xlsImpprod17081057?sku=2519994"),
    ("NYX", "Sweet Cheeks Soft Cheek Tint", "Blush", "All", "Natural", "Drugstore", "All" ,"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSBOesVvaR2Wdaiye1IgzVXGYFinIMKL8B43g&s", "https://www.ulta.com/p/sweet-cheeks-soft-cheek-tint-blush-pimprod2016401?sku=2565838"),
    ("Becca", "Shimmering Skin Perfector Highlighter", "Highlighter", "All", "Radiant", "High-end", "All" ,"https://m.smashbox.com/media/images/products/840x840/sb_sku_C72202_840x840_0.jpg", "https://www.sephora.com/product/smashbox-smashbox-x-becca-shimmering-skin-perfector-highlighter-P477825"),
    ("Fenty Beauty", "Killawatt Freestyle Highlighter", "Highlighter", "All", "Glowy", "High-end", "All" ,"https://www.sephora.com/productimages/sku/s1925924-main-zoom.jpg?imwidth=630", "https://www.sephora.com/product/killawatt-freestyle-highlighter-P64879845?skuId=1925924"),
    ("Wet n Wild", "MegaGlo Highlighting Powder", "Highlighter", "All", "Dewy", "Drugstore", "All" ,"https://www.wetnwildbeauty.com/wp-content/uploads/sites/6/2022/10/319B.jpg", "https://www.wetnwildbeauty.com/product/megaglotm-highlighting-powder/"),
    ("Juvia’s Place", "The Zulu Eyeshadow Palette", "Eyeshadow", "All", "Bold", "Drugstore", "All" ,"https://media.ulta.com/i/ulta/2536082cm_alt01?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/zulu-palette-xlsImpprod18771137?sku=2536082"),
    ("Too Faced", "Natural Eyes Neutral Eyeshadow Palette", "Eyeshadow", "All", "Neutral", "All" ,"High-end", "https://media.ulta.com/i/ulta/2526211?w=1600&h=1600&fmt=auto", "https://www.ulta.com/p/natural-eyes-neutral-eyeshadow-palette-xlsImpprod18031045?sku=2526211"),
    ("Urban Decay", "Naked3 Eyeshadow Palette", "Eyeshadow", "All", "Neutral", "High-end", "All" ,"https://m.media-amazon.com/images/I/81Avvz-kzCL._AC_UF1000,1000_QL80_.jpg", "https://www.ulta.com/p/naked3-soft-pink-eyeshadow-palette-xlsImpprod6320257?sku=2266731"),
]

# Create database
conn = sqlite3.connect("beauty_products.db")
cursor = conn.cursor()

# Create or replace table
cursor.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    brand_name TEXT,
    product_name TEXT,
    category TEXT,
    skin_type_match TEXT,
    makeup_finish TEXT,
    price_range TEXT,
    concern_match TEXT,
    image_url TEXT,
    purchase_link TEXT
)
''')

# Clear old data before readding
cursor.execute("DELETE FROM products")

# Insert product data
cursor.executemany('''
INSERT INTO products (
    brand_name, product_name, category,
    skin_type_match, makeup_finish, price_range,
    concern_match, image_url, purchase_link
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', products)

conn.commit()
conn.close()

print("Database created")
