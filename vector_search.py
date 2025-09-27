from pymongo import MongoClient
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import sys
from pymongo.errors import ConnectionFailure, OperationFailure

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, use system env vars

# Step 2: Configuration and Connection Management
def load_config():
    """Load configuration from environment variables or default values"""
    config = {
        'MONGODB_URI': os.getenv('MONGODB_URI', 
            "mongodb+srv://username:password@cluster0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"),
        'DATABASE_NAME': os.getenv('DATABASE_NAME', 'vectorDemo'),
        'COLLECTION_NAME': os.getenv('COLLECTION_NAME', 'items'),
        'MODEL_NAME': os.getenv('MODEL_NAME', 'sentence-transformers/all-mpnet-base-v2'),
        'VECTOR_INDEX_NAME': os.getenv('VECTOR_INDEX_NAME', 'vector_index')
    }
    return config

def connect_to_mongodb(uri, db_name, collection_name):
    """Connect to MongoDB with error handling"""
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        # Test the connection
        client.admin.command('ping')
        db = client[db_name]
        collection = db[collection_name]
        print("✅ Connected to MongoDB Atlas")
        return client, db, collection
    except ConnectionFailure:
        print("❌ Failed to connect to MongoDB. Check your connection string and network.")
        return None, None, None
    except OperationFailure as e:
        if "authentication failed" in str(e):
            print("❌ Authentication failed. Please check your username and password.")
            print("💡 Make sure to replace <db_password> with your actual password.")
        else:
            print(f"❌ MongoDB operation failed: {e}")
        return None, None, None
    except Exception as e:
        print(f"❌ Unexpected error connecting to MongoDB: {e}")
        return None, None, None

def load_model(model_name):
    """Load the sentence transformer model with error handling"""
    try:
        print(f"🔄 Loading model: {model_name}")
        model = SentenceTransformer(model_name)
        print("✅ Model loaded successfully")
        return model
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        print("💡 This might take a while on first run as the model needs to be downloaded.")
        return None

# Load configuration
config = load_config()

# Connect to MongoDB Atlas with error handling
client, db, collection = connect_to_mongodb(
    config['MONGODB_URI'], 
    config['DATABASE_NAME'], 
    config['COLLECTION_NAME']
)

if not client:
    print("❌ Cannot continue without database connection. Please fix the connection and try again.")
    print("\n💡 To fix:")
    print("1. Create a .env file: cp .env.example .env")
    print("2. Edit .env with your MongoDB Atlas credentials")
    print("3. Or set MONGODB_URI environment variable with your connection string")
    print("4. Ensure your IP is whitelisted in MongoDB Atlas")
    print("\n📁 Example .env file:")
    print("MONGODB_URI=mongodb+srv://username:password@cluster0.mongodb.net/...")
    sys.exit(1)

# Step 3: Generate embeddings with Python
# Load the model
model = load_model(config['MODEL_NAME'])
if not model:
    print("❌ Cannot continue without the embedding model.")
    sys.exit(1)

# Clear existing data (with confirmation)
try:
    count = collection.count_documents({})
    if count > 0:
        response = input(f"⚠️  Found {count} existing documents. Clear them? (y/N): ")
        if response.lower() == 'y':
            result = collection.delete_many({})
            print(f"🗑️  Cleared {result.deleted_count} documents.")
        else:
            print("📁 Keeping existing documents.")
    else:
        print("📄 Collection is empty.")
except Exception as e:
    print(f"❌ Error checking/clearing collection: {e}")

def embed_text(text: str):
    """Generate embeddings for text with error handling"""
    try:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        return model.encode(text.strip()).tolist()
    except Exception as e:
        print(f"❌ Error generating embedding for text: {e}")
        return None

# Step 4: Insert sample documents with embeddings
# Each product includes name, description, list of features, use_cases and tags.
products = [
    # Marathon / long-distance running (explicit!)
    {
        "name": "MarathonPro 3000",
        "description": "Designed specifically for marathon and ultra distance running: maximum cushioning, breathable knit upper, responsive midsole and engineered heel support for long-run comfort.",
        "features": ["marathon", "long-distance", "max cushioning", "breathable", "support"],
        "category": "shoes",
        "use_cases": ["marathon", "long-distance running", "road running"],
        "tags": ["running", "endurance", "comfort"]
    },
    {
        "name": "Enduro LongRun",
        "description": "Lightweight long-run trainer optimized for marathon pacing with added cushioning, stable platform, and enhanced forefoot energy return for hours of comfortable running.",
        "features": ["long-run", "lightweight", "energy return", "cushioning"],
        "category": "shoes",
        "use_cases": ["marathon", "road running"],
        "tags": ["running","marathon","comfort"]
    },

    # Road running / neutral
    {
        "name": "Red Road Runner",
        "description": "Neutral road running shoe for daily training: breathable mesh, moderate cushioning and responsive ride; suitable for tempo runs and long easy runs.",
        "features": ["road running", "breathable", "moderate cushioning"],
        "category": "shoes",
        "use_cases": ["training", "road running", "tempo runs"],
        "tags": ["running","training"]
    },

    # Trail running (explicit trail)
    {
        "name": "TrailMaster RidgeGrip",
        "description": "Trail-running shoe with aggressive outsole, rock plate for protection, waterproof upper, designed for technical trails and rugged terrain.",
        "features": ["trail", "high grip", "rock plate", "waterproof"],
        "category": "shoes",
        "use_cases": ["trail running", "hiking", "off-road"],
        "tags": ["trail","outdoors"]
    },

    # Tennis & court
    {
        "name": "CourtPro Tennis",
        "description": "Court shoe with lateral support, non-marking sole and reinforced toe; built for tennis footwork and short intense bursts, not for long-distance running.",
        "features": ["court", "lateral support", "non-marking sole"],
        "category": "shoes",
        "use_cases": ["tennis","court sports"],
        "tags": ["tennis","sport"]
    },

    # Formal
    {
        "name": "Oxford Leather Formal",
        "description": "Classic leather formal shoe for office and events: polished leather, sturdy sole, refined silhouette.",
        "features": ["formal", "leather", "office"],
        "category": "shoes",
        "use_cases": ["formal wear","office"],
        "tags": ["formal","leather"]
    },

    # Hiking
    {
        "name": "Alpine Trek Boots",
        "description": "High-ankle hiking boots with waterproof membrane, ankle support and durable lugged outsole for mountain treks.",
        "features": ["hiking", "waterproof", "ankle support", "lugged outsole"],
        "category": "shoes",
        "use_cases": ["hiking","trekking","outdoor"],
        "tags": ["outdoors","hiking"]
    },

    # Casual sneakers
    {
        "name": "Classic Canvas Sneaker",
        "description": "Casual everyday canvas sneaker with rubber sole, comfortable fit for daily wear and walking.",
        "features": ["casual","canvas", "everyday"],
        "category": "shoes",
        "use_cases": ["casual","walking"],
        "tags": ["casual"]
    },

    # Cross-trainer
    {
        "name": "CrossFit Trainer",
        "description": "Stable cross-trainer shoe engineered for gym workouts, short sprints, and lateral movements; flexible yet supportive.",
        "features": ["cross-train","stable","gym"],
        "category": "shoes",
        "use_cases": ["gym","cross-training"],
        "tags": ["training","gym"]
    },

    # Cleats
    {
        "name": "Pro Soccer Cleats",
        "description": "Low-profile football/soccer cleats with studded outsole; optimized for grip on grass and agility.",
        "features": ["cleats","studs","agility"],
        "category": "shoes",
        "use_cases": ["soccer","football"],
        "tags": ["sports","cleats"]
    }
]

# ---------- Create 'canonical_text' to improve embedding quality for better scoring ----------
for p in products:
    # join features and others into one rich text blob
    features = ", ".join(p["features"])
    uses = ", ".join(p["use_cases"])
    tags = ", ".join(p["tags"])
    canonical = f"{p['name']}. {p['description']}. Features: {features}. Use cases: {uses}. Tags: {tags}."
    p["canonical_text"] = canonical

# ---------- Embed canonical_text----------
print("Embedding items...")
for p in products:
    p["embedding"] = embed_text(p["canonical_text"])

# ---------- Insert into MongoDB ----------
try:
    # Filter out any products with failed embeddings
    valid_products = [p for p in products if p.get("embedding") is not None]
    if not valid_products:
        print("❌ No valid products to insert (embedding generation failed)")
        sys.exit(1)
    
    result = collection.insert_many(valid_products)
    print(f"✅ Inserted {len(result.inserted_ids)} documents into MongoDB.")
    
    # Verify the vector index exists
    try:
        indexes = collection.list_search_indexes()
        index_names = [idx['name'] for idx in indexes]
        if config['VECTOR_INDEX_NAME'] not in index_names:
            print(f"⚠️  Vector index '{config['VECTOR_INDEX_NAME']}' not found!")
            print("💡 Create a vector search index in MongoDB Atlas with:")
            print(f"   - Index name: {config['VECTOR_INDEX_NAME']}")
            print("   - Field path: embedding")
            print(f"   - Dimensions: 768 (for {config['MODEL_NAME']})")
            print("   - Similarity: cosine")
            print("   - Add filter fields: category, features, tags")
        else:
            print(f"✅ Vector index '{config['VECTOR_INDEX_NAME']}' found.")
            print("💡 If filtering fails, add 'category' as a filter field in your index.")
    except Exception as e:
        print(f"⚠️  Could not verify vector index: {e}")
        
except Exception as e:
    print(f"❌ Error inserting documents: {e}")
    sys.exit(1)

# Step 5: Perform your first vector search
query_text = "25k long running best shoes"
query_embedding = embed_text(query_text)

pipeline = [
    {
        "$vectorSearch": {
            "index": config['VECTOR_INDEX_NAME'],  # Use the vector search index you created
            "path": "embedding",
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": 3
        }
    },
    {
        "$project": {
            "name": 1,
            "description":1,
            "score": {"$meta": "vectorSearchScore"}
        }
    }
]

results = collection.aggregate(pipeline)

print(f"\nSearch results for: '{query_text}'\n")
for r in results:
    print(f"- {r['name']} (score: {r['score']:.4f})")
    print(f"  {r['description'][:100]}...")
    print()

# Step 6: Advanced Search Features
print("=" * 60)
print("ADVANCED SEARCH EXAMPLES")
print("=" * 60)

# 6a. Filtering by category
def vector_search_with_filter(query_text, category_filter=None, limit=3):
    query_embedding = embed_text(query_text)
    
    # Base vector search stage
    vector_stage = {
        "$vectorSearch": {
            "index": config['VECTOR_INDEX_NAME'],
            "path": "embedding", 
            "queryVector": query_embedding,
            "numCandidates": 100,
            "limit": limit if not category_filter else limit * 3  # Get more if filtering
        }
    }
    
    # Try vector search with filter first, fallback to post-filter if needed
    try:
        if category_filter:
            vector_stage["$vectorSearch"]["filter"] = {"category": {"$eq": category_filter}}
        
        pipeline = [
            vector_stage,
            {
                "$project": {
                    "name": 1,
                    "description": 1,
                    "category": 1,
                    "features": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        if category_filter:
            pipeline.insert(-1, {"$limit": limit})
        
        return list(collection.aggregate(pipeline))
        
    except Exception as e:
        if "needs to be indexed as filter" in str(e) and category_filter:
            print(f"⚠️  Filter not supported in index, using post-filtering...")
            # Fallback: do vector search then filter results
            vector_stage["$vectorSearch"].pop("filter", None)  # Remove filter
            pipeline = [
                vector_stage,
                {"$match": {"category": category_filter}},  # Post-filter
                {
                    "$project": {
                        "name": 1,
                        "description": 1,
                        "category": 1,
                        "features": 1,
                        "score": {"$meta": "vectorSearchScore"}
                    }
                },
                {"$limit": limit}
            ]
            return list(collection.aggregate(pipeline))
        else:
            raise e

# Example 1: Filtered search - only shoes
print("\n1. FILTERED SEARCH (shoes only):")
filtered_results = vector_search_with_filter("comfortable running", "shoes")
for r in filtered_results:
    print(f"- {r['name']} | {r['category']} (score: {r['score']:.4f})")

# 6b. Hybrid search (combine vector + text search)
def hybrid_search(query_text, text_search_term=None, limit=3):
    query_embedding = embed_text(query_text)
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": config['VECTOR_INDEX_NAME'],
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": 20  # Get more candidates for hybrid scoring
            }
        }
    ]
    
    # Add text search scoring if specified
    if text_search_term:
        pipeline.extend([
            {
                "$addFields": {
                    "vectorScore": {"$meta": "vectorSearchScore"},
                    "textScore": {
                        "$cond": {
                            "if": {"$regexMatch": {"input": "$description", "regex": text_search_term, "options": "i"}},
                            "then": 0.5,  # Boost for text match
                            "else": 0
                        }
                    }
                }
            },
            {
                "$addFields": {
                    "hybridScore": {"$add": ["$vectorScore", "$textScore"]}
                }
            },
            {"$sort": {"hybridScore": -1}}
        ])
    
    pipeline.extend([
        {"$limit": limit},
        {
            "$project": {
                "name": 1,
                "description": 1,
                "category": 1,
                "features": 1,
                "vectorScore": {"$ifNull": ["$vectorScore", {"$meta": "vectorSearchScore"}]},
                "textScore": {"$ifNull": ["$textScore", 0]},
                "hybridScore": {"$ifNull": ["$hybridScore", {"$meta": "vectorSearchScore"}]}
            }
        }
    ])
    
    return list(collection.aggregate(pipeline))

# Example 2: Hybrid search
print("\n2. HYBRID SEARCH (vector + text 'marathon'):")
hybrid_results = hybrid_search("long distance running shoes", "marathon")
for r in hybrid_results:
    v_score = r.get('vectorScore', 0)
    t_score = r.get('textScore', 0) 
    h_score = r.get('hybridScore', 0)
    print(f"- {r['name']} (vector: {v_score:.3f}, text: {t_score:.3f}, hybrid: {h_score:.3f})")

# 6c. Multiple search scenarios
search_scenarios = [
    ("marathon running shoes", "Long distance running"),
    ("trail hiking boots", "Outdoor adventures"),
    ("office professional shoes", "Business attire"),
    ("gym workout footwear", "Fitness training"),
    ("casual everyday sneakers", "Daily wear")
]

print("\n3. MULTIPLE SEARCH SCENARIOS:")
for query, description in search_scenarios:
    print(f"\n{description}: '{query}'")
    results = vector_search_with_filter(query, limit=2)
    for r in results:
        print(f"  → {r['name']} (score: {r['score']:.3f})")

# 6d. Feature-based search
def search_by_features(desired_features, limit=3):
    # Create query from features
    feature_query = " ".join(desired_features)
    query_embedding = embed_text(feature_query)
    
    pipeline = [
        {
            "$vectorSearch": {
                "index": config['VECTOR_INDEX_NAME'],
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": 100,
                "limit": limit
            }
        },
        {
            "$addFields": {
                "matchingFeatures": {
                    "$size": {
                        "$setIntersection": ["$features", desired_features]
                    }
                }
            }
        },
        {
            "$project": {
                "name": 1,
                "features": 1,
                "matchingFeatures": 1,
                "score": {"$meta": "vectorSearchScore"}
            }
        }
    ]
    
    return list(collection.aggregate(pipeline))

print("\n4. FEATURE-BASED SEARCH:")
desired_features = ["breathable", "cushioning", "lightweight"]
feature_results = search_by_features(desired_features)
for r in feature_results:
    print(f"- {r['name']} (score: {r['score']:.3f})")
    print(f"  Features: {r['features']}")
    print(f"  Matching: {r['matchingFeatures']}/{len(desired_features)}")
    print()

# Step 7: Interactive Search Interface
print("=" * 60)
print("INTERACTIVE SEARCH INTERFACE")
print("=" * 60)

def interactive_search():
    """Interactive search interface with multiple options"""
    
    print("\nVector Search Interface")
    print("Commands:")
    print("  'search <query>' - Basic vector search")
    print("  'filter <query> <category>' - Search with category filter")
    print("  'hybrid <query> <keyword>' - Hybrid vector + text search")
    print("  'features <feature1,feature2,...>' - Search by features")
    print("  'help' - Show this help")
    print("  'quit' - Exit")
    print()
    
    while True:
        try:
            user_input = input("🔍 Enter command: ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye! 👋")
                break
                
            if user_input.lower() == 'help':
                print("\nCommands:")
                print("  search running shoes")
                print("  filter comfortable shoes")
                print("  hybrid running marathon")
                print("  features breathable,cushioning,lightweight")
                continue
            
            parts = user_input.split(' ', 2)
            command = parts[0].lower()
            
            if command == 'search' and len(parts) >= 2:
                query = ' '.join(parts[1:])
                print(f"\n🔍 Searching for: '{query}'")
                results = vector_search_with_filter(query, limit=5)
                display_search_results(results)
                
            elif command == 'filter' and len(parts) >= 3:
                query = parts[1]
                category = parts[2]
                print(f"\n🔍 Searching '{query}' in category '{category}'")
                results = vector_search_with_filter(query, category, limit=5)
                display_search_results(results)
                
            elif command == 'hybrid' and len(parts) >= 3:
                query = parts[1]
                keyword = parts[2]
                print(f"\n🔍 Hybrid search: '{query}' + keyword '{keyword}'")
                results = hybrid_search(query, keyword, limit=5)
                display_hybrid_results(results)
                
            elif command == 'features' and len(parts) >= 2:
                features_str = parts[1]
                features = [f.strip() for f in features_str.split(',')]
                print(f"\n🔍 Searching by features: {features}")
                results = search_by_features(features, limit=5)
                display_feature_results(results, features)
                
            else:
                print("❌ Invalid command. Type 'help' for usage.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def display_search_results(results):
    """Display basic search results"""
    if not results:
        print("No results found.")
        return
        
    print(f"\nFound {len(results)} results:")
    print("-" * 50)
    for i, r in enumerate(results, 1):
        print(f"{i}. {r['name']} (score: {r['score']:.3f})")
        print(f"   Category: {r.get('category', 'N/A')}")
        print(f"   Description: {r['description'][:80]}...")
        if 'features' in r:
            print(f"   Features: {', '.join(r['features'][:3])}...")
        print()

def display_hybrid_results(results):
    """Display hybrid search results with scores"""
    if not results:
        print("No results found.")
        return
        
    print(f"\nFound {len(results)} results:")
    print("-" * 50)
    for i, r in enumerate(results, 1):
        v_score = r.get('vectorScore', 0)
        t_score = r.get('textScore', 0)
        h_score = r.get('hybridScore', 0)
        print(f"{i}. {r['name']}")
        print(f"   Scores - Vector: {v_score:.3f}, Text: {t_score:.3f}, Total: {h_score:.3f}")
        print(f"   Description: {r['description'][:80]}...")
        print()

def display_feature_results(results, desired_features):
    """Display feature-based search results"""
    if not results:
        print("No results found.")
        return
        
    print(f"\nFound {len(results)} results:")
    print("-" * 50)
    for i, r in enumerate(results, 1):
        matching = r.get('matchingFeatures', 0)
        print(f"{i}. {r['name']} (score: {r['score']:.3f})")
        print(f"   Feature match: {matching}/{len(desired_features)}")
        print(f"   All features: {', '.join(r.get('features', []))}")
        print()

# Step 9: Tutorial Summary and Next Steps
print("=" * 60)
print("TUTORIAL COMPLETE! 🎉")
print("=" * 60)

print("\n✅ What you've built:")
print("   • MongoDB Atlas vector search with embeddings")
print("   • Advanced search with filtering and hybrid search")
print("   • Interactive search interface")
print("   • Error handling and configuration management")

print("\n🔧 To get started:")
print("   1. Replace <db_password> in your MongoDB URI with your actual password")
print("   2. Create a vector search index in MongoDB Atlas:")
print(f"      - Index name: {config['VECTOR_INDEX_NAME']}")
print("      - Field path: embedding") 
print(f"      - Dimensions: 768 (for {config['MODEL_NAME']})")
print("      - Similarity: cosine")
print("   3. Run the script again")

print("\n🚀 Advanced features you can explore:")
print("   • Add more sophisticated filtering")
print("   • Implement semantic similarity thresholds")
print("   • Add batch processing for large datasets")
print("   • Create a web interface with Flask/FastAPI")
print("   • Add real-time search suggestions")

print(f"\n📊 Current configuration:")
print(f"   Database: {config['DATABASE_NAME']}")
print(f"   Collection: {config['COLLECTION_NAME']}")
print(f"   Model: {config['MODEL_NAME']}")
print(f"   Vector Index: {config['VECTOR_INDEX_NAME']}")

# Start interactive mode if run directly
if __name__ == "__main__":
    try:
        # Test if we can actually perform a search
        test_embedding = embed_text("test")
        if test_embedding:
            print("\n🎯 Ready for interactive search!")
            interactive_search()
        else:
            print("\n❌ Embedding generation failed. Check model loading.")
    except Exception as e:
        print(f"\n❌ Error in interactive mode: {e}")
        print("💡 Fix your MongoDB connection first, then try again.")
