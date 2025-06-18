# Database Architecture: Qdrant-Only Storage Strategy

## 🎯 Overview

The Clinical Trial Accelerator uses **Qdrant as the single source of truth** for all data storage needs. This unified approach eliminates the complexity of managing multiple databases while providing both metadata storage and vector search capabilities.

## 🏗️ Architecture Principles

### Single Database Philosophy
- **No SQLite, PostgreSQL, or other traditional databases**
- **Qdrant handles both metadata and vector embeddings**
- **Simplified data flow and reduced infrastructure complexity**
- **Consistent query interface for all data operations**

### Data Storage Strategy
```
PDF Upload → Text Extraction → Embedding Generation → Qdrant Storage
                                                    ↓
                                            Metadata + Vectors
                                                    ↓
                                            Frontend Queries
```

## 📊 Data Structure in Qdrant

### Collection Organization
Each uploaded protocol creates a **unique collection** in Qdrant with the naming pattern:
```
{study_acronym}_{timestamp}_{microseconds}
```

### Metadata Schema
Each vector point in Qdrant includes comprehensive metadata:

```json
{
  "id": "unique_point_id",
  "vector": [0.1, 0.2, ...],  // Document embeddings
  "payload": {
    // Protocol Metadata
    "protocol_id": "unique_protocol_identifier",
    "study_acronym": "STUDY-123",
    "protocol_title": "Phase III Clinical Trial for...",
    "collection_name": "study123_20241215_143022_123456",
    "upload_date": "2024-12-15T14:30:22Z",
    "status": "processed",
    "file_path": "/uploads/protocol.pdf",
    "created_at": "2024-12-15T14:30:22Z",
    
    // Document Chunk Metadata
    "chunk_index": 0,
    "chunk_text": "This protocol describes...",
    "page_number": 1,
    "section_type": "introduction",
    "chunk_size": 512,
    
    // Processing Metadata
    "embedding_model": "text-embedding-ada-002",
    "processing_version": "1.0",
    "last_updated": "2024-12-15T14:30:22Z"
  }
}
```

## 🔄 Core Operations

### 1. Protocol Upload & Storage
```python
# Workflow:
1. Upload PDF → Extract text → Chunk content
2. Generate embeddings for each chunk
3. Create new Qdrant collection
4. Store vectors with comprehensive metadata
5. No separate database writes needed
```

### 2. Frontend Dropdown Population
```python
# Query all collections to populate protocol dropdown:
1. List all Qdrant collections
2. Extract metadata from first point in each collection
3. Return: study_acronym, protocol_title, status, upload_date
4. Frontend renders dropdown options
```

### 3. Protocol Retrieval
```python
# Get protocol details:
1. Query specific collection by collection_name
2. Retrieve metadata from any point (all have same protocol metadata)
3. Return protocol information for document generation
```

### 4. Document Generation (RAG)
```python
# Semantic search for document generation:
1. Generate query embedding
2. Search relevant collection for similar content
3. Retrieve top-k chunks with metadata
4. Use chunks + metadata for LangGraph document generation
```

## 🛠️ Implementation Details

### Collection Management
- **One collection per protocol** for data isolation
- **Collection names are unique** using timestamp + microseconds
- **Metadata consistency** across all points in a collection
- **Easy cleanup** by dropping entire collections

### Query Patterns
```python
# List all protocols (for dropdown)
collections = qdrant_client.get_collections()
protocols = []
for collection in collections:
    # Get metadata from first point
    points = qdrant_client.scroll(collection.name, limit=1)
    if points[0]:
        metadata = points[0][0].payload
        protocols.append({
            "study_acronym": metadata["study_acronym"],
            "protocol_title": metadata["protocol_title"],
            "status": metadata["status"],
            "collection_name": collection.name
        })

# Search within protocol for RAG
results = qdrant_client.search(
    collection_name=collection_name,
    query_vector=query_embedding,
    limit=10,
    with_payload=True
)
```

### Status Management
```python
# Update protocol status across all points in collection
qdrant_client.set_payload(
    collection_name=collection_name,
    payload={"status": "processed"},
    points=None  # Updates all points
)
```

## 🎯 Benefits of Qdrant-Only Approach

### Simplified Architecture
- ✅ **Single database to manage**
- ✅ **No data synchronization issues**
- ✅ **Unified query interface**
- ✅ **Reduced infrastructure complexity**

### Performance Advantages
- ✅ **Fast vector similarity search**
- ✅ **Efficient metadata filtering**
- ✅ **Horizontal scaling capabilities**
- ✅ **Memory-efficient operations**

### Development Benefits
- ✅ **Fewer database connections**
- ✅ **Simplified testing setup**
- ✅ **Consistent data access patterns**
- ✅ **Reduced code complexity**

## 🚀 Migration Strategy

### Phase 1: Update Backend Services
1. Modify `app/services/qdrant_service.py` to handle metadata storage
2. Update protocol creation to store metadata in Qdrant
3. Implement collection listing for dropdown population
4. Add status update operations

### Phase 2: Remove SQLite Dependencies
1. Remove `app/database.py`
2. Update imports across the codebase
3. Remove SQLite-related tests
4. Update API endpoints to use Qdrant service

### Phase 3: Update Frontend Integration
1. Modify API calls to use new Qdrant-based endpoints
2. Update dropdown population logic
3. Test end-to-end workflow

## 🧪 Testing Strategy

### Unit Tests
- Qdrant service operations
- Metadata storage and retrieval
- Collection management
- Status updates

### Integration Tests
- Full protocol upload workflow
- Dropdown population from Qdrant
- Document generation with RAG
- Error handling scenarios

### Performance Tests
- Large protocol handling
- Multiple collection queries
- Vector search performance
- Memory usage optimization

## 📝 API Endpoints (Updated)

```python
# Protocol management via Qdrant
POST   /protocols/           # Create protocol + Qdrant collection
GET    /protocols/           # List all protocols from collections
GET    /protocols/{id}       # Get protocol from collection metadata
PATCH  /protocols/{id}/status # Update status in collection
DELETE /protocols/{id}       # Delete entire collection
```

## 🔧 Configuration

### Environment Variables
```bash
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_api_key_here
OPENAI_API_KEY=your_openai_key_here
EMBEDDING_MODEL=text-embedding-ada-002
```

### Qdrant Setup
```python
# Development (memory-based)
qdrant_client = QdrantClient(":memory:")

# Production (cloud/server)
qdrant_client = QdrantClient(
    url=os.getenv("QDRANT_URL"),
    api_key=os.getenv("QDRANT_API_KEY")
)
```

This architecture provides a clean, scalable, and maintainable solution that leverages Qdrant's capabilities for both metadata storage and vector operations while eliminating the complexity of managing multiple database systems. 