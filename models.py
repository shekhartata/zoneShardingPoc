"""
Data models for MongoDB Zone Sharding Demo
Defines schemas for tenant-specific and common collections
"""

from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
import uuid


@dataclass
class User:
    """Common user model accessible across all regions"""
    user_id: str
    username: str
    email: str
    country: str
    region: str
    created_at: datetime
    last_login: datetime
    preferences: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['last_login'] = self.last_login.isoformat()
        return data


@dataclass
class Product:
    """Common product catalog accessible across all regions"""
    product_id: str
    name: str
    description: str
    category: str
    price: float
    currency: str
    available_regions: List[str]
    created_at: datetime
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class Category:
    """Common category model"""
    category_id: str
    name: str
    description: str
    parent_category: str = None
    created_at: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.created_at:
            data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class Order:
    """Tenant-specific order model (sharded by region)"""
    order_id: str
    user_id: str
    country: str
    region: str
    products: List[Dict[str, Any]]
    total_amount: float
    currency: str
    status: str
    created_at: datetime
    updated_at: datetime
    shipping_address: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


@dataclass
class Transaction:
    """Tenant-specific transaction model (sharded by region)"""
    transaction_id: str
    order_id: str
    user_id: str
    country: str
    region: str
    amount: float
    currency: str
    payment_method: str
    status: str
    created_at: datetime
    processed_at: datetime = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        if self.processed_at:
            data['processed_at'] = self.processed_at.isoformat()
        return data


@dataclass
class Log:
    """Tenant-specific log model (sharded by region)"""
    log_id: str
    user_id: str
    country: str
    region: str
    action: str
    resource: str
    details: Dict[str, Any]
    ip_address: str
    user_agent: str
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data


class DataGenerator:
    """Utility class to generate sample data for demo"""
    
    @staticmethod
    def generate_user(country: str, region: str) -> User:
        """Generate a sample user"""
        user_id = str(uuid.uuid4())
        username = f"user_{user_id[:8]}"
        email = f"{username}@example.com"
        
        return User(
            user_id=user_id,
            username=username,
            email=email,
            country=country,
            region=region,
            created_at=datetime.now(),
            last_login=datetime.now(),
            preferences={
                "language": "en" if country in ["US", "GB"] else "local",
                "timezone": "UTC",
                "notifications": True
            }
        )
    
    @staticmethod
    def generate_product() -> Product:
        """Generate a sample product"""
        product_id = str(uuid.uuid4())
        categories = ["Electronics", "Clothing", "Books", "Home", "Sports"]
        
        return Product(
            product_id=product_id,
            name=f"Product {product_id[:8]}",
            description=f"Description for product {product_id[:8]}",
            category=categories[hash(product_id) % len(categories)],
            price=round(10.0 + (hash(product_id) % 1000) / 10, 2),
            currency="USD",
            available_regions=["CN", "TR", "AE", "US", "EU", "GB"],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    @staticmethod
    def generate_category() -> Category:
        """Generate a sample category"""
        category_id = str(uuid.uuid4())
        categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Automotive", "Health"]
        
        return Category(
            category_id=category_id,
            name=categories[hash(category_id) % len(categories)],
            description=f"Category description for {categories[hash(category_id) % len(categories)]}",
            created_at=datetime.now()
        )
    
    @staticmethod
    def generate_order(user_id: str, country: str, region: str) -> Order:
        """Generate a sample order"""
        order_id = str(uuid.uuid4())
        
        return Order(
            order_id=order_id,
            user_id=user_id,
            country=country,
            region=region,
            products=[
                {"product_id": str(uuid.uuid4()), "quantity": 1, "price": 25.99},
                {"product_id": str(uuid.uuid4()), "quantity": 2, "price": 15.50}
            ],
            total_amount=56.99,
            currency="USD",
            status="pending",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            shipping_address={
                "street": "123 Main St",
                "city": "Sample City",
                "country": country,
                "postal_code": "12345"
            }
        )
    
    @staticmethod
    def generate_transaction(order_id: str, user_id: str, country: str, region: str) -> Transaction:
        """Generate a sample transaction"""
        transaction_id = str(uuid.uuid4())
        
        return Transaction(
            transaction_id=transaction_id,
            order_id=order_id,
            user_id=user_id,
            country=country,
            region=region,
            amount=56.99,
            currency="USD",
            payment_method="credit_card",
            status="completed",
            created_at=datetime.now(),
            processed_at=datetime.now()
        )
    
    @staticmethod
    def generate_log(user_id: str, country: str, region: str) -> Log:
        """Generate a sample log entry"""
        log_id = str(uuid.uuid4())
        actions = ["login", "logout", "view_product", "add_to_cart", "checkout", "payment"]
        
        return Log(
            log_id=log_id,
            user_id=user_id,
            country=country,
            region=region,
            action=actions[hash(log_id) % len(actions)],
            resource=f"resource_{hash(log_id) % 100}",
            details={"session_id": str(uuid.uuid4())},
            ip_address=f"192.168.1.{hash(log_id) % 255}",
            user_agent="Mozilla/5.0 (Demo Browser)",
            created_at=datetime.now()
        )
