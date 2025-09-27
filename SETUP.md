# MongoDB Atlas Vector Search Application

## 🔐 Configuration Setup

### Method 1: Environment Variables (Recommended)
```bash
# Create .env file (not tracked by git)
cp .env.example .env

# Edit .env with your credentials
MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0
```

### Method 2: Direct Configuration
Edit `vector_search.py` line 20 with your connection string:
```python
'MONGODB_URI': os.getenv('MONGODB_URI', 
    "mongodb+srv://dueprincipati:YOUR_PASSWORD@cluster0.lcobvz0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"),
```

## 🚨 Security Note
Never commit actual credentials to public repositories. Use environment variables or GitHub secrets for production deployments.