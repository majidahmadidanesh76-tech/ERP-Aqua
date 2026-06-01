"""
مدیریت کاربران برای ERP-Aqua
"""

import json
import os
import hashlib
import datetime


class UserManager:
    """مدیریت کاربران سیستم"""
    
    def __init__(self):
        self.users_file = "data/users.json"
        self.current_user = None
        self.ensure_data_dir()
    
    def ensure_data_dir(self):
        """اطمینان از وجود پوشه داده‌ها"""
        if not os.path.exists("data"):
            os.makedirs("data")
    
    def load_users(self):
        """بارگذاری لیست کاربران"""
        if not os.path.exists(self.users_file):
            return []
        
        try:
            with open(self.users_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("users", [])
        except:
            return []
    
    def save_users(self, users):
        """ذخیره لیست کاربران"""
        with open(self.users_file, "w", encoding="utf-8") as f:
            json.dump({"users": users}, f, indent=2, ensure_ascii=False)
    
    def hash_password(self, password):
        """هش کردن رمز عبور"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def add_user(self, username, password, name, role="user"):
        """افزودن کاربر جدید"""
        users = self.load_users()
        
        # بررسی تکراری نبودن نام کاربری
        for user in users:
            if user["username"] == username:
                return False, "نام کاربری تکراری است"
        
        new_user = {
            "username": username,
            "password": self.hash_password(password),
            "name": name,
            "role": role,
            "created_at": datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
        }
        
        users.append(new_user)
        self.save_users(users)
        return True, "کاربر با موفقیت اضافه شد"
    
    def delete_user(self, username):
        """حذف کاربر"""
        users = self.load_users()
        new_users = [u for u in users if u["username"] != username]
        
        if len(new_users) == len(users):
            return False, "کاربر یافت نشد"
        
        self.save_users(new_users)
        return True, "کاربر با موفقیت حذف شد"
    
    def change_password(self, username, old_password, new_password):
        """تغییر رمز عبور"""
        users = self.load_users()
        hashed_old = self.hash_password(old_password)
        
        for i, user in enumerate(users):
            if user["username"] == username:
                if user["password"] != hashed_old:
                    return False, "رمز عبور فعلی اشتباه است"
                
                users[i]["password"] = self.hash_password(new_password)
                self.save_users(users)
                return True, "رمز عبور با موفقیت تغییر کرد"
        
        return False, "کاربر یافت نشد"
    
    def check_login(self, username, password):
        """بررسی ورود"""
        users = self.load_users()
        hashed_password = self.hash_password(password)
        
        for user in users:
            if user["username"] == username and user["password"] == hashed_password:
                self.current_user = {
                    "username": user["username"],
                    "name": user["name"],
                    "role": user["role"]
                }
                return True, self.current_user
        
        return False, None