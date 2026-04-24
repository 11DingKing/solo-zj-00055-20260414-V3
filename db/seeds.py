from hello.models import User, Product
from hello.extensions import db


def seed():
    admin_user = User.query.filter_by(username="admin").first()
    if not admin_user:
        admin_user = User(
            username="admin",
            email="admin@example.com",
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)
        db.session.commit()
        print("Created admin user: admin / admin123")

    product_count = Product.query.count()
    if product_count == 0:
        sample_products = [
            {
                "name": "MacBook Pro 16英寸",
                "sku": "MBP-16-2024",
                "category": "笔记本电脑",
                "price": 19999.00,
                "stock": 50,
                "status": "active",
                "description": "搭载M3 Max芯片的专业级笔记本电脑",
            },
            {
                "name": "iPhone 15 Pro Max",
                "sku": "IP15PM-256",
                "category": "手机",
                "price": 9999.00,
                "stock": 200,
                "status": "active",
                "description": "钛金属设计，A17 Pro芯片",
            },
            {
                "name": "AirPods Pro 2",
                "sku": "APP2-USB-C",
                "category": "音频设备",
                "price": 1899.00,
                "stock": 500,
                "status": "active",
                "description": "主动降噪，空间音频",
            },
            {
                "name": "iPad Pro 12.9",
                "sku": "IPADP-129-2024",
                "category": "平板电脑",
                "price": 8999.00,
                "stock": 0,
                "status": "out_of_stock",
                "description": "M3芯片，Liquid Retina XDR显示屏",
            },
            {
                "name": "Apple Watch Ultra 2",
                "sku": "AWU2-49",
                "category": "智能穿戴",
                "price": 6499.00,
                "stock": 100,
                "status": "active",
                "description": "49mm钛金属表壳，精准双频GPS",
            },
            {
                "name": "Magic Keyboard",
                "sku": "MK-NUMPAD",
                "category": "配件",
                "price": 999.00,
                "stock": 300,
                "status": "active",
                "description": "触控ID，带数字小键盘",
            },
            {
                "name": "Studio Display",
                "sku": "SD-27-5K",
                "category": "显示器",
                "price": 11499.00,
                "stock": 25,
                "status": "active",
                "description": "27英寸5K视网膜显示屏，12MP超广角摄像头",
            },
            {
                "name": "Mac Mini M2",
                "sku": "MM-M2-8GB",
                "category": "台式电脑",
                "price": 4499.00,
                "stock": 0,
                "status": "out_of_stock",
                "description": "M2芯片，8GB统一内存",
            },
            {
                "name": "HomePod mini",
                "sku": "HPM-WHITE",
                "category": "智能家居",
                "price": 749.00,
                "stock": 0,
                "status": "inactive",
                "description": "智能音箱，Siri加持",
            },
            {
                "name": "Apple TV 4K",
                "sku": "ATV4K-128",
                "category": "娱乐设备",
                "price": 1499.00,
                "stock": 150,
                "status": "active",
                "description": "A15仿生芯片，128GB存储",
            },
        ]

        for product_data in sample_products:
            product = Product(**product_data)
            db.session.add(product)

        db.session.commit()
        print(f"Created {len(sample_products)} sample products")
