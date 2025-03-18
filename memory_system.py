"""
Enhanced Memory System - Advanced memory storage and retrieval using ChromaDB
Supports various memory types, contextual retrieval, and memory summarization
"""
try:
    import chromadb
    import numpy as np
    from datetime import datetime, timedelta
    import json
    import hashlib
    import time
except ImportError:
    print("Warning: Required packages not installed. Installing dependencies...")
    import subprocess
    subprocess.call(["pip", "install", "chromadb numpy"])
    import chromadb
    import numpy as np
    from datetime import datetime, timedelta
    import json
    import hashlib
    import time

class MemorySystem:
    def __init__(self, persistence_path="./memory_store", max_memory_age_days=30):
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(path=persistence_path)
        
        # Set up memory collections
        self.episodic = self.client.get_or_create_collection("episodic_memory")
        self.semantic = self.client.get_or_create_collection("semantic_memory")
        self.procedural = self.client.get_or_create_collection("procedural_memory")
        
        # Set maximum memory age for automatic pruning
        self.max_memory_age = max_memory_age_days
        
        # Cache for frequently accessed memories
        self.memory_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        
        # Set up memory importance tracking
        self.memory_access_count = {}
        
    def _generate_memory_id(self, memory_type, content, metadata=None):
        """Generate a unique ID for a memory based on content and metadata"""
        content_str = str(content)
        metadata_str = str(metadata) if metadata else ""
        unique_str = f"{memory_type}_{content_str}_{metadata_str}_{time.time()}"
        return f"{memory_type}_{hashlib.md5(unique_str.encode()).hexdigest()}"
        
    def add_memory(self, memory_type, content, metadata=None, importance=1):
        """Add a new memory to the appropriate collection with importance rating"""
        if metadata is None:
            metadata = {}
            
        # Add timestamp and importance
        current_time = datetime.now()
        metadata["timestamp"] = current_time.isoformat()
        metadata["importance"] = importance
        metadata["access_count"] = 0
        
        # Generate unique ID
        memory_id = self._generate_memory_id(memory_type, content, metadata)
        
        # Generate embedding using the content
        collection = getattr(self, memory_type)
        
        # Make sure content is string
        if not isinstance(content, str):
            content = json.dumps(content)
            
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[memory_id]
        )
        
        # Add to cache for faster retrieval
        self.memory_cache[memory_id] = {
            "content": content,
            "metadata": metadata,
            "type": memory_type,
            "last_accessed": current_time,
            "created": current_time
        }
        
        return memory_id
        
    def retrieve_relevant(self, query, memory_type=None, limit=5, min_importance=0, include_metadata=True):
        """
        Retrieve memories relevant to the query with advanced filtering
        
        Args:
            query: The search query
            memory_type: Optional specific memory type to search (episodic, semantic, procedural)
            limit: Maximum number of results to return
            min_importance: Minimum importance rating to include
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of relevant memories with their content and metadata
        """
        results = []
        
        if memory_type:
            collections = [getattr(self, memory_type)]
        else:
            collections = [self.episodic, self.semantic, self.procedural]
            
        for collection in collections:
            response = collection.query(
                query_texts=[query],
                n_results=limit * 2  # Get more results for filtering
            )
            
            # Process each result
            for i, (doc, metadata, id) in enumerate(zip(
                response["documents"][0], 
                response["metadatas"][0],
                response["ids"][0]
            )):
                # Skip if importance is below threshold
                if metadata["importance"] < min_importance:
                    continue
                
                # Update access count and last accessed time
                metadata["access_count"] = metadata.get("access_count", 0) + 1
                metadata["last_accessed"] = datetime.now().isoformat()
                
                # Update in collection
                memory_type = self._get_memory_type_from_id(id)
                if memory_type:
                    collection = getattr(self, memory_type)
                    collection.update(
                        ids=[id],
                        metadatas=[metadata]
                    )
                
                # Update cache
                if id in self.memory_cache:
                    self.memory_cache[id]["metadata"] = metadata
                    self.memory_cache[id]["last_accessed"] = datetime.now()
                    self.cache_hits += 1
                else:
                    self.memory_cache[id] = {
                        "content": doc,
                        "metadata": metadata,
                        "type": memory_type,
                        "last_accessed": datetime.now()
                    }
                    self.cache_misses += 1
                
                # Add to results
                if include_metadata:
                    results.append((doc, metadata, id))
                else:
                    results.append(doc)
                    
                # Stop if we have enough results
                if len(results) >= limit:
                    break
            
        return results
    
    def retrieve_by_timeframe(self, start_time, end_time=None, memory_type=None, limit=20):
        """Retrieve memories within a specific timeframe"""
        if end_time is None:
            end_time = datetime.now()
            
        if isinstance(start_time, str):
            start_time = datetime.fromisoformat(start_time)
            
        if isinstance(end_time, str):
            end_time = datetime.fromisoformat(end_time)
            
        results = []
        
        if memory_type:
            collections = [getattr(self, memory_type)]
        else:
            collections = [self.episodic, self.semantic, self.procedural]
            
        for collection in collections:
            # Get all memories (could be optimized with proper filtering in ChromaDB)
            all_memories = collection.get()
            
            for i, (doc, metadata, id) in enumerate(zip(
                all_memories["documents"], 
                all_memories["metadatas"],
                all_memories["ids"]
            )):
                # Parse timestamp
                timestamp = datetime.fromisoformat(metadata["timestamp"])
                
                # Check if within timeframe
                if start_time <= timestamp <= end_time:
                    results.append((doc, metadata, id))
                    
                    # Stop if we have enough results
                    if len(results) >= limit:
                        break
                        
        # Sort by timestamp
        results.sort(key=lambda x: x[1]["timestamp"])
        
        return results
    
    def update_memory(self, memory_id, content=None, metadata=None):
        """Update an existing memory"""
        # Determine memory type
        memory_type = self._get_memory_type_from_id(memory_id)
        
        if not memory_type:
            return False
            
        collection = getattr(self, memory_type)
        
        # Get current memory
        try:
            memory = collection.get(ids=[memory_id])
        except Exception:
            return False
            
        # Update content if provided
        if content:
            collection.update(
                ids=[memory_id],
                documents=[content if isinstance(content, str) else json.dumps(content)]
            )
            
        # Update metadata if provided
        if metadata:
            # Get current metadata
            current_metadata = memory["metadatas"][0]
            
            # Update with new metadata
            current_metadata.update(metadata)
            
            # Set updated timestamp
            current_metadata["updated_at"] = datetime.now().isoformat()
            
            collection.update(
                ids=[memory_id],
                metadatas=[current_metadata]
            )
            
            # Update cache
            if memory_id in self.memory_cache:
                self.memory_cache[memory_id]["metadata"] = current_metadata
                if content:
                    self.memory_cache[memory_id]["content"] = content
                
        return True
    
    def delete_memory(self, memory_id):
        """Delete a memory by ID"""
        memory_type = self._get_memory_type_from_id(memory_id)
        
        if not memory_type:
            return False
            
        collection = getattr(self, memory_type)
        
        try:
            collection.delete(ids=[memory_id])
            
            # Remove from cache
            if memory_id in self.memory_cache:
                del self.memory_cache[memory_id]
                
            return True
        except Exception:
            return False
    
    def prune_old_memories(self, max_age_days=None):
        """Delete memories older than the specified age"""
        if max_age_days is None:
            max_age_days = self.max_memory_age
            
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        cutoff_str = cutoff_date.isoformat()
        
        pruned_count = 0
        
        for memory_type in ["episodic", "semantic", "procedural"]:
            collection = getattr(self, memory_type)
            
            # Get all memories
            all_memories = collection.get()
            
            for i, (metadata, id) in enumerate(zip(
                all_memories["metadatas"],
                all_memories["ids"]
            )):
                # Parse timestamp
                timestamp = datetime.fromisoformat(metadata["timestamp"])
                
                # Check if older than cutoff
                if timestamp < cutoff_date:
                    # Keep important memories regardless of age
                    if metadata.get("importance", 0) > 3 or metadata.get("access_count", 0) > 5:
                        continue
                        
                    # Delete memory
                    collection.delete(ids=[id])
                    
                    # Remove from cache
                    if id in self.memory_cache:
                        del self.memory_cache[id]
                        
                    pruned_count += 1
                    
        return pruned_count
    
    def summarize_memories(self, memory_type=None, timeframe_days=7, limit=50):
        """Generate a summary of recent memories"""
        start_time = datetime.now() - timedelta(days=timeframe_days)
        
        memories = self.retrieve_by_timeframe(start_time, memory_type=memory_type, limit=limit)
        
        # Group by type and category
        grouped_memories = {}
        
        for content, metadata, id in memories:
            mem_type = metadata.get("type", "general")
            
            if mem_type not in grouped_memories:
                grouped_memories[mem_type] = []
                
            grouped_memories[mem_type].append({
                "content": content,
                "timestamp": metadata.get("timestamp"),
                "importance": metadata.get("importance", 1)
            })
            
        # Create summary
        summary = {
            "period": f"Last {timeframe_days} days",
            "total_memories": len(memories),
            "memory_groups": grouped_memories
        }
        
        return summary
    
    def get_memory_stats(self):
        """Get statistics about the memory collections"""
        stats = {}
        for memory_type in ["episodic", "semantic", "procedural"]:
            collection = getattr(self, memory_type)
            count = collection.count()
            
            # Get additional stats
            if count > 0:
                all_memories = collection.get()
                
                # Calculate average importance
                importances = [m.get("importance", 1) for m in all_memories["metadatas"]]
                avg_importance = sum(importances) / len(importances) if importances else 0
                
                # Get memory categories
                categories = {}
                for metadata in all_memories["metadatas"]:
                    category = metadata.get("type", "general")
                    categories[category] = categories.get(category, 0) + 1
                
                stats[memory_type] = {
                    "count": count,
                    "avg_importance": avg_importance,
                    "categories": categories,
                    "cache_hits": self.cache_hits,
                    "cache_misses": self.cache_misses
                }
            else:
                stats[memory_type] = {"count": 0}
                
        return stats
    
    def _get_memory_type_from_id(self, memory_id):
        """Extract memory type from ID"""
        if "_" not in memory_id:
            return None
            
        memory_type = memory_id.split("_")[0]
        
        if memory_type in ["episodic", "semantic", "procedural"]:
            return memory_type
            
        return None
        
    def clear_memory_cache(self):
        """Clear the memory cache"""
        self.memory_cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
