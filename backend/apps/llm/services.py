"""
LangChain integration service for LoreBoard
Handles all LLM operations
"""

from typing import List, Dict, Optional, Tuple
import logging
from django.conf import settings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.schema import BaseMessage
from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.callbacks import CallbackManager
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from pydantic import BaseModel, Field
import json

logger = logging.getLogger(__name__)


# Pydantic models for structured outputs
class ExtractedEntity(BaseModel):
    """Entity extracted from text"""
    name: str = Field(description="Entity name")
    type: str = Field(description="Entity type: character, location, item, event")
    description: str = Field(description="Brief description of the entity")
    confidence: float = Field(description="Confidence score 0-1")


class AutoFillSuggestion(BaseModel):
    """Suggestion for auto-fill slot"""
    text: str = Field(description="Suggested text")
    confidence: float = Field(description="Confidence score 0-1")
    reasoning: str = Field(description="Why this suggestion fits")


class ConsistencyIssue(BaseModel):
    """Inconsistency found in content"""
    type: str = Field(description="Type of inconsistency")
    entity: Optional[str] = Field(description="Related entity if applicable")
    issue: str = Field(description="Description of the issue")
    severity: str = Field(description="Severity: low, medium, high")
    locations: List[Dict] = Field(description="Where the issue occurs")


class LLMService:
    """
    Service for all LLM operations using LangChain
    """
    
    def __init__(self):
        # Initialize LLM based on settings
        self.llm = self._initialize_llm()
        self.embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)
        self.vector_store = None  # Initialize when needed
        
    def _initialize_llm(self):
        """Initialize the LLM based on configuration"""
        if settings.LLM_PROVIDER == 'openai':
            return ChatOpenAI(
                model_name=settings.LLM_MODEL,
                temperature=settings.LLM_TEMPERATURE,
                openai_api_key=settings.OPENAI_API_KEY,
                max_tokens=2000
            )
        # Add other providers as needed
        else:
            raise ValueError(f"Unsupported LLM provider: {settings.LLM_PROVIDER}")
    
    async def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract entities from text using LLM
        """
        # Create parser for structured output
        parser = PydanticOutputParser(pydantic_object=ExtractedEntity)
        
        # Create prompt template
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a creative writing assistant that identifies important entities "
                "(characters, locations, items, events) in story text. "
                "Extract all significant entities that would be worth tracking."
            ),
            HumanMessagePromptTemplate.from_template(
                "Extract entities from this text:\n\n{text}\n\n"
                "Format: {format_instructions}"
            )
        ])
        
        # Create chain
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_parser=OutputFixingParser.from_llm(parser=parser, llm=self.llm)
        )
        
        try:
            # Run extraction
            result = await chain.arun(
                text=text,
                format_instructions=parser.get_format_instructions()
            )
            
            # Convert to list of dicts
            entities = []
            if isinstance(result, list):
                entities = [entity.dict() for entity in result]
            else:
                # Handle single entity
                entities = [result.dict()]
            
            logger.info(f"Extracted {len(entities)} entities from text")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return []
    
    async def generate_autofill_suggestions(
        self, 
        context_before: str, 
        context_after: str,
        num_suggestions: int = 3
    ) -> List[str]:
        """
        Generate suggestions for auto-fill slots
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a creative writing assistant. Given the context before and after a blank, "
                "suggest appropriate words or short phrases that would fit naturally. "
                "Consider style, tone, and narrative flow."
            ),
            HumanMessagePromptTemplate.from_template(
                "Context before: {context_before}\n"
                "Context after: {context_after}\n\n"
                "Suggest {num} different options that would fit in the blank. "
                "Return as a JSON array of strings."
            )
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = await chain.arun(
                context_before=context_before,
                context_after=context_after,
                num=num_suggestions
            )
            
            # Parse JSON response
            suggestions = json.loads(result)
            if isinstance(suggestions, list):
                return suggestions[:num_suggestions]
            else:
                return [str(suggestions)]
                
        except Exception as e:
            logger.error(f"Error generating autofill suggestions: {str(e)}")
            # Fallback suggestions
            return ["word", "phrase", "text"]
    
    async def get_entity_summary(self, entity_data: Dict, query: str) -> str:
        """
        Generate a summary about an entity based on a specific query
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a helpful assistant that provides information about story entities. "
                "Based on the entity data provided, answer the user's question concisely."
            ),
            HumanMessagePromptTemplate.from_template(
                "Entity: {entity_name}\n"
                "Type: {entity_type}\n"
                "Description: {description}\n"
                "Attributes: {attributes}\n"
                "Mentions in content: {mention_count}\n\n"
                "Question: {query}"
            )
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            summary = await chain.arun(
                entity_name=entity_data.get('name', 'Unknown'),
                entity_type=entity_data.get('type', 'unknown'),
                description=entity_data.get('description', 'No description'),
                attributes=json.dumps(entity_data.get('attributes', {})),
                mention_count=entity_data.get('mention_count', 0),
                query=query
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating entity summary: {str(e)}")
            return "Unable to generate summary at this time."
    
    async def analyze_content_consistency(self, content: str, entities: List[Dict]) -> List[Dict]:
        """
        Analyze content for consistency issues
        """
        # Create parser for structured output
        parser = PydanticOutputParser(pydantic_object=ConsistencyIssue)
        
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a meticulous editor checking for consistency in creative writing. "
                "Look for contradictions, inconsistencies in character attributes, "
                "timeline issues, and other continuity errors."
            ),
            HumanMessagePromptTemplate.from_template(
                "Content to analyze:\n{content}\n\n"
                "Known entities: {entities}\n\n"
                "Identify any consistency issues. Format: {format_instructions}"
            )
        ])
        
        chain = LLMChain(
            llm=self.llm,
            prompt=prompt,
            output_parser=OutputFixingParser.from_llm(parser=parser, llm=self.llm)
        )
        
        try:
            result = await chain.arun(
                content=content,
                entities=json.dumps(entities),
                format_instructions=parser.get_format_instructions()
            )
            
            # Convert to list of dicts
            issues = []
            if isinstance(result, list):
                issues = [issue.dict() for issue in result]
            else:
                issues = [result.dict()]
            
            return issues
            
        except Exception as e:
            logger.error(f"Error analyzing consistency: {str(e)}")
            return []
    
    def create_content_embedding(self, text: str) -> List[float]:
        """
        Create embedding for content
        """
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            logger.error(f"Error creating embedding: {str(e)}")
            return []
    
    async def find_similar_content(self, query: str, limit: int = 5) -> List[Tuple[str, float]]:
        """
        Find similar content using vector search
        """
        if not self.vector_store:
            # Initialize vector store if needed
            # This would connect to your vector database
            pass
        
        try:
            # Perform similarity search
            results = self.vector_store.similarity_search_with_score(query, k=limit)
            return [(doc.page_content, score) for doc, score in results]
        except Exception as e:
            logger.error(f"Error finding similar content: {str(e)}")
            return []
    
    async def generate_writing_prompt(self, context: Dict) -> str:
        """
        Generate a writing prompt based on current context
        """
        prompt = ChatPromptTemplate.from_messages([
            SystemMessagePromptTemplate.from_template(
                "You are a creative writing coach. Generate an inspiring writing prompt "
                "based on the story context provided."
            ),
            HumanMessagePromptTemplate.from_template(
                "Current story elements:\n"
                "Entities: {entities}\n"
                "Recent content: {recent_content}\n"
                "Genre/Style: {style}\n\n"
                "Generate a creative prompt to continue the story:"
            )
        ])
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        
        try:
            result = await chain.arun(
                entities=json.dumps(context.get('entities', [])),
                recent_content=context.get('recent_content', 'No recent content'),
                style=context.get('style', 'General fiction')
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating writing prompt: {str(e)}")
            return "What happens next in your story?"
