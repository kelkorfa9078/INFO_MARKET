import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ecommerce.settings')
django.setup()

from shop.models import Category, Product

def fetch_and_save_data():
    
    url = "https://fakestoreapi.com/products/category/electronics"
    
    print("⏳ Connexion à l'API et récupération des données...")
    response = requests.get(url)
    
    if response.status_code == 200:
        products_json = response.json()
        
        
        category, created = Category.objects.get_or_create(
            name="Matériel Informatique",
            defaults={'description': "PC Portables, Écrans, Disques Durs et Composants Électroniques"}
        )
        
       
        Product.objects.filter(category=category).delete()
        print("🗑️ Anciens produits nettoyés pour la mise à jour.")

        print(f"📦 {len(products_json)} produits trouvés. Début de l'importation...")
        
     
        for prod in products_json:
            title = prod['title']
            price = float(prod['price']) * 10  
            description = prod['description']
            
            image_url = prod.get('image', '') 
            
           
            if not Product.objects.filter(title=title).exists():
                Product.objects.create(
                    category=category,
                    title=title,
                    description=f"{description} (Importé automatiquement)",
                    price=price,
                    stock=30,
                    image_url=image_url  
                )
                print(f"🟢 Produit ajouté : {title[:40]}... | 💰 {price} DH | 🖼️ Image OK")
                
        print("\n🎉 Scraping, téléchargement des images et synchronisation terminés avec succès !")
    else:
        print(f"🔴 Échec de la connexion. Code d'erreur : {response.status_code}")

if __name__ == "__main__":
    fetch_and_save_data()