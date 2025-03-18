"""
Memory System - Advanced memory storage and retrieval using ChromaDB
"""
try:
    import chromadb
    import numpy as np
    from datetime import datetime
except ImportError:
    print("Warning: Required packages not installed. Installing dependencies...")
    import subprocess
    subprocess.call(["pip", "install", "chromadb numpy"])
    import chromadb
    import numpy as np
    from datetime import datetime

class MemorySystem:
    def __init__(self, persistence_path="./memory_store"):
        self.client = chromadb.PersistentClient(path=persistence_path)
        self.episodic = self.client.get_or_create_collection("episodic_memory")
        self.semantic = self.client.get_or_create_collection("semantic_memory")
        self.procedural = self.client.get_or_create_collection("procedural_memory")
        
    def add_memory(self, memory_type, content, metadata=None):
        """Add a new memory to the appropriate collection"""
        if metadata is None:
            metadata = {}
            
        # Add timestamp
        metadata["timestamp"] = datetime.now().isoformat()
        
        # Generate embedding using the content
        collection = getattr(self, memory_type)
        collection.add(
            documents=[content],
            metadatas=[metadata],
            ids=[f"{memory_type}_{datetime.now().timestamp()}"]
        )
        
    def retrieve_relevant(self, query, memory_type=None, limit=5):
        """Retrieve memories relevant to the query"""
        results = []
        
        if memory_type:
            collections = [getattr(self, memory_type)]
        else:
            collections = [self.episodic, self.semantic, self.procedural]
            
        for collection in collections:
            response = collection.query(
                query_texts=[query],
                n_results=limit
            )
            
            results.extend(zip(response["documents"][0], response["metadatas"][0]))
            
        return results
        
    def get_memory_stats(self):
        """Get statistics about the memory collections"""
        stats = {}
        for memory_type in ["episodic", "semantic", "procedural"]:
            collection = getattr(self, memory_type)
            stats[memory_type] = collection.count()
        return stats
