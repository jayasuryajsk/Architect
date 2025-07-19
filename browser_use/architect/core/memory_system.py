"""
Advanced Memory System for Continuous Learning and Evolution
"""

import json
import os
import sqlite3
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import pickle
import logging

logger = logging.getLogger(__name__)


class PersistentMemory:
    """SQLite-based persistent memory for tools, patterns, and knowledge"""
    
    def __init__(self, db_path: str = "architect_memory.db"):
        self.db_path = db_path
        self._init_database()
        
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tools table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tools (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    code TEXT NOT NULL,
                    spec TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP,
                    success_count INTEGER DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    avg_execution_time REAL DEFAULT 0,
                    performance_score REAL DEFAULT 0.5,
                    tags TEXT,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Tool evolution history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tool_evolution (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_id TEXT,
                    old_version INTEGER,
                    new_version INTEGER,
                    old_code TEXT,
                    new_code TEXT,
                    reason TEXT,
                    improvements TEXT,
                    evolved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tool_id) REFERENCES tools(id)
                )
            ''')
            
            # Execution history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS executions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_id TEXT,
                    task TEXT,
                    inputs TEXT,
                    outputs TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    error_message TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tool_id) REFERENCES tools(id)
                )
            ''')
            
            # Knowledge patterns
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_type TEXT,
                    pattern_data TEXT,
                    success_rate REAL,
                    usage_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Task memory
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_hash TEXT UNIQUE,
                    task_description TEXT,
                    solution_approach TEXT,
                    tools_used TEXT,
                    success BOOLEAN,
                    execution_time REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    async def store_tool(self, tool: Dict[str, Any]) -> str:
        """Store a tool in memory"""
        tool_id = self._generate_tool_id(tool)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if tool exists
            cursor.execute('SELECT version FROM tools WHERE id = ?', (tool_id,))
            existing = cursor.fetchone()
            
            if existing:
                # Update existing tool
                new_version = existing[0] + 1
                cursor.execute('''
                    UPDATE tools 
                    SET code = ?, spec = ?, version = ?, last_used = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (tool['code'], json.dumps(tool['spec']), new_version, tool_id))
            else:
                # Insert new tool
                cursor.execute('''
                    INSERT INTO tools (id, name, code, spec, tags)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    tool_id,
                    tool['name'],
                    tool['code'],
                    json.dumps(tool['spec']),
                    json.dumps(tool.get('tags', []))
                ))
            
            conn.commit()
            
        logger.info(f"💾 Stored tool: {tool['name']} (ID: {tool_id})")
        return tool_id
    
    async def get_tool(self, tool_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a tool from memory"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT name, code, spec, version, performance_score
                FROM tools
                WHERE id = ? AND is_active = 1
            ''', (tool_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': tool_id,
                    'name': row[0],
                    'code': row[1],
                    'spec': json.loads(row[2]),
                    'version': row[3],
                    'performance_score': row[4]
                }
        
        return None
    
    async def find_similar_tools(self, task: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find tools similar to a given task"""
        task_embedding = self._simple_embedding(task)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, name, code, spec, performance_score
                FROM tools
                WHERE is_active = 1
                ORDER BY performance_score DESC
                LIMIT ?
            ''', (limit * 2,))  # Get more to filter
            
            tools = []
            for row in cursor.fetchall():
                spec = json.loads(row[3])
                similarity = self._calculate_similarity(
                    task_embedding,
                    self._simple_embedding(spec.get('purpose', ''))
                )
                
                if similarity > 0.3:  # Threshold
                    tools.append({
                        'id': row[0],
                        'name': row[1],
                        'code': row[2],
                        'spec': spec,
                        'performance_score': row[4],
                        'similarity': similarity
                    })
            
            # Sort by similarity and return top matches
            tools.sort(key=lambda x: x['similarity'], reverse=True)
            return tools[:limit]
    
    async def record_execution(self, tool_id: str, task: str, inputs: Dict, 
                               outputs: Dict, success: bool, execution_time: float,
                               error: Optional[str] = None):
        """Record tool execution for learning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Record execution
            cursor.execute('''
                INSERT INTO executions (tool_id, task, inputs, outputs, success, 
                                        execution_time, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                tool_id, task, json.dumps(inputs), json.dumps(outputs),
                success, execution_time, error
            ))
            
            # Update tool statistics
            cursor.execute('''
                UPDATE tools
                SET success_count = success_count + ?,
                    failure_count = failure_count + ?,
                    avg_execution_time = (
                        (avg_execution_time * (success_count + failure_count) + ?) /
                        (success_count + failure_count + 1)
                    ),
                    last_used = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (1 if success else 0, 0 if success else 1, execution_time, tool_id))
            
            # Recalculate performance score
            self._update_performance_score(cursor, tool_id)
            
            conn.commit()
    
    async def get_tool_performance(self, tool_id: str) -> Dict[str, Any]:
        """Get performance metrics for a tool"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT success_count, failure_count, avg_execution_time, 
                       performance_score, last_used
                FROM tools
                WHERE id = ?
            ''', (tool_id,))
            
            row = cursor.fetchone()
            if row:
                total_uses = row[0] + row[1]
                return {
                    'success_rate': row[0] / total_uses if total_uses > 0 else 0,
                    'total_uses': total_uses,
                    'avg_execution_time': row[2],
                    'performance_score': row[3],
                    'last_used': row[4]
                }
        
        return {}
    
    async def evolve_tool(self, tool_id: str, new_code: str, reason: str, 
                          improvements: List[str]) -> int:
        """Record tool evolution"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current tool
            cursor.execute('SELECT code, version FROM tools WHERE id = ?', (tool_id,))
            old_code, old_version = cursor.fetchone()
            new_version = old_version + 1
            
            # Record evolution
            cursor.execute('''
                INSERT INTO tool_evolution (tool_id, old_version, new_version, 
                                            old_code, new_code, reason, improvements)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                tool_id, old_version, new_version, old_code, new_code,
                reason, json.dumps(improvements)
            ))
            
            # Update tool
            cursor.execute('''
                UPDATE tools
                SET code = ?, version = ?
                WHERE id = ?
            ''', (new_code, new_version, tool_id))
            
            conn.commit()
            
        logger.info(f"🔄 Evolved tool {tool_id} to version {new_version}")
        return new_version
    
    async def store_pattern(self, pattern_type: str, pattern_data: Dict, 
                            success_rate: float):
        """Store a successful pattern for reuse"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO patterns (pattern_type, pattern_data, success_rate)
                VALUES (?, ?, ?)
            ''', (pattern_type, json.dumps(pattern_data), success_rate))
            conn.commit()
    
    async def get_patterns(self, pattern_type: str, min_success_rate: float = 0.7) -> List[Dict]:
        """Retrieve successful patterns"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT pattern_data, success_rate, usage_count
                FROM patterns
                WHERE pattern_type = ? AND success_rate >= ?
                ORDER BY success_rate DESC, usage_count DESC
                LIMIT 10
            ''', (pattern_type, min_success_rate))
            
            patterns = []
            for row in cursor.fetchall():
                patterns.append({
                    'data': json.loads(row[0]),
                    'success_rate': row[1],
                    'usage_count': row[2]
                })
            
            return patterns
    
    async def remember_task_solution(self, task: str, solution_approach: Dict,
                                     tools_used: List[str], success: bool,
                                     execution_time: float):
        """Remember how a task was solved"""
        task_hash = self._hash_task(task)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO tasks 
                (task_hash, task_description, solution_approach, tools_used, 
                 success, execution_time)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                task_hash, task, json.dumps(solution_approach),
                json.dumps(tools_used), success, execution_time
            ))
            conn.commit()
    
    async def recall_task_solution(self, task: str) -> Optional[Dict[str, Any]]:
        """Recall how a similar task was solved"""
        # First try exact match
        task_hash = self._hash_task(task)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT solution_approach, tools_used, success, execution_time
                FROM tasks
                WHERE task_hash = ?
            ''', (task_hash,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'solution_approach': json.loads(row[0]),
                    'tools_used': json.loads(row[1]),
                    'success': row[2],
                    'execution_time': row[3]
                }
            
            # Try similar tasks
            cursor.execute('''
                SELECT task_description, solution_approach, tools_used, 
                       success, execution_time
                FROM tasks
                WHERE success = 1
                ORDER BY created_at DESC
                LIMIT 100
            ''')
            
            task_embedding = self._simple_embedding(task)
            best_match = None
            best_similarity = 0
            
            for row in cursor.fetchall():
                similarity = self._calculate_similarity(
                    task_embedding,
                    self._simple_embedding(row[0])
                )
                
                if similarity > best_similarity and similarity > 0.7:
                    best_similarity = similarity
                    best_match = {
                        'task': row[0],
                        'solution_approach': json.loads(row[1]),
                        'tools_used': json.loads(row[2]),
                        'success': row[3],
                        'execution_time': row[4],
                        'similarity': similarity
                    }
            
            return best_match
    
    async def cleanup_old_data(self, days: int = 30):
        """Clean up old execution data"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM executions
                WHERE executed_at < ?
            ''', (cutoff_date,))
            
            deleted = cursor.rowcount
            conn.commit()
            
        logger.info(f"🧹 Cleaned up {deleted} old execution records")
    
    def _generate_tool_id(self, tool: Dict) -> str:
        """Generate unique tool ID"""
        content = f"{tool['name']}_{tool.get('spec', {}).get('purpose', '')}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _hash_task(self, task: str) -> str:
        """Generate task hash"""
        return hashlib.md5(task.lower().strip().encode()).hexdigest()
    
    def _simple_embedding(self, text: str) -> Dict[str, float]:
        """Simple word-based embedding for similarity"""
        words = text.lower().split()
        embedding = defaultdict(float)
        
        for word in words:
            # Simple TF
            embedding[word] += 1.0 / len(words)
        
        return dict(embedding)
    
    def _calculate_similarity(self, embedding1: Dict, embedding2: Dict) -> float:
        """Calculate cosine similarity between embeddings"""
        if not embedding1 or not embedding2:
            return 0.0
        
        # Get all unique words
        all_words = set(embedding1.keys()) | set(embedding2.keys())
        
        # Calculate dot product and magnitudes
        dot_product = sum(
            embedding1.get(word, 0) * embedding2.get(word, 0)
            for word in all_words
        )
        
        magnitude1 = sum(v ** 2 for v in embedding1.values()) ** 0.5
        magnitude2 = sum(v ** 2 for v in embedding2.values()) ** 0.5
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _update_performance_score(self, cursor: sqlite3.Cursor, tool_id: str):
        """Update tool performance score"""
        cursor.execute('''
            SELECT success_count, failure_count, avg_execution_time,
                   created_at, last_used
            FROM tools
            WHERE id = ?
        ''', (tool_id,))
        
        row = cursor.fetchone()
        if row:
            success_count, failure_count, avg_time, created_at, last_used = row
            total_uses = success_count + failure_count
            
            if total_uses == 0:
                score = 0.5
            else:
                # Success rate (0-1)
                success_rate = success_count / total_uses
                
                # Speed score (faster is better, normalized)
                speed_score = 1.0 / (1.0 + avg_time) if avg_time > 0 else 1.0
                
                # Reliability bonus for consistent performance
                reliability = min(total_uses / 10, 1.0)  # Max at 10 uses
                
                # Recency bonus
                last_used_date = datetime.fromisoformat(last_used) if last_used else datetime.now()
                days_since_use = (datetime.now() - last_used_date).days
                recency_score = 1.0 / (1.0 + days_since_use / 7)  # Decay over weeks
                
                # Combined score
                score = (
                    0.5 * success_rate +
                    0.2 * speed_score +
                    0.2 * reliability +
                    0.1 * recency_score
                )
            
            cursor.execute('''
                UPDATE tools
                SET performance_score = ?
                WHERE id = ?
            ''', (score, tool_id))