# MongoDB Atlas Vector Search Application

A comprehensive implementation of vector search using MongoDB Atlas and Sentence Transformers, featuring advanced search capabilities, interactive CLI interface, and production-ready error handling.

## 🚀 Features

- **MongoDB Atlas Integration**: Robust connection management with authentication
- **Advanced Vector Search**: Multiple search strategies including filtering, hybrid search, and feature-based matching
- **Interactive CLI**: User-friendly command-line interface with multiple search modes
- **Production Ready**: Comprehensive error handling, configuration management, and graceful degradation
- **Sentence Transformers**: Utilizes state-of-the-art embedding models for semantic search

## 📋 Prerequisites

- Python 3.8+
- MongoDB Atlas account with a cluster
- Vector search index created in MongoDB Atlas

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd vector-search-app
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure MongoDB connection**:
   ```bash
   # Copy the environment template
   cp .env.example .env
   
   # Edit .env with your MongoDB Atlas credentials
   # Replace username:password with your actual credentials
   ```

## 🗂️ MongoDB Atlas Setup

### Create Vector Search Index

In MongoDB Atlas, create a search index with these settings:

```json
{
  "fields": [
    {
      "numDimensions": 768,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "category",
      "type": "filter"
    },
    {
      "path": "features",
      "type": "filter"
    }
  ]
}
```

**Index Configuration:**
- **Index Name**: `vector_index`
- **Database**: `vectorDemo`
- **Collection**: `items`

## 🎯 Usage

### Basic Execution
```bash
python vector_search.py
```

### Interactive Search Commands

Once the application starts, you can use these commands:

- **Basic Search**: `search running shoes`
- **Category Filter**: `filter comfortable shoes`
- **Hybrid Search**: `hybrid running marathon`
- **Feature Search**: `features breathable,cushioning,lightweight`
- **Help**: `help`
- **Exit**: `quit`

## 🔍 Search Features

### 1. **Basic Vector Search**
Semantic similarity search using sentence embeddings:
```python
search marathon running shoes
```

### 2. **Filtered Search**  
Search within specific categories:
```python
filter comfortable shoes
```

### 3. **Hybrid Search**
Combines vector similarity with keyword matching:
```python
hybrid running marathon
```

### 4. **Feature-Based Search**
Find products with specific features:
```python
features breathable,cushioning,lightweight
```

## 📁 Project Structure

```
vector-search-app/
├── vector_search.py      # Main application file
├── requirements.txt      # Python dependencies
├── README.md            # Project documentation
├── .env.example         # Environment variables template
├── .gitignore          # Git ignore rules  
└── .venv/              # Virtual environment (not tracked)
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

```bash
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=vectorDemo
COLLECTION_NAME=items
MODEL_NAME=sentence-transformers/all-mpnet-base-v2
VECTOR_INDEX_NAME=vector_index
```

## 🏗️ Architecture

### Core Components

1. **Configuration Manager**: Loads settings from environment variables
2. **MongoDB Client**: Handles database connections with error recovery
3. **Embedding Engine**: Manages SentenceTransformer models
4. **Search Engine**: Implements multiple search strategies
5. **CLI Interface**: Provides interactive user experience

### Search Pipeline

1. **Text Input** → **Embedding Generation** → **Vector Search** → **Result Formatting**
2. **Filtering**: Pre-filter or post-filter based on index capabilities
3. **Hybrid Scoring**: Combines vector similarity with text matching
4. **Feature Matching**: Semantic search enhanced with feature intersection

## 🚨 Troubleshooting

### Common Issues

1. **Authentication Failed**
   - Verify MongoDB credentials
   - Check IP whitelist in MongoDB Atlas
   - Ensure cluster is running

2. **Vector Index Not Found**
   - Create vector search index in MongoDB Atlas
   - Verify index name matches configuration
   - Check field paths and dimensions

3. **Model Loading Issues**
   - First run downloads the model (may take time)
   - Ensure stable internet connection
   - Check available disk space

4. **Filter Errors**
   - Add filter fields to vector search index
   - Application will fallback to post-filtering

## 🔧 Development

### Adding New Search Features

1. Create new search function in `vector_search.py`
2. Add command handler in `interactive_search()`
3. Implement result display function
4. Update help text

### Extending Data Schema

1. Modify product data structure
2. Update embedding generation logic
3. Adjust search pipelines
4. Update vector index configuration

## 📊 Performance Considerations

- **Embedding Model**: `all-mpnet-base-v2` (768 dimensions) for quality vs `all-MiniLM-L6-v2` (384 dimensions) for speed
- **Index Configuration**: Proper vector index setup crucial for performance
- **Batch Processing**: For large datasets, implement batch embedding generation
- **Caching**: Consider caching embeddings for frequently searched terms

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- MongoDB Atlas for vector search capabilities
- Sentence Transformers for embedding models
- Hugging Face for model hosting