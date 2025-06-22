# Migration Guide: SQLite to Qdrant-Only Architecture

## 🎯 Migration Overview

This guide outlines the step-by-step process to migrate from the current SQLite + Qdrant dual-database architecture to a **Qdrant-only** approach where all protocol metadata and vector embeddings are stored in Qdrant.

## 📋 Pre-Migration Checklist

- [ ] Backup any existing protocol data
- [ ] Ensure Qdrant service is running and accessible
- [ ] Review current API endpoints and their usage
- [ ] Identify all SQLite-dependent tests
- [ ] Plan for frontend dropdown population changes

## 🔄 Migration Steps

### Phase 1: Enhance Qdrant Service

#### 1.1 Update Qdrant Service for Metadata Storage

**File: `backend/app/services/qdrant_service.py`**

Add these new methods to handle protocol metadata:

```python
def create_protocol_collection(
    self, 
    study_acronym: str, 
    protocol_title: str,
    file_path: Optional[str] = None
) -> str:
    """Create a new collection for a protocol with metadata."""
    collection_name = self.generate_collection_name(study_acronym)
    
    # Create collection
    self.client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
    )
    
    return collection_name

def store_protocol_with_metadata(
    self,
    collection_name: str,
    chunks: List[str],
    embeddings: List[List[float]],
    protocol_metadata: dict
) -> bool:
    """Store document chunks with protocol metadata."""
    points = []
    
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        payload = {
            # Protocol metadata (same for all chunks)
            **protocol_metadata,
            
            # Chunk-specific metadata
            "chunk_index": i,
            "chunk_text": chunk,
            "chunk_size": len(chunk),
            "embedding_model": "text-embedding-ada-002",
            "processing_version": "1.0",
            "last_updated": datetime.now().isoformat()
        }
        
        points.append(PointStruct(
            id=f"{collection_name}_{i}",
            vector=embedding,
            payload=payload
        ))
    
    self.client.upsert(
        collection_name=collection_name,
        points=points
    )
    
    return True

def list_all_protocols(self) -> List[dict]:
    """List all protocols by querying collection metadata."""
    collections = self.client.get_collections()
    protocols = []
    
    for collection in collections.collections:
        try:
            # Get first point to extract protocol metadata
            result = self.client.scroll(
                collection_name=collection.name,
                limit=1,
                with_payload=True
            )
            
            if result[0]:  # If points exist
                payload = result[0][0].payload
                protocols.append({
                    "protocol_id": payload.get("protocol_id"),
                    "study_acronym": payload.get("study_acronym"),
                    "protocol_title": payload.get("protocol_title"),
                    "collection_name": collection.name,
                    "upload_date": payload.get("upload_date"),
                    "status": payload.get("status", "processing"),
                    "file_path": payload.get("file_path"),
                    "created_at": payload.get("created_at")
                })
        except Exception as e:
            logger.warning(f"Could not retrieve metadata for collection {collection.name}: {e}")
            continue
    
    return protocols

def get_protocol_by_collection(self, collection_name: str) -> Optional[dict]:
    """Get protocol metadata from collection."""
    try:
        result = self.client.scroll(
            collection_name=collection_name,
            limit=1,
            with_payload=True
        )
        
        if result[0]:
            return result[0][0].payload
        return None
    except Exception as e:
        logger.error(f"Error retrieving protocol from collection {collection_name}: {e}")
        return None

def update_protocol_status(self, collection_name: str, status: str) -> bool:
    """Update status for all points in a collection."""
    try:
        self.client.set_payload(
            collection_name=collection_name,
            payload={"status": status, "last_updated": datetime.now().isoformat()},
            points=None  # Updates all points
        )
        return True
    except Exception as e:
        logger.error(f"Error updating status for collection {collection_name}: {e}")
        return False

def delete_protocol(self, collection_name: str) -> bool:
    """Delete entire protocol collection."""
    try:
        self.client.delete_collection(collection_name)
        return True
    except Exception as e:
        logger.error(f"Error deleting collection {collection_name}: {e}")
        return False
```

#### 1.2 Update Collection Name Generation

Move the collection name generation logic to Qdrant service:

```python
def generate_collection_name(self, study_acronym: str) -> str:
    """Generate unique collection name for protocol."""
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    clean_acronym = "".join(c for c in study_acronym if c.isalnum() or c == "_").lower()
    
    if now.microsecond > 0:
        microseconds = f"{now.microsecond:06d}"
        return f"{clean_acronym}_{timestamp}_{microseconds}"
    else:
        return f"{clean_acronym}_{timestamp}"
```

### Phase 2: Update API Endpoints

#### 2.1 Modify Protocol API Routes

**File: `backend/app/api/protocols.py`**

Replace SQLite database calls with Qdrant service calls:

```python
from ..services.qdrant_service import QdrantService

# Initialize Qdrant service
qdrant_service = QdrantService()

@router.post("/", response_model=ProtocolResponse, status_code=status.HTTP_201_CREATED)
async def create_new_protocol(protocol: ProtocolCreate) -> ProtocolResponse:
    """Create a new protocol using Qdrant storage."""
    try:
        # Create collection and get collection name
        collection_name = qdrant_service.create_protocol_collection(
            study_acronym=protocol.study_acronym,
            protocol_title=protocol.protocol_title,
            file_path=protocol.file_path
        )
        
        # For now, create a minimal entry (actual document processing happens separately)
        protocol_metadata = {
            "protocol_id": f"proto_{int(time.time())}",
            "study_acronym": protocol.study_acronym,
            "protocol_title": protocol.protocol_title,
            "collection_name": collection_name,
            "upload_date": datetime.now().isoformat(),
            "status": "processing",
            "file_path": protocol.file_path,
            "created_at": datetime.now().isoformat()
        }
        
        # Store initial metadata (will be updated when document is processed)
        qdrant_service.store_protocol_with_metadata(
            collection_name=collection_name,
            chunks=["Initial protocol entry"],
            embeddings=[[0.0] * 1536],  # Placeholder embedding
            protocol_metadata=protocol_metadata
        )
        
        return ProtocolResponse(**protocol_metadata)
        
    except Exception as e:
        logger.error(f"Error creating protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create protocol"
        )

@router.get("/", response_model=List[ProtocolResponse])
async def list_protocols(
    status_filter: Optional[str] = Query(None, description="Filter protocols by status")
) -> List[ProtocolResponse]:
    """List all protocols from Qdrant collections."""
    try:
        protocols = qdrant_service.list_all_protocols()
        
        if status_filter:
            protocols = [p for p in protocols if p.get("status") == status_filter]
        
        return [ProtocolResponse(**protocol) for protocol in protocols]
        
    except Exception as e:
        logger.error(f"Error listing protocols: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocols"
        )

@router.get("/collection/{collection_name}", response_model=ProtocolResponse)
async def get_protocol_by_collection(collection_name: str) -> ProtocolResponse:
    """Get protocol by collection name."""
    try:
        protocol_data = qdrant_service.get_protocol_by_collection(collection_name)
        
        if not protocol_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Protocol with collection {collection_name} not found"
            )
        
        return ProtocolResponse(**protocol_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving protocol: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve protocol"
        )
```

### Phase 3: Remove SQLite Dependencies

#### 3.1 Files to Remove/Update

**Remove these files:**
- `backend/app/database.py`
- `backend/protocols.db`

**Update these files:**
- Remove SQLite imports from all API files
- Update `backend/app/main.py` to remove database initialization
- Update all test files to use Qdrant instead of SQLite

#### 3.2 Update Main Application

**File: `backend/app/main.py`**

```python
# Remove these lines:
# from .database import DatabaseError, init_database

# Remove database initialization:
# try:
#     init_database()
#     logger.info("Database initialized successfully")
# except DatabaseError as e:
#     logger.error(f"Failed to initialize database: {e}")
#     raise

# Replace with Qdrant initialization if needed:
try:
    # Qdrant client initialization happens in service
    logger.info("Application initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    raise
```

### Phase 4: Update Tests

#### 4.1 Create New Qdrant Test Fixtures

**File: `backend/tests/conftest.py`**

```python
@pytest.fixture
def qdrant_service():
    """Create a test Qdrant service with in-memory client."""
    from app.services.qdrant_service import QdrantService
    
    # Use in-memory Qdrant for testing
    service = QdrantService(client=QdrantClient(":memory:"))
    return service

@pytest.fixture
def sample_protocol_data():
    """Sample protocol data for testing."""
    return {
        "study_acronym": "TEST-001",
        "protocol_title": "Test Protocol for Unit Testing",
        "file_path": "/test/protocol.pdf"
    }
```

#### 4.2 Update Test Files

Replace SQLite-based tests with Qdrant-based tests:

**Example: `backend/tests/test_qdrant_protocols.py`**

```python
def test_create_protocol_collection(qdrant_service, sample_protocol_data):
    """Test creating a protocol collection."""
    collection_name = qdrant_service.create_protocol_collection(
        study_acronym=sample_protocol_data["study_acronym"],
        protocol_title=sample_protocol_data["protocol_title"],
        file_path=sample_protocol_data["file_path"]
    )
    
    assert collection_name.startswith("test001_")
    
    # Verify collection exists
    collections = qdrant_service.client.get_collections()
    collection_names = [c.name for c in collections.collections]
    assert collection_name in collection_names

def test_list_protocols(qdrant_service, sample_protocol_data):
    """Test listing all protocols."""
    # Create test protocol
    collection_name = qdrant_service.create_protocol_collection(**sample_protocol_data)
    
    # Store metadata
    protocol_metadata = {
        "protocol_id": "test_001",
        "study_acronym": sample_protocol_data["study_acronym"],
        "protocol_title": sample_protocol_data["protocol_title"],
        "collection_name": collection_name,
        "status": "processing"
    }
    
    qdrant_service.store_protocol_with_metadata(
        collection_name=collection_name,
        chunks=["test chunk"],
        embeddings=[[0.1] * 1536],
        protocol_metadata=protocol_metadata
    )
    
    # List protocols
    protocols = qdrant_service.list_all_protocols()
    
    assert len(protocols) == 1
    assert protocols[0]["study_acronym"] == "TEST-001"
```

### Phase 5: Update Frontend Integration

#### 5.1 Update API Calls

The frontend API calls should remain largely the same, but ensure they're using the correct endpoints:

```typescript
// Frontend will continue to call the same endpoints
// GET /protocols/ - now returns data from Qdrant collections
// POST /protocols/ - now creates Qdrant collections
// etc.
```

## 🧪 Testing the Migration

### 1. Unit Tests
```bash
# Run Qdrant service tests
npm run test:backend -- tests/test_qdrant_service.py

# Run API tests
npm run test:backend -- tests/test_api_protocols.py
```

### 2. Integration Tests
```bash
# Test full workflow
npm run test:backend -- tests/test_integration.py
```

### 3. Manual Testing
1. Start the application
2. Upload a protocol PDF
3. Verify it appears in the dropdown
4. Generate a document
5. Verify all operations work without SQLite

## 🚨 Rollback Plan

If issues arise during migration:

1. **Keep SQLite code in a backup branch**
2. **Restore `app/database.py` from backup**
3. **Restore SQLite-based API endpoints**
4. **Switch back to SQLite-based tests**

## ✅ Post-Migration Verification

- [ ] All tests pass
- [ ] Frontend dropdown populates correctly
- [ ] Protocol upload works
- [ ] Document generation works
- [ ] No SQLite references remain in code
- [ ] Performance is acceptable
- [ ] Error handling works correctly

## 📚 Additional Resources

- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Qdrant Python Client](https://github.com/qdrant/qdrant-client)
- [Vector Database Best Practices](https://qdrant.tech/articles/vector-database-best-practices/)

This migration will result in a cleaner, more maintainable architecture with Qdrant as the single source of truth for all data storage needs. 