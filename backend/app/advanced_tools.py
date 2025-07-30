import re
import json
import math
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from langchain.tools.base import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain_community.llms import Together
from vector_store import doc_metadata, hybrid_search

# Advanced Document Analysis Tool
class DocumentAnalysisTool(BaseTool):
    name: str = "document_analysis"
    description: str = "Perform advanced analysis on documents including sentiment, key themes, and statistical information."
    
    def _run(self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        try:
            # Extract analysis type from query
            analysis_type = self._determine_analysis_type(query)
            
            if analysis_type == "sentiment":
                return self._analyze_sentiment()
            elif analysis_type == "themes":
                return self._extract_themes()
            elif analysis_type == "statistics":
                return self._document_statistics()
            else:
                return self._general_analysis(query)
                
        except Exception as e:
            return f"Error in document analysis: {str(e)}"
    
    def _determine_analysis_type(self, query: str) -> str:
        query_lower = query.lower()
        if any(word in query_lower for word in ["sentiment", "mood", "tone"]):
            return "sentiment"
        elif any(word in query_lower for word in ["theme", "topic", "subject"]):
            return "themes"
        elif any(word in query_lower for word in ["statistics", "stats", "count", "number"]):
            return "statistics"
        else:
            return "general"
    
    def _analyze_sentiment(self) -> str:
        # Simple sentiment analysis based on keyword counting
        positive_words = ["good", "excellent", "positive", "successful", "effective", "beneficial"]
        negative_words = ["bad", "poor", "negative", "failed", "ineffective", "problematic"]
        
        doc_sentiments = []
        
        for doc in doc_metadata[:10]:  # Analyze first 10 documents
            text = doc["text"].lower()
            pos_count = sum(1 for word in positive_words if word in text)
            neg_count = sum(1 for word in negative_words if word in text)
            
            if pos_count > neg_count:
                sentiment = "Positive"
            elif neg_count > pos_count:
                sentiment = "Negative"
            else:
                sentiment = "Neutral"
            
            doc_sentiments.append({
                "filename": doc.get("metadata", {}).get("filename", "Unknown"),
                "sentiment": sentiment,
                "positive_indicators": pos_count,
                "negative_indicators": neg_count
            })
        
        summary = "Document Sentiment Analysis:\n"
        for doc_sent in doc_sentiments:
            summary += f"- {doc_sent['filename']}: {doc_sent['sentiment']} (pos: {doc_sent['positive_indicators']}, neg: {doc_sent['negative_indicators']})\n"
        
        return summary
    
    def _extract_themes(self) -> str:
        # Simple theme extraction using keyword frequency
        word_freq = {}
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        
        for doc in doc_metadata[:20]:  # Analyze first 20 documents
            words = re.findall(r'\b\w+\b', doc["text"].lower())
            for word in words:
                if len(word) > 3 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top themes
        top_themes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        themes_summary = "Top Themes in Documents:\n"
        for theme, count in top_themes:
            themes_summary += f"- {theme.title()}: mentioned {count} times\n"
        
        return themes_summary
    
    def _document_statistics(self) -> str:
        if not doc_metadata:
            return "No documents available for statistics."
        
        # Calculate statistics
        total_docs = len(doc_metadata)
        doc_types = {}
        total_words = 0
        
        for doc in doc_metadata:
            # Document type statistics
            doc_type = doc.get("metadata", {}).get("doc_type", "Unknown")
            doc_types[doc_type] = doc_types.get(doc_type, 0) + 1
            
            # Word count
            word_count = len(doc["text"].split())
            total_words += word_count
        
        avg_words = total_words / total_docs if total_docs > 0 else 0
        
        stats = f"""Document Statistics:
- Total document chunks: {total_docs}
- Total words: {total_words:,}
- Average words per chunk: {avg_words:.1f}
- Document types: {len(doc_types)}

Document Type Breakdown:
"""
        for doc_type, count in doc_types.items():
            percentage = (count / total_docs) * 100
            stats += f"- {doc_type}: {count} chunks ({percentage:.1f}%)\n"