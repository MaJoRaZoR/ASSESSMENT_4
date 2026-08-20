"""
Inventory and Supply Chain Management System
Filename: InventoryManagement.py
Provides core inventory, warehouse, supplier, and multi-warehouse order routing mechanics.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import threading

@dataclass
class Supplier:
    supplier_id: str
    name: str
    contact: str

@dataclass
class Product:
    product_id: str
    name: str
    reorder_threshold: int
    reorder_quantity: int
    supplier_id: str

@dataclass
class Warehouse:
    warehouse_id: str
    name: str
    inventory: Dict[str, int] = field(default_factory=dict)  # product_id -> quantity

class InventorySystem:
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.warehouses: Dict[str, Warehouse] = {}
        self.suppliers: Dict[str, Supplier] = {}
        self.lock = threading.Lock()
        
        # Initialize default warehouses
        for wh_id in ['Warehouse A', 'Warehouse B', 'Warehouse C']:
            self.warehouses[wh_id] = Warehouse(warehouse_id=wh_id, name=wh_id)

    def add_supplier(self, supplier_id: str, name: str, contact: str) -> None:
        with self.lock:
            self.suppliers[supplier_id] = Supplier(supplier_id, name, contact)

    def add_product_definition(self, product_id: str, name: str, reorder_threshold: int, reorder_quantity: int, supplier_id: str) -> None:
        with self.lock:
            if supplier_id not in self.suppliers:
                raise ValueError(f"Supplier {supplier_id} does not exist.")
            self.products[product_id] = Product(product_id, name, reorder_threshold, reorder_quantity, supplier_id)

    def add_stock(self, warehouse_id: str, product_id: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Cannot add negative stock.")
        with self.lock:
            if warehouse_id not in self.warehouses:
                raise ValueError(f"Warehouse {warehouse_id} does not exist.")
            if product_id not in self.products:
                raise ValueError(f"Product {product_id} is not defined.")
            
            wh = self.warehouses[warehouse_id]
            wh.inventory[product_id] = wh.inventory.get(product_id, 0) + quantity

    def remove_stock(self, warehouse_id: str, product_id: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Quantity to remove cannot be negative.")
        with self.lock:
            if warehouse_id not in self.warehouses:
                raise ValueError(f"Warehouse {warehouse_id} does not exist.")
            if product_id not in self.products:
                raise ValueError(f"Product {product_id} is not defined.")
            
            wh = self.warehouses[warehouse_id]
            current_stock = wh.inventory.get(product_id, 0)
            if current_stock < quantity:
                raise ValueError(f"Insufficient inventory in {warehouse_id} for product {product_id}.")
            
            wh.inventory[product_id] = current_stock - quantity

    def transfer_stock(self, from_warehouse_id: str, to_warehouse_id: str, product_id: str, quantity: int) -> None:
        if quantity < 0:
            raise ValueError("Transfer quantity cannot be negative.")
        if from_warehouse_id == to_warehouse_id:
            raise ValueError("Source and destination warehouses must be different.")
            
        with self.lock:
            if from_warehouse_id not in self.warehouses or to_warehouse_id not in self.warehouses:
                raise ValueError("One or both warehouses do not exist.")
            if product_id not in self.products:
                raise ValueError(f"Product {product_id} is not defined.")
                
            wh_src = self.warehouses[from_warehouse_id]
            wh_dest = self.warehouses[to_warehouse_id]
            
            if wh_src.inventory.get(product_id, 0) < quantity:
                raise ValueError(f"Insufficient stock in {from_warehouse_id} to perform transfer.")
                
            wh_src.inventory[product_id] -= quantity
            wh_dest.inventory[product_id] = wh_dest.inventory.get(product_id, 0) + quantity

    def get_total_stock(self, product_id: str) -> int:
        with self.lock:
            if product_id not in self.products:
                raise ValueError(f"Product {product_id} is not defined.")
            return sum(wh.inventory.get(product_id, 0) for wh in self.warehouses.values())

    def check_low_stock(self, product_id: str) -> bool:
        with self.lock:
            if product_id not in self.products:
                raise ValueError(f"Product {product_id} is not defined.")
            prod = self.products[product_id]
            total_stock = sum(wh.inventory.get(product_id, 0) for wh in self.warehouses.values())
            return total_stock <= prod.reorder_threshold

    def trigger_reorder(self, product_id: str, target_warehouse_id: str) -> Optional[dict]:
        with self.lock:
            if product_id not in self.products:
                raise ValueError(f"Product {product_id} is not defined.")
            if target_warehouse_id not in self.warehouses:
                raise ValueError(f"Warehouse {target_warehouse_id} does not exist.")
                
            prod = self.products[product_id]
            total_stock = sum(wh.inventory.get(product_id, 0) for wh in self.warehouses.values())
            
            if total_stock <= prod.reorder_threshold:
                # Simulate reorder process
                wh = self.warehouses[target_warehouse_id]
                wh.inventory[product_id] = wh.inventory.get(product_id, 0) + prod.reorder_quantity
                return {
                    "product_id": product_id,
                    "supplier_id": prod.supplier_id,
                    "ordered_quantity": prod.reorder_quantity,
                    "delivered_to": target_warehouse_id
                }
            return None

    def fulfill_order(self, product_id: str, quantity: int) -> str:
        """
        Automatically selects the first warehouse with enough stock to fulfill the order.
        Returns the warehouse_id that fulfilled the order.
        """
        if quantity < 0:
            raise ValueError("Order quantity cannot be negative.")
            
        with self.lock:
            if product_id not in self.products:
                raise ValueError(f"Product {product_id} is not defined.")
                
            # Selection Strategy: Prioritize warehouse with sufficient stock sequentially (A, B, C)
            selected_warehouse: Optional[str] = None
            for wh_id in ['Warehouse A', 'Warehouse B', 'Warehouse C']:
                if self.warehouses[wh_id].inventory.get(product_id, 0) >= quantity:
                    selected_warehouse = wh_id
                    break
                    
            if not selected_warehouse:
                raise ValueError(f"Insufficient inventory across all warehouses to fulfill order of {quantity} units.")
                
            self.warehouses[selected_warehouse].inventory[product_id] -= quantity
            return selected_warehouse
