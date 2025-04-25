from flask import Flask, render_template, request, redirect, url_for
from flask import request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
from datetime import datetime
import os

app = Flask(__name__)

ORDERS_DIR = os.environ.get('ORDERS_DIR', '.')
ORDERS_FILE = os.path.join(ORDERS_DIR, 'orders.json')

# Preberite e-poštne podatke iz okolja
sender_email = os.environ.get('SENDER_EMAIL')
sender_password = os.environ.get('SENDER_PASSWORD')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/category')
def category():
    return render_template('category.html')

@app.route('/about')
def about():
    return render_template('index.html')  # Create an about.html template later

@app.route('/cart')
def cart():
    return render_template('cart.html')

@app.route('/brand/<brand_name>')
def brand_products(brand_name):
    return render_template('brand_products.html', brand=brand_name)

@app.route('/products/<brand_name>/<category>')
def products(brand_name, category):
    # Osnovni izdelki po kategorijah
    base_products = {
        'tshirts': [
            {"id": 1, "name": "Klasična majica", "price": 29.99, "type": "short"},
            {"id": 2, "name": "Polo majica", "price": 39.99, "type": "short"},
            {"id": 3, "name": "Športna majica", "price": 24.99, "type": "short"},
            {"id": 4, "name": "Elegantna majica", "price": 49.99, "type": "long"},
            {"id": 5, "name": "Casual majica", "price": 34.99, "type": "short"},
            {"id": 6, "name": "Premium majica", "price": 59.99, "type": "long"},
        ],
        'pants': [
            {"id": 7, "name": "Klasične hlače", "price": 49.99, "type": "long"},
            {"id": 8, "name": "Jeans hlače", "price": 59.99, "type": "long"},
            {"id": 9, "name": "Športne hlače", "price": 44.99, "type": "short"},
            {"id": 10, "name": "Elegantne hlače", "price": 69.99, "type": "long"},
            {"id": 11, "name": "Kratke hlače", "price": 34.99, "type": "short"},
        ],
        'jackets': [
            {"id": 12, "name": "Zimska jakna", "price": 84.99, "type": "long"},
            {"id": 13, "name": "Lahka jakna", "price": 79.99, "type": "short"},
            {"id": 14, "name": "Športna jakna", "price": 69.99, "type": "short"},
            {"id": 15, "name": "Elegantna jakna", "price": 119.99, "type": "long"},
        ],
        'accessories': [
            {"id": 16, "name": "Kapa", "price": 19.99, "type": "short"},
            {"id": 17, "name": "Šal", "price": 24.99, "type": "long"},
            {"id": 18, "name": "Pas", "price": 29.99, "type": "short"},
            {"id": 19, "name": "Rokavice", "price": 22.99, "type": "short"},
            {"id": 20, "name": "Nogavice", "price": 12.99, "type": "short"},
        ]
    }
    
    # Specifični izdelki za vsako znamko
    brand_specific_products = {
        'lacoste': {
            'tshirts': [
                {"id": 1, "name": "Lacoste Polo majica", "price": 89.99, "image": "lacoste_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Lacoste Sport majica", "price": 79.99, "image": "lacoste_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Lacoste Klasična majica", "price": 69.99, "image": "lacoste_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "Lacoste Premium majica", "price": 99.99, "image": "lacoste_tshirt4.jpg", "type": "long"},
            ],
            'pants': [
                {"id": 7, "name": "Lacoste Klasične hlače", "price": 119.99, "image": "lacoste_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Lacoste Sport hlače", "price": 99.99, "image": "lacoste_pants2.jpg", "type": "short"},
                {"id": 9, "name": "Lacoste Elegantne hlače", "price": 129.99, "image": "lacoste_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Lacoste Zimska jakna", "price": 199.99, "image": "lacoste_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Lacoste Lahka jakna", "price": 159.99, "image": "lacoste_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Lacoste Bomber jakna", "price": 179.99, "image": "lacoste_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Lacoste Kapa", "price": 49.99, "image": "lacoste_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Lacoste Šal", "price": 59.99, "image": "lacoste_acc2.jpg", "type": "long"},
                {"id": 18, "name": "Lacoste Denarnica", "price": 89.99, "image": "lacoste_acc3.jpg", "type": "short"},
            ]
        },
        'polo': {
            'tshirts': [
                {"id": 1, "name": "Ralph Lauren Polo majica", "price": 99.99, "image": "polo_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Ralph Lauren Classic majica", "price": 89.99, "image": "polo_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Ralph Lauren Slim Fit majica", "price": 109.99, "image": "polo_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "Ralph Lauren Oxford srajca", "price": 119.99, "image": "polo_tshirt4.jpg", "type": "long"},
            ],
            'pants': [
                {"id": 7, "name": "Ralph Lauren Chino hlače", "price": 129.99, "image": "polo_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Ralph Lauren Jeans", "price": 139.99, "image": "polo_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Ralph Lauren Cargo hlače", "price": 119.99, "image": "polo_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Ralph Lauren Bunda", "price": 249.99, "image": "polo_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Ralph Lauren Parka", "price": 299.99, "image": "polo_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Ralph Lauren Bomber", "price": 199.99, "image": "polo_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Ralph Lauren Klobuk", "price": 79.99, "image": "polo_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Ralph Lauren Pas", "price": 119.99, "image": "polo_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Ralph Lauren Ura", "price": 249.99, "image": "polo_acc3.jpg", "type": "short"},
            ]
        },
        'burberry': {
            'tshirts': [
                {"id": 1, "name": "Burberry Check Trim majica", "price": 299.99, "image": "burberry_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Burberry Monogram majica", "price": 349.99, "image": "burberry_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Burberry Vintage Check majica", "price": 329.99, "image": "burberry_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Burberry Check hlače", "price": 499.99, "image": "burberry_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Burberry Cotton hlače", "price": 449.99, "image": "burberry_pants2.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Burberry Trench plašč", "price": 1999.99, "image": "burberry_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Burberry Karo jakna", "price": 1499.99, "image": "burberry_jacket2.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Burberry Šal", "price": 399.99, "image": "burberry_acc1.jpg", "type": "long"},
                {"id": 17, "name": "Burberry Denarnica", "price": 449.99, "image": "burberry_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Burberry Rokavice", "price": 349.99, "image": "burberry_acc3.jpg", "type": "short"},
            ]
        },
        'dior': {
            'tshirts': [
                {"id": 1, "name": "Dior Oblique majica", "price": 699.99, "image": "dior_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Dior CD Icon majica", "price": 749.99, "image": "dior_tshirt2.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Dior Wool hlače", "price": 1199.99, "image": "dior_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Dior Jogging hlače", "price": 899.99, "image": "dior_pants2.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Dior Bomber jakna", "price": 2499.99, "image": "dior_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Dior Oblique plašč", "price": 3499.99, "image": "dior_jacket2.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Dior Klobuk", "price": 799.99, "image": "dior_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Dior Torba", "price": 1999.99, "image": "dior_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Dior Sončna očala", "price": 499.99, "image": "dior_acc3.jpg", "type": "short"},
            ]
        },
        'nike': {
            'tshirts': [
                {"id": 1, "name": "Nike Dri-FIT majica", "price": 59.99, "image": "nike_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Nike Sportswear Club majica", "price": 49.99, "image": "nike_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Nike Pro majica", "price": 69.99, "image": "nike_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "Nike Tech Fleece majica", "price": 79.99, "image": "nike_tshirt4.jpg", "type": "long"},
            ],
            'pants': [
                {"id": 7, "name": "Nike Dri-FIT hlače", "price": 89.99, "image": "nike_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Nike Tech Fleece hlače", "price": 109.99, "image": "nike_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Nike Training hlače", "price": 79.99, "image": "nike_pants3.jpg", "type": "short"},
                {"id": 10, "name": "Nike Basketball hlače", "price": 69.99, "image": "nike_pants4.jpg", "type": "short"},
            ],
            'jackets': [
                {"id": 12, "name": "Nike Windrunner jakna", "price": 129.99, "image": "nike_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Nike Tech Pack jakna", "price": 179.99, "image": "nike_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Nike Sportswear Track jakna", "price": 99.99, "image": "nike_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Nike Dual Fusion Backpack", "price": 49.99, "image": "nike_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Nike kapa", "price": 29.99, "image": "nike_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Nike Dri-FIT trak za glavo", "price": 19.99, "image": "nike_acc3.jpg", "type": "short"},
                {"id": 19, "name": "Nike Dri-FIT nogavice", "price": 14.99, "image": "nike_acc4.jpg", "type": "short"},
            ]
        },
        'balmain': {
            'tshirts': [
                {"id": 1, "name": "Balmain Logo majica", "price": 399.99, "image": "balmain_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Balmain Monogram majica", "price": 499.99, "image": "balmain_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Balmain Premium majica", "price": 599.99, "image": "balmain_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Balmain Biker hlače", "price": 999.99, "image": "balmain_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Balmain Jogging hlače", "price": 799.99, "image": "balmain_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Balmain Slim Fit hlače", "price": 899.99, "image": "balmain_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Balmain Leather jakna", "price": 2999.99, "image": "balmain_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Balmain Blazer", "price": 1999.99, "image": "balmain_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Balmain Denim jakna", "price": 1299.99, "image": "balmain_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Balmain Usnjeni pas", "price": 599.99, "image": "balmain_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Balmain Mošnjiček", "price": 699.99, "image": "balmain_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Balmain Zapestnica", "price": 499.99, "image": "balmain_acc3.jpg", "type": "short"},
            ]
        },
        'bape': {
            'tshirts': [
                {"id": 1, "name": "BAPE Camo majica", "price": 149.99, "image": "bape_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "BAPE Shark majica", "price": 169.99, "image": "bape_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "BAPE College majica", "price": 129.99, "image": "bape_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "BAPE x ADIDAS majica", "price": 199.99, "image": "bape_tshirt4.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "BAPE Camo hlače", "price": 199.99, "image": "bape_pants1.jpg", "type": "long"},
                {"id": 8, "name": "BAPE Shark hlače", "price": 229.99, "image": "bape_pants2.jpg", "type": "short"},
                {"id": 9, "name": "BAPE Denim hlače", "price": 249.99, "image": "bape_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "BAPE Shark hoodie", "price": 349.99, "image": "bape_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "BAPE Camo jakna", "price": 399.99, "image": "bape_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "BAPE Color Block jakna", "price": 449.99, "image": "bape_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "BAPE Camo kapa", "price": 99.99, "image": "bape_acc1.jpg", "type": "short"},
                {"id": 17, "name": "BAPE Shark maska", "price": 79.99, "image": "bape_acc2.jpg", "type": "short"},
                {"id": 18, "name": "BAPE Camo Tote torba", "price": 129.99, "image": "bape_acc3.jpg", "type": "short"},
                {"id": 19, "name": "BAPE Nogavice", "price": 59.99, "image": "bape_acc4.jpg", "type": "short"},
            ]
        },
        'ami': {
            'tshirts': [
                {"id": 1, "name": "AMI Paris Logo majica", "price": 139.99, "image": "ami_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "AMI de Coeur majica", "price": 149.99, "image": "ami_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "AMI Ami majica", "price": 129.99, "image": "ami_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "AMI Long Sleeve majica", "price": 179.99, "image": "ami_tshirt4.jpg", "type": "long"},
            ],
            'pants': [
                {"id": 7, "name": "AMI Carrot Fit hlače", "price": 219.99, "image": "ami_pants1.jpg", "type": "long"},
                {"id": 8, "name": "AMI Cigarette Fit hlače", "price": 239.99, "image": "ami_pants2.jpg", "type": "long"},
                {"id": 9, "name": "AMI Elastic Waist hlače", "price": 199.99, "image": "ami_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "AMI Oversize pulover", "price": 289.99, "image": "ami_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "AMI de Coeur jakna", "price": 349.99, "image": "ami_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "AMI Paris Bomber", "price": 399.99, "image": "ami_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "AMI Paris kapa", "price": 99.99, "image": "ami_acc1.jpg", "type": "short"},
                {"id": 17, "name": "AMI de Coeur Tote torba", "price": 169.99, "image": "ami_acc2.jpg", "type": "short"},
                {"id": 18, "name": "AMI Leather denarnica", "price": 199.99, "image": "ami_acc3.jpg", "type": "short"},
            ]
        },
        'jordan': {
            'tshirts': [
                {"id": 1, "name": "Jordan Jumpman majica", "price": 49.99, "image": "jordan_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Jordan 23 majica", "price": 59.99, "image": "jordan_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Jordan Air majica", "price": 69.99, "image": "jordan_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "Jordan Flight majica", "price": 79.99, "image": "jordan_tshirt4.jpg", "type": "long"},
            ],
            'pants': [
                {"id": 7, "name": "Jordan Flight hlače", "price": 89.99, "image": "jordan_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Jordan Jumpman hlače", "price": 99.99, "image": "jordan_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Jordan 23 Alpha hlače", "price": 109.99, "image": "jordan_pants3.jpg", "type": "short"},
                {"id": 10, "name": "Jordan Diamond hlače", "price": 119.99, "image": "jordan_pants4.jpg", "type": "short"},
            ],
            'jackets': [
                {"id": 12, "name": "Jordan Flight jakna", "price": 159.99, "image": "jordan_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Jordan Jumpman jakna", "price": 179.99, "image": "jordan_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Jordan 23 Engineered jakna", "price": 199.99, "image": "jordan_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Jordan Backpack", "price": 69.99, "image": "jordan_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Jordan Jumpman kapa", "price": 39.99, "image": "jordan_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Jordan zapestne trakove", "price": 19.99, "image": "jordan_acc3.jpg", "type": "short"},
                {"id": 19, "name": "Jordan Elite nogavice", "price": 24.99, "image": "jordan_acc4.jpg", "type": "short"},
            ]
        },
        'adidas': {
            'tshirts': [
                {"id": 1, "name": "Adidas Originals majica", "price": 44.99, "image": "adidas_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Adidas Trefoil majica", "price": 39.99, "image": "adidas_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Adidas Sport majica", "price": 49.99, "image": "adidas_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "Adidas Adicolor majica", "price": 54.99, "image": "adidas_tshirt4.jpg", "type": "long"},
            ],
            'pants': [
                {"id": 7, "name": "Adidas Tiro hlače", "price": 64.99, "image": "adidas_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Adidas Originals Track hlače", "price": 69.99, "image": "adidas_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Adidas Sport hlače", "price": 59.99, "image": "adidas_pants3.jpg", "type": "short"},
                {"id": 10, "name": "Adidas Essentials hlače", "price": 54.99, "image": "adidas_pants4.jpg", "type": "short"},
            ],
            'jackets': [
                {"id": 12, "name": "Adidas Originals Track jakna", "price": 89.99, "image": "adidas_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Adidas Terrex jakna", "price": 129.99, "image": "adidas_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Adidas Z.N.E. hoodie", "price": 99.99, "image": "adidas_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Adidas Classic Backpack", "price": 39.99, "image": "adidas_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Adidas kapa", "price": 24.99, "image": "adidas_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Adidas Classic nogavice", "price": 14.99, "image": "adidas_acc3.jpg", "type": "short"},
                {"id": 19, "name": "Adidas športna torba", "price": 44.99, "image": "adidas_acc4.jpg", "type": "short"},
            ]
        },
        'amiri': {
            'tshirts': [
                {"id": 1, "name": "Amiri Logo majica", "price": 349.99, "image": "amiri_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Amiri Graphic majica", "price": 399.99, "image": "amiri_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Amiri Distressed majica", "price": 429.99, "image": "amiri_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Amiri MX1 jeans", "price": 899.99, "image": "amiri_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Amiri Track hlače", "price": 799.99, "image": "amiri_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Amiri Cargo hlače", "price": 849.99, "image": "amiri_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Amiri Bone jakna", "price": 1999.99, "image": "amiri_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Amiri Distressed denim jakna", "price": 1799.99, "image": "amiri_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Amiri Varsity jakna", "price": 2499.99, "image": "amiri_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Amiri kapa", "price": 349.99, "image": "amiri_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Amiri pas", "price": 549.99, "image": "amiri_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Amiri torbica", "price": 899.99, "image": "amiri_acc3.jpg", "type": "short"},
            ]
        },
        'balenciaga': {
            'tshirts': [
                {"id": 1, "name": "Balenciaga Logo majica", "price": 549.99, "image": "balenciaga_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Balenciaga Campaign majica", "price": 599.99, "image": "balenciaga_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Balenciaga Oversize majica", "price": 649.99, "image": "balenciaga_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Balenciaga Track hlače", "price": 899.99, "image": "balenciaga_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Balenciaga Denim hlače", "price": 849.99, "image": "balenciaga_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Balenciaga Cargo hlače", "price": 949.99, "image": "balenciaga_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Balenciaga Track jakna", "price": 1999.99, "image": "balenciaga_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Balenciaga Denim jakna", "price": 1799.99, "image": "balenciaga_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Balenciaga Oversize hoodie", "price": 1299.99, "image": "balenciaga_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Balenciaga kapa", "price": 399.99, "image": "balenciaga_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Balenciaga Speed torbica", "price": 899.99, "image": "balenciaga_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Balenciaga Hourglass denarnica", "price": 649.99, "image": "balenciaga_acc3.jpg", "type": "short"},
            ]
        },
        'versace': {
            'tshirts': [
                {"id": 1, "name": "Versace Medusa majica", "price": 399.99, "image": "versace_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Versace Barocco majica", "price": 449.99, "image": "versace_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Versace Logo majica", "price": 379.99, "image": "versace_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Versace Barocco hlače", "price": 749.99, "image": "versace_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Versace Medusa hlače", "price": 699.99, "image": "versace_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Versace La Greca hlače", "price": 779.99, "image": "versace_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Versace Barocco jakna", "price": 1499.99, "image": "versace_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Versace Medusa jakna", "price": 1799.99, "image": "versace_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Versace La Greca bomber", "price": 1299.99, "image": "versace_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Versace Medusa pas", "price": 399.99, "image": "versace_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Versace šal", "price": 349.99, "image": "versace_acc2.jpg", "type": "long"},
                {"id": 18, "name": "Versace denarnica", "price": 499.99, "image": "versace_acc3.jpg", "type": "short"},
            ]
        },
        'cortez': {
            'tshirts': [
                {"id": 1, "name": "Cortez Classic majica", "price": 79.99, "image": "cortez_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Cortez Vintage majica", "price": 89.99, "image": "cortez_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Cortez Logo majica", "price": 74.99, "image": "cortez_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Cortez Track hlače", "price": 99.99, "image": "cortez_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Cortez Vintage hlače", "price": 109.99, "image": "cortez_pants2.jpg", "type": "short"},
                {"id": 9, "name": "Cortez Cargo hlače", "price": 119.99, "image": "cortez_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Cortez Vintage jakna", "price": 159.99, "image": "cortez_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Cortez Track hoodie", "price": 129.99, "image": "cortez_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Cortez Classic jakna", "price": 139.99, "image": "cortez_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Cortez kapa", "price": 39.99, "image": "cortez_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Cortez športna torba", "price": 69.99, "image": "cortez_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Cortez nogavice", "price": 19.99, "image": "cortez_acc3.jpg", "type": "short"},
            ]
        },
        'Dolce & Gabbana': {
            'tshirts': [
                {"id": 1, "name": "Dolce & Gabbana Crown majica", "price": 499.99, "image": "dolce_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Dolce & Gabbana Logo majica", "price": 449.99, "image": "dolce_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Dolce & Gabbana Print majica", "price": 529.99, "image": "dolce_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Dolce & Gabbana Casual hlače", "price": 699.99, "image": "dolce_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Dolce & Gabbana Jogging hlače", "price": 649.99, "image": "dolce_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Dolce & Gabbana Denim hlače", "price": 749.99, "image": "dolce_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Dolce & Gabbana Bomber jakna", "price": 1899.99, "image": "dolce_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Dolce & Gabbana Logo jakna", "price": 1699.99, "image": "dolce_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Dolce & Gabbana Print hoodie", "price": 1199.99, "image": "dolce_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Dolce & Gabbana pas", "price": 449.99, "image": "dolce_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Dolce & Gabbana denarnica", "price": 549.99, "image": "dolce_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Dolce & Gabbana šal", "price": 399.99, "image": "dolce_acc3.jpg", "type": "long"},
            ]
        },
        'Tommy Hilfiger': {
            'tshirts': [
                {"id": 1, "name": "Tommy Hilfiger Logo majica", "price": 69.99, "image": "tommy_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Tommy Hilfiger Icon majica", "price": 79.99, "image": "tommy_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Tommy Hilfiger Flag majica", "price": 74.99, "image": "tommy_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "Tommy Hilfiger Polo majica", "price": 89.99, "image": "tommy_tshirt4.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Tommy Hilfiger Chino hlače", "price": 99.99, "image": "tommy_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Tommy Hilfiger Denim hlače", "price": 109.99, "image": "tommy_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Tommy Hilfiger Jogger hlače", "price": 89.99, "image": "tommy_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Tommy Hilfiger Flag jakna", "price": 189.99, "image": "tommy_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Tommy Hilfiger Bomber jakna", "price": 219.99, "image": "tommy_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Tommy Hilfiger Logo hoodie", "price": 149.99, "image": "tommy_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Tommy Hilfiger kapa", "price": 39.99, "image": "tommy_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Tommy Hilfiger pas", "price": 59.99, "image": "tommy_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Tommy Hilfiger denarnica", "price": 69.99, "image": "tommy_acc3.jpg", "type": "short"},
                {"id": 19, "name": "Tommy Hilfiger torba", "price": 99.99, "image": "tommy_acc4.jpg", "type": "short"},
            ]
        },
        'Calvin Klein': {
            'tshirts': [
                {"id": 1, "name": "Calvin Klein Logo majica", "price": 59.99, "image": "ck_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Calvin Klein Monogram majica", "price": 64.99, "image": "ck_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Calvin Klein Classic majica", "price": 54.99, "image": "ck_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "Calvin Klein dolga majica", "price": 69.99, "image": "ck_tshirt4.jpg", "type": "long"},
            ],
            'pants': [
                {"id": 7, "name": "Calvin Klein Slim hlače", "price": 99.99, "image": "ck_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Calvin Klein Jogger hlače", "price": 89.99, "image": "ck_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Calvin Klein Chino hlače", "price": 109.99, "image": "ck_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Calvin Klein Logo jakna", "price": 149.99, "image": "ck_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Calvin Klein Monogram hoodie", "price": 129.99, "image": "ck_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Calvin Klein zimska jakna", "price": 199.99, "image": "ck_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Calvin Klein pas", "price": 59.99, "image": "ck_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Calvin Klein denarnica", "price": 69.99, "image": "ck_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Calvin Klein torbica", "price": 99.99, "image": "ck_acc3.jpg", "type": "short"},
                {"id": 19, "name": "Calvin Klein nogavice", "price": 19.99, "image": "ck_acc4.jpg", "type": "short"},
            ]
        },
        'gucci': {
            'tshirts': [
                {"id": 1, "name": "Gucci Logo majica", "price": 549.99, "image": "gucci_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Gucci Oversize majica", "price": 599.99, "image": "gucci_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Gucci Print majica", "price": 649.99, "image": "gucci_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Gucci Track hlače", "price": 899.99, "image": "gucci_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Gucci Denim hlače", "price": 949.99, "image": "gucci_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Gucci Jogging hlače", "price": 849.99, "image": "gucci_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Gucci Logo jakna", "price": 1999.99, "image": "gucci_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Gucci Track jakna", "price": 1799.99, "image": "gucci_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Gucci Print hoodie", "price": 1499.99, "image": "gucci_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Gucci pas", "price": 549.99, "image": "gucci_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Gucci kapa", "price": 399.99, "image": "gucci_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Gucci denarnica", "price": 649.99, "image": "gucci_acc3.jpg", "type": "short"},
                {"id": 19, "name": "Gucci šal", "price": 499.99, "image": "gucci_acc4.jpg", "type": "long"},
            ]
        },
        'gallery dept.': {
            'tshirts': [
                {"id": 1, "name": "Gallery Dept. Logo majica", "price": 199.99, "image": "gallery_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Gallery Dept. Souvenir majica", "price": 219.99, "image": "gallery_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Gallery Dept. Art majica", "price": 189.99, "image": "gallery_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Gallery Dept. Flare hlače", "price": 399.99, "image": "gallery_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Gallery Dept. Carpenter hlače", "price": 429.99, "image": "gallery_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Gallery Dept. Baggy hlače", "price": 379.99, "image": "gallery_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Gallery Dept. Varsity jakna", "price": 599.99, "image": "gallery_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Gallery Dept. hoodie", "price": 349.99, "image": "gallery_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Gallery Dept. Denim jakna", "price": 499.99, "image": "gallery_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Gallery Dept. kapa", "price": 129.99, "image": "gallery_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Gallery Dept. torba", "price": 249.99, "image": "gallery_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Gallery Dept. pas", "price": 179.99, "image": "gallery_acc3.jpg", "type": "short"},
            ]
        },
        'puma': {
            'tshirts': [
                {"id": 1, "name": "Puma Essentials majica", "price": 34.99, "image": "puma_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Puma Logo majica", "price": 39.99, "image": "puma_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Puma Sport majica", "price": 44.99, "image": "puma_tshirt3.jpg", "type": "short"},
                {"id": 4, "name": "Puma Classics majica", "price": 37.99, "image": "puma_tshirt4.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Puma Essentials hlače", "price": 54.99, "image": "puma_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Puma Training hlače", "price": 59.99, "image": "puma_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Puma Track hlače", "price": 64.99, "image": "puma_pants3.jpg", "type": "long"},
                {"id": 10, "name": "Puma Sport hlače", "price": 49.99, "image": "puma_pants4.jpg", "type": "short"},
            ],
            'jackets': [
                {"id": 12, "name": "Puma Track jakna", "price": 84.99, "image": "puma_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Puma hoodie", "price": 69.99, "image": "puma_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Puma Windbreaker jakna", "price": 79.99, "image": "puma_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Puma Phase Backpack", "price": 39.99, "image": "puma_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Puma kapa", "price": 19.99, "image": "puma_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Puma nogavice", "price": 12.99, "image": "puma_acc3.jpg", "type": "short"},
                {"id": 19, "name": "Puma športna torba", "price": 44.99, "image": "puma_acc4.jpg", "type": "short"},
            ]
        },
        'Karl Lagerfeld': {
            'tshirts': [
                {"id": 1, "name": "Karl Lagerfeld Logo majica", "price": 89.99, "image": "karl_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Karl Lagerfeld Ikonik majica", "price": 99.99, "image": "karl_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Karl Lagerfeld Silhueta majica", "price": 94.99, "image": "karl_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Karl Lagerfeld Casual hlače", "price": 149.99, "image": "karl_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Karl Lagerfeld Sweat hlače", "price": 129.99, "image": "karl_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Karl Lagerfeld Denim hlače", "price": 169.99, "image": "karl_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Karl Lagerfeld Ikonik jakna", "price": 279.99, "image": "karl_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Karl Lagerfeld Bomber jakna", "price": 329.99, "image": "karl_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Karl Lagerfeld hoodie", "price": 199.99, "image": "karl_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Karl Lagerfeld kapa", "price": 69.99, "image": "karl_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Karl Lagerfeld denarnica", "price": 119.99, "image": "karl_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Karl Lagerfeld torbica", "price": 189.99, "image": "karl_acc3.jpg", "type": "short"},
            ]
        },
        'hellstar': {
            'tshirts': [
                {"id": 1, "name": "Hellstar Logo majica", "price": 89.99, "image": "hellstar_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Hellstar Graphic majica", "price": 99.99, "image": "hellstar_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Hellstar Vintage majica", "price": 79.99, "image": "hellstar_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Hellstar Cargo hlače", "price": 129.99, "image": "hellstar_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Hellstar Denim hlače", "price": 149.99, "image": "hellstar_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Hellstar Track hlače", "price": 119.99, "image": "hellstar_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Hellstar hoodie", "price": 159.99, "image": "hellstar_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Hellstar Denim jakna", "price": 219.99, "image": "hellstar_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Hellstar Logo jakna", "price": 189.99, "image": "hellstar_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Hellstar kapa", "price": 49.99, "image": "hellstar_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Hellstar pas", "price": 69.99, "image": "hellstar_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Hellstar nahrbtnik", "price": 99.99, "image": "hellstar_acc3.jpg", "type": "short"},
            ]
        },
        'Casablanca': {
            'tshirts': [
                {"id": 1, "name": "Casablanca Silk majica", "price": 369.99, "image": "casa_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Casablanca Tennis Club majica", "price": 329.99, "image": "casa_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Casablanca Grand Prix majica", "price": 349.99, "image": "casa_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Casablanca Silk hlače", "price": 549.99, "image": "casa_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Casablanca Tennis hlače", "price": 499.99, "image": "casa_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Casablanca Track hlače", "price": 469.99, "image": "casa_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Casablanca Silk jakna", "price": 999.99, "image": "casa_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Casablanca Après Sport jakna", "price": 899.99, "image": "casa_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Casablanca Tennis Club jakna", "price": 849.99, "image": "casa_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Casablanca Silk šal", "price": 249.99, "image": "casa_acc1.jpg", "type": "long"},
                {"id": 17, "name": "Casablanca kapa", "price": 189.99, "image": "casa_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Casablanca torba", "price": 499.99, "image": "casa_acc3.jpg", "type": "short"},
            ]
        },
        'The North Face': {
            'tshirts': [
                {"id": 1, "name": "The North Face Logo majica", "price": 49.99, "image": "tnf_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "The North Face Mountain majica", "price": 59.99, "image": "tnf_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "The North Face Exploration majica", "price": 54.99, "image": "tnf_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "The North Face Cargo hlače", "price": 89.99, "image": "tnf_pants1.jpg", "type": "long"},
                {"id": 8, "name": "The North Face Exploration hlače", "price": 99.99, "image": "tnf_pants2.jpg", "type": "long"},
                {"id": 9, "name": "The North Face Trail hlače", "price": 79.99, "image": "tnf_pants3.jpg", "type": "short"},
            ],
            'jackets': [
                {"id": 12, "name": "The North Face Nuptse jakna", "price": 299.99, "image": "tnf_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "The North Face Mountain jakna", "price": 249.99, "image": "tnf_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "The North Face Denali jakna", "price": 199.99, "image": "tnf_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "The North Face Expedition kapa", "price": 34.99, "image": "tnf_acc1.jpg", "type": "short"},
                {"id": 17, "name": "The North Face Base Camp torba", "price": 129.99, "image": "tnf_acc2.jpg", "type": "short"},
                {"id": 18, "name": "The North Face Borealis nahrbtnik", "price": 99.99, "image": "tnf_acc3.jpg", "type": "short"},
            ]
        },
        'prada': {
            'tshirts': [
                {"id": 1, "name": "Prada Logo majica", "price": 449.99, "image": "prada_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Prada Re-Nylon majica", "price": 499.99, "image": "prada_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Prada Tech majica", "price": 529.99, "image": "prada_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Prada Re-Nylon hlače", "price": 899.99, "image": "prada_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Prada Gabardine hlače", "price": 849.99, "image": "prada_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Prada Tech hlače", "price": 799.99, "image": "prada_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Prada Re-Nylon jakna", "price": 1799.99, "image": "prada_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Prada Technical jakna", "price": 1999.99, "image": "prada_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Prada Linea Rossa jakna", "price": 1699.99, "image": "prada_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Prada Re-Nylon kapa", "price": 399.99, "image": "prada_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Prada torbica", "price": 1499.99, "image": "prada_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Prada sončna očala", "price": 399.99, "image": "prada_acc3.jpg", "type": "short"},
            ]
        },
        'saint': {
            'tshirts': [
                {"id": 1, "name": "Saint Laurent Logo majica", "price": 449.99, "image": "saint_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Saint Laurent Signature majica", "price": 499.99, "image": "saint_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Saint Laurent Paris majica", "price": 449.99, "image": "saint_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Saint Laurent Skinny hlače", "price": 899.99, "image": "saint_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Saint Laurent Denim hlače", "price": 849.99, "image": "saint_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Saint Laurent Cargo hlače", "price": 799.99, "image": "saint_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Saint Laurent Teddy jakna", "price": 2199.99, "image": "saint_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Saint Laurent Leather jakna", "price": 3499.99, "image": "saint_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Saint Laurent Denim jakna", "price": 1699.99, "image": "saint_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Saint Laurent pas", "price": 499.99, "image": "saint_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Saint Laurent torbica", "price": 1499.99, "image": "saint_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Saint Laurent sončna očala", "price": 399.99, "image": "saint_acc3.jpg", "type": "short"},
            ]
        },
        'trapstar': {
            'tshirts': [
                {"id": 1, "name": "Trapstar Logo majica", "price": 119.99, "image": "trapstar_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Trapstar Irongate majica", "price": 129.99, "image": "trapstar_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Trapstar Decoded majica", "price": 109.99, "image": "trapstar_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Trapstar Track hlače", "price": 149.99, "image": "trapstar_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Trapstar Decoded hlače", "price": 159.99, "image": "trapstar_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Trapstar Jogger hlače", "price": 139.99, "image": "trapstar_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Trapstar Decoded jakna", "price": 219.99, "image": "trapstar_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Trapstar Irongate hoodie", "price": 199.99, "image": "trapstar_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Trapstar Track jakna", "price": 239.99, "image": "trapstar_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Trapstar kapa", "price": 69.99, "image": "trapstar_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Trapstar torba", "price": 99.99, "image": "trapstar_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Trapstar maska", "price": 39.99, "image": "trapstar_acc3.jpg", "type": "short"},
            ]
        },
        'armani': {
            'tshirts': [
                {"id": 1, "name": "Armani Logo majica", "price": 129.99, "image": "armani_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Armani Eagle majica", "price": 149.99, "image": "armani_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Armani Exchange majica", "price": 99.99, "image": "armani_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Armani Jeans hlače", "price": 199.99, "image": "armani_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Armani Chino hlače", "price": 219.99, "image": "armani_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Armani Elegantne hlače", "price": 249.99, "image": "armani_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Armani Bomber jakna", "price": 399.99, "image": "armani_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Armani Exchange jakna", "price": 349.99, "image": "armani_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Armani Elegantni plašč", "price": 599.99, "image": "armani_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Armani pas", "price": 149.99, "image": "armani_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Armani denarnica", "price": 179.99, "image": "armani_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Armani ura", "price": 349.99, "image": "armani_acc3.jpg", "type": "short"},
            ]
        },
        'canada': {
            'tshirts': [
                {"id": 1, "name": "Canada Goose Logo majica", "price": 119.99, "image": "canada_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Canada Goose Arctic majica", "price": 129.99, "image": "canada_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Canada Goose Graphic majica", "price": 109.99, "image": "canada_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Canada Goose Outdoor hlače", "price": 249.99, "image": "canada_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Canada Goose Arctic hlače", "price": 279.99, "image": "canada_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Canada Goose Expediton hlače", "price": 299.99, "image": "canada_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Canada Goose Expedition parka", "price": 1299.99, "image": "canada_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Canada Goose Chilliwack jakna", "price": 999.99, "image": "canada_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Canada Goose Langford parka", "price": 1199.99, "image": "canada_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Canada Goose kapa", "price": 149.99, "image": "canada_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Canada Goose rokavice", "price": 179.99, "image": "canada_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Canada Goose šal", "price": 199.99, "image": "canada_acc3.jpg", "type": "long"},
            ]
        },
        'Louis Vuitton': {
            'tshirts': [
                {"id": 1, "name": "Louis Vuitton Monogram majica", "price": 699.99, "image": "lv_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Louis Vuitton Damier majica", "price": 749.99, "image": "lv_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Louis Vuitton Logo majica", "price": 649.99, "image": "lv_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Louis Vuitton Monogram hlače", "price": 999.99, "image": "lv_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Louis Vuitton Pleated hlače", "price": 1099.99, "image": "lv_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Louis Vuitton Cargo hlače", "price": 1199.99, "image": "lv_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Louis Vuitton Monogram jakna", "price": 2499.99, "image": "lv_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Louis Vuitton Damier jakna", "price": 2699.99, "image": "lv_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Louis Vuitton Denim jakna", "price": 2299.99, "image": "lv_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Louis Vuitton pas", "price": 599.99, "image": "lv_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Louis Vuitton denarnica", "price": 899.99, "image": "lv_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Louis Vuitton torba", "price": 1499.99, "image": "lv_acc3.jpg", "type": "short"},
            ]
        },
        'valentino': {
            'tshirts': [
                {"id": 1, "name": "Valentino VLTN majica", "price": 499.99, "image": "valentino_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Valentino Logo majica", "price": 549.99, "image": "valentino_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Valentino Rock Stud majica", "price": 599.99, "image": "valentino_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Valentino Track hlače", "price": 799.99, "image": "valentino_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Valentino VLTN hlače", "price": 849.99, "image": "valentino_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Valentino Rock Stud hlače", "price": 899.99, "image": "valentino_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Valentino VLTN jakna", "price": 1599.99, "image": "valentino_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Valentino Rock Stud jakna", "price": 1799.99, "image": "valentino_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Valentino Casual jakna", "price": 1699.99, "image": "valentino_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Valentino pas", "price": 399.99, "image": "valentino_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Valentino torbica", "price": 1299.99, "image": "valentino_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Valentino Rock Stud denarnica", "price": 599.99, "image": "valentino_acc3.jpg", "type": "short"},
            ]
        },
        'essentials': {
            'tshirts': [
                {"id": 1, "name": "Fear of God Essentials majica", "price": 89.99, "image": "essentials_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Essentials Logo majica", "price": 99.99, "image": "essentials_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Essentials Boxy majica", "price": 79.99, "image": "essentials_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Essentials Sweat hlače", "price": 129.99, "image": "essentials_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Essentials Track hlače", "price": 139.99, "image": "essentials_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Essentials Nylon hlače", "price": 119.99, "image": "essentials_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Essentials Hoodie", "price": 149.99, "image": "essentials_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Essentials Zip-up hoodie", "price": 159.99, "image": "essentials_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Essentials Track jakna", "price": 169.99, "image": "essentials_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Essentials kapa", "price": 49.99, "image": "essentials_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Essentials nahrbtnik", "price": 129.99, "image": "essentials_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Essentials torba", "price": 109.99, "image": "essentials_acc3.jpg", "type": "short"},
            ]
        },
        'moncler': {
            'tshirts': [
                {"id": 1, "name": "Moncler Logo majica", "price": 249.99, "image": "moncler_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Moncler Tricolor majica", "price": 299.99, "image": "moncler_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Moncler Genius majica", "price": 329.99, "image": "moncler_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Moncler Casual hlače", "price": 449.99, "image": "moncler_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Moncler Sweat hlače", "price": 399.99, "image": "moncler_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Moncler Genius hlače", "price": 499.99, "image": "moncler_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Moncler Maya jakna", "price": 1499.99, "image": "moncler_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Moncler Genius jakna", "price": 1799.99, "image": "moncler_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Moncler Grenoble jakna", "price": 1699.99, "image": "moncler_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Moncler kapa", "price": 249.99, "image": "moncler_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Moncler šal", "price": 299.99, "image": "moncler_acc2.jpg", "type": "long"},
                {"id": 18, "name": "Moncler rokavice", "price": 229.99, "image": "moncler_acc3.jpg", "type": "short"},
            ]
        },
        'syna': {
            'tshirts': [
                {"id": 1, "name": "Syna Logo majica", "price": 129.99, "image": "syna_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Syna Premium majica", "price": 149.99, "image": "syna_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Syna Signature majica", "price": 139.99, "image": "syna_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Syna Track hlače", "price": 179.99, "image": "syna_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Syna Cargo hlače", "price": 199.99, "image": "syna_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Syna Premium hlače", "price": 189.99, "image": "syna_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Syna Logo jakna", "price": 249.99, "image": "syna_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Syna Premium jakna", "price": 299.99, "image": "syna_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Syna Signature hoodie", "price": 229.99, "image": "syna_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Syna kapa", "price": 69.99, "image": "syna_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Syna torbica", "price": 119.99, "image": "syna_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Syna nahrbtnik", "price": 149.99, "image": "syna_acc3.jpg", "type": "short"},
            ]
        },
        'Off-White': {
            'tshirts': [
                {"id": 1, "name": "Off-White Arrows majica", "price": 349.99, "image": "off_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Off-White Diagonal majica", "price": 329.99, "image": "off_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Off-White Logo majica", "price": 299.99, "image": "off_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Off-White Diagonal hlače", "price": 549.99, "image": "off_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Off-White Industrial hlače", "price": 599.99, "image": "off_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Off-White Arrows hlače", "price": 499.99, "image": "off_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Off-White Arrows jakna", "price": 999.99, "image": "off_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Off-White Industrial jakna", "price": 1099.99, "image": "off_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Off-White Diagonal jakna", "price": 899.99, "image": "off_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Off-White Industrial pas", "price": 249.99, "image": "off_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Off-White torba", "price": 599.99, "image": "off_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Off-White kapa", "price": 199.99, "image": "off_acc3.jpg", "type": "short"},
            ]
        },
        'fendi': {
            'tshirts': [
                {"id": 1, "name": "Fendi FF Logo majica", "price": 499.99, "image": "fendi_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Fendi Roma majica", "price": 549.99, "image": "fendi_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Fendi Karligraphy majica", "price": 529.99, "image": "fendi_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Fendi FF Logo hlače", "price": 849.99, "image": "fendi_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Fendi Track hlače", "price": 799.99, "image": "fendi_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Fendi Roma hlače", "price": 899.99, "image": "fendi_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Fendi FF Logo jakna", "price": 1799.99, "image": "fendi_jacket1.jpg", "type": "short"},
                {"id": 13, "name": "Fendi Roma bomber", "price": 1899.99, "image": "fendi_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Fendi Karligraphy hoodie", "price": 1299.99, "image": "fendi_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Fendi FF Logo pas", "price": 449.99, "image": "fendi_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Fendi Peekaboo torbica", "price": 2499.99, "image": "fendi_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Fendi kapa", "price": 349.99, "image": "fendi_acc3.jpg", "type": "short"},
            ]
        },
        'spider': {
            'tshirts': [
                {"id": 1, "name": "Spider Logo majica", "price": 99.99, "image": "spider_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Spider Graphic majica", "price": 109.99, "image": "spider_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Spider Web majica", "price": 89.99, "image": "spider_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Spider Track hlače", "price": 149.99, "image": "spider_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Spider Cargo hlače", "price": 159.99, "image": "spider_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Spider Web hlače", "price": 139.99, "image": "spider_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Spider Logo hoodie", "price": 199.99, "image": "spider_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Spider Graphic jakna", "price": 249.99, "image": "spider_jacket2.jpg", "type": "short"},
                {"id": 14, "name": "Spider Web hoodie", "price": 219.99, "image": "spider_jacket3.jpg", "type": "long"},
            ],
            'accessories': [
                {"id": 16, "name": "Spider kapa", "price": 49.99, "image": "spider_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Spider nahrbtnik", "price": 119.99, "image": "spider_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Spider pas", "price": 79.99, "image": "spider_acc3.jpg", "type": "short"},
            ]
        },
        'Stone Island': {
            'tshirts': [
                {"id": 1, "name": "Stone Island Logo majica", "price": 199.99, "image": "stone_tshirt1.jpg", "type": "short"},
                {"id": 2, "name": "Stone Island Patch majica", "price": 219.99, "image": "stone_tshirt2.jpg", "type": "short"},
                {"id": 3, "name": "Stone Island Marina majica", "price": 229.99, "image": "stone_tshirt3.jpg", "type": "short"},
            ],
            'pants': [
                {"id": 7, "name": "Stone Island Cargo hlače", "price": 299.99, "image": "stone_pants1.jpg", "type": "long"},
                {"id": 8, "name": "Stone Island Ghost hlače", "price": 319.99, "image": "stone_pants2.jpg", "type": "long"},
                {"id": 9, "name": "Stone Island Shadow hlače", "price": 339.99, "image": "stone_pants3.jpg", "type": "long"},
            ],
            'jackets': [
                {"id": 12, "name": "Stone Island Soft Shell jakna", "price": 599.99, "image": "stone_jacket1.jpg", "type": "long"},
                {"id": 13, "name": "Stone Island Membrana jakna", "price": 649.99, "image": "stone_jacket2.jpg", "type": "long"},
                {"id": 14, "name": "Stone Island Ghost jakna", "price": 699.99, "image": "stone_jacket3.jpg", "type": "short"},
            ],
            'accessories': [
                {"id": 16, "name": "Stone Island kapa", "price": 119.99, "image": "stone_acc1.jpg", "type": "short"},
                {"id": 17, "name": "Stone Island torba", "price": 199.99, "image": "stone_acc2.jpg", "type": "short"},
                {"id": 18, "name": "Stone Island rokavice", "price": 149.99, "image": "stone_acc3.jpg", "type": "short"},
            ]
        },
    }
    
    # Pridobi posebne izdelke za izbrano znamko in kategorijo
    if brand_name in brand_specific_products and category in brand_specific_products[brand_name]:
        products = brand_specific_products[brand_name][category]
    # Če za izbrano znamko nimamo posebnih izdelkov, uporabimo osnovno predlogo in prilagodimo cene
    elif category in base_products:
        # Kopiramo osnovne izdelke
        products = base_products[category].copy()
        
        # Prilagodimo cene glede na znamko
        price_factors = {
            'lacoste': 2.5,
            'polo': 3.0,
            'burberry': 8.0,
            'dior': 12.0,
            'nike': 1.8,
            'balmain': 10.0,
            'bape': 4.0,
            'ami': 5.0,
            'jordan': 2.0
        }
        
        # Pridobi faktor za izbrano znamko (privzeto 1.0)
        factor = price_factors.get(brand_name.lower(), 1.0)
        
        # Prilagodi izdelke
        for product in products:
            # Prilagodi ceno
            product['price'] = round(product['price'] * factor, 2)
            # Dodaj ime znamke
            product['name'] = f"{brand_name.capitalize()} {product['name']}"
            # Dodaj prefiks za sliko
            product['image'] = f"{brand_name.lower()}_{product['image']}"
            
            # Alternativna slika za fallback, če specifična slika ni na voljo
            product['image_fallback'] = f"{brand_name.lower()}.jpg"
    else:
        products = []
    
    return render_template('products.html', brand=brand_name, category=category, products=products)

# Preureditev obstoječe funkcije send_admin_notification v splošno funkcijo za pošiljanje e-pošte
def send_email(recipient, subject, message):
    # Ustvarite sporočilo
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    
    # Dodajte vsebino
    msg.attach(MIMEText(message, 'plain'))
    
    # Pošljite e-pošto
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print(f"E-pošta uspešno poslana prejemniku: {recipient}")
        return True
    except Exception as e:
        print(f"Napaka pri pošiljanju e-pošte: {str(e)}")
        return False

# Posodobljena funkcija submit_order, ki pošlje e-pošto tudi kupcu
@app.route('/submit-order', methods=['POST'])
def submit_order():
    try:
        # Prejmi podatke iz POST zahteve
        data = request.json
        customer_email = data.get('email')
        customer_instagram = data.get('instagram')
        total_price = data.get('total')
        items = data.get('items', [])
        
        # Sestavi sporočilo za administratorja
        admin_message = f"Novo naročilo!\n\n"
        admin_message += f"Email kupca: {customer_email}\n"
        admin_message += f"Instagram: @{customer_instagram}\n"
        admin_message += f"Skupna vrednost: {total_price}€\n\n"
        admin_message += "Naročeni izdelki:\n"
        
        # Sestavimo del sporočila s seznamom izdelkov (uporabno za obe e-pošti)
        items_list = ""
        for item in items:
            # Dodamo velikost v sporočilo
            item_size = item.get('size', 'Ni izbrano')
            item_line = f"- {item['name']} (Velikost: {item_size}) - {item['price']}€\n"
            admin_message += item_line
            items_list += item_line
        
        # Shrani naročilo v datoteko (za zgodovino)
        with open(ORDERS_FILE, 'a') as f:
            order_data = {
                'email': customer_email,
                'instagram': customer_instagram,
                'total': total_price,
                'items': items,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            f.write(json.dumps(order_data) + '\n')
        
        # Pošlji e-pošto administratorju
        admin_subject = "Novo naročilo - Cory's Clothing"
        send_email("corysreps@gmail.com", admin_subject, admin_message)
        
        # Sestavi sporočilo za kupca
        customer_message = f"Spoštovani,\n\n"
        customer_message += f"Zahvaljujemo se vam za vaše naročilo pri Cory's Clothing!\n\n"
        customer_message += f"Podrobnosti vašega naročila:\n"
        customer_message += f"Instagram: @{customer_instagram}\n"
        customer_message += f"Skupna vrednost: {total_price}€\n\n"
        customer_message += "Naročeni izdelki:\n"
        customer_message += items_list
        customer_message += "\nKontaktirali vas bomo preko Instagrama (@{}) za nadaljnja navodila glede plačila in dostave. V primeru da nimate instagrama vas bomo kontaktirali po Mailu.\n\n".format(customer_instagram)
        customer_message += "V primeru kakršnihkoli vprašanj nas lahko kontaktirate preko Instagrama @corysreps ali odgovorite na to e-pošto.\n\n"
        customer_message += "Hvala za vaše zaupanje!\n"
        customer_message += "Cory's Clothing Team"
        
        # Pošlji e-pošto kupcu
        customer_subject = "Potrditev naročila - Cory's Clothing"
        send_email(customer_email, customer_subject, customer_message)
        
        return jsonify({'success': True, 'message': 'Naročilo uspešno oddano'})
    except Exception as e:
        print(f"Napaka pri oddaji naročila: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)