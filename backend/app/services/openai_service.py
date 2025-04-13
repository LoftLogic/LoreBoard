import openai
from typing import Dict, Any, List, Optional
from app.core.config import settings

# Configure OpenAI API
openai.api_key = settings.OPENAI_API_KEY

def extract_entity_attributes(entity_type: str, entity_name: str, context_text: str) -> Dict[str, str]:
    """
    Extract attributes for a new entity using OpenAI API.
    
    Args:
        entity_type: Type of entity (character, place, item)
        entity_name: Name of the entity
        context_text: Text context where the entity appears
        
    Returns:
        Dictionary with extracted attributes
    """
    # Define prompts based on entity type
    if entity_type == "character":
        system_prompt = f"""
        You are an assistant helping to extract information about a character in a story. 
        The character's name is {entity_name}.
        From the provided text, identify and extract relevant details about this character.
        
        Organize the information into these categories:
        - physical: Physical appearance and characteristics
        - personality: Personality traits, behaviors, and mannerisms
        - background: History, origin, and past experiences
        - goals: Motivations, desires, and objectives
        - relationships: Connections with other characters or entities
        
        Keep each category concise but comprehensive. If information for a category is not present, provide an empty string for that category.
        Format your response as a JSON object with these categories as keys.
        """
        
    elif entity_type == "place":
        system_prompt = f"""
        You are an assistant helping to extract information about a place in a story. 
        The place's name is {entity_name}.
        From the provided text, identify and extract relevant details about this place.
        
        Organize the information into these categories:
        - physical: Physical attributes, appearance, and characteristics
        - environment: Surrounding environment, atmosphere, and conditions
        - purpose: Function, role, or purpose of the place
        - history: Background, past events, and origin
        - location: Where this place is situated relative to other locations
        
        Keep each category concise but comprehensive. If information for a category is not present, provide an empty string for that category.
        Format your response as a JSON object with these categories as keys.
        """
        
    elif entity_type == "item":
        system_prompt = f"""
        You are an assistant helping to extract information about an item in a story. 
        The item's name is {entity_name}.
        From the provided text, identify and extract relevant details about this item.
        
        Organize the information into these categories:
        - physical: Physical appearance, size, material, and other characteristics
        - function: Purpose, use, and functionality
        - origin: Where it came from, who made it, its history
        - ownership: Who owns it or has possessed it
        - properties: Special properties, powers, or unique attributes
        
        Keep each category concise but comprehensive. If information for a category is not present, provide an empty string for that category.
        Format your response as a JSON object with these categories as keys.
        """
    else:
        raise ValueError(f"Invalid entity type: {entity_type}")

    # Check if the entity name exists in the context
    if entity_name.lower() not in context_text.lower():
        raise ValueError(f"Entity '{entity_name}' not found in the provided text context.")
    
    # If the entity name is a common word or very short, it might be a false positive
    if len(entity_name) <= 3 and entity_name.lower() in ["a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so"]:
        raise ValueError(f"'{entity_name}' appears to be a common word rather than a valid entity name.")

    # Make the API call
    response = openai.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the text context:\n\n{context_text}"}
        ],
        response_format={"type": "json_object"}
    )
    
    # Extract and return the result
    try:
        content = response.choices[0].message.content
        import json
        result = json.loads(content)
        
        # Validate the response based on entity type
        if entity_type == "character":
            expected_keys = ["physical", "personality", "background", "goals", "relationships"]
        elif entity_type == "place":
            expected_keys = ["physical", "environment", "purpose", "history", "location"]
        elif entity_type == "item":
            expected_keys = ["physical", "function", "origin", "ownership", "properties"]
            
        # Ensure all expected keys are present
        for key in expected_keys:
            if key not in result:
                result[key] = ""
                
        return result
    except Exception as e:
        raise ValueError(f"Failed to parse LLM response: {str(e)}")

def update_entity_attributes(entity_type: str, entity_name: str, existing_data: Dict[str, Any], context_text: str, category: Optional[str] = None) -> Dict[str, str]:
    """
    Update attributes for an existing entity using OpenAI API.
    
    Args:
        entity_type: Type of entity (character, place, item)
        entity_name: Name of the entity
        existing_data: Existing entity data
        context_text: New text context
        category: Specific category to update (optional)
        
    Returns:
        Dictionary with updated attributes
    """
    # Create a description of the existing entity
    existing_info = ""
    if entity_type == "character":
        categories = ["physical", "personality", "background", "goals", "relationships"]
        for cat in categories:
            if existing_data.get(cat):
                existing_info += f"{cat}: {existing_data.get(cat, '')}\n\n"
    elif entity_type == "place":
        categories = ["physical", "environment", "purpose", "history", "location"]
        for cat in categories:
            if existing_data.get(cat):
                existing_info += f"{cat}: {existing_data.get(cat, '')}\n\n"
    elif entity_type == "item":
        categories = ["physical", "function", "origin", "ownership", "properties"]
        for cat in categories:
            if existing_data.get(cat):
                existing_info += f"{cat}: {existing_data.get(cat, '')}\n\n"
    else:
        raise ValueError(f"Invalid entity type: {entity_type}")
    
    # Define system prompt based on the update type
    if category:
        # Specific category update
        system_prompt = f"""
        You are an assistant helping to update information about a {entity_type} in a story. 
        The {entity_type}'s name is {entity_name}.
        
        Here is the existing information about this {entity_type}:
        {existing_info}
        
        From the new text context, extract any new or updated information about the '{category}' category ONLY.
        Do not repeat information that is already included in the existing data.
        Format your response as text that can be appended to the existing information.
        """
    else:
        # General update
        system_prompt = f"""
        You are an assistant helping to update information about a {entity_type} in a story. 
        The {entity_type}'s name is {entity_name}.
        
        Here is the existing information about this {entity_type}:
        {existing_info}
        
        From the new text context, identify and extract any new or updated information about this {entity_type}.
        Do not repeat information that is already included in the existing data.
        
        If entity_type is 'character', organize any new information into these categories:
        - physical: Physical appearance and characteristics
        - personality: Personality traits, behaviors, and mannerisms
        - background: History, origin, and past experiences
        - goals: Motivations, desires, and objectives
        - relationships: Connections with other characters or entities
        
        If entity_type is 'place', organize any new information into these categories:
        - physical: Physical attributes, appearance, and characteristics
        - environment: Surrounding environment, atmosphere, and conditions
        - purpose: Function, role, or purpose of the place
        - history: Background, past events, and origin
        - location: Where this place is situated relative to other locations
        
        If entity_type is 'item', organize any new information into these categories:
        - physical: Physical appearance, size, material, and other characteristics
        - function: Purpose, use, and functionality
        - origin: Where it came from, who made it, its history
        - ownership: Who owns it or has possessed it
        - properties: Special properties, powers, or unique attributes
        
        Format your response as a JSON object with these categories as keys. Include only categories that have new information.
        """
    
    # Check if the entity name exists in the context
    if entity_name.lower() not in context_text.lower() and not any(
        alias.lower() in context_text.lower() 
        for alias in existing_data.get("aliases", [])
    ):
        raise ValueError(f"Entity '{entity_name}' or its aliases not found in the provided text context.")

    # Make the API call
    response = openai.chat.completions.create(
        model=settings.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the new text context:\n\n{context_text}"}
        ],
        response_format={"type": "json_object"} if not category else None
    )
    
    # Extract and process the result
    content = response.choices[0].message.content
    
    if category:
        # For specific category updates, return just that category's update
        return {category: content.strip()}
    else:
        # For general updates, parse the JSON
        try:
            import json
            result = json.loads(content)
            
            # If entity_type is 'character', ensure expected keys
            if entity_type == "character":
                for key in ["physical", "personality", "background", "goals", "relationships"]:
                    if key not in result:
                        result[key] = ""
            # If entity_type is 'place', ensure expected keys
            elif entity_type == "place":
                for key in ["physical", "environment", "purpose", "history", "location"]:
                    if key not in result:
                        result[key] = ""
            # If entity_type is 'item', ensure expected keys
            elif entity_type == "item":
                for key in ["physical", "function", "origin", "ownership", "properties"]:
                    if key not in result:
                        result[key] = ""
                        
            return result
        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {str(e)}")

def detect_entities_in_text(text: str, known_entities: Dict[str, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
    """
    Detect known entities in a text segment.
    
    Args:
        text: Text to analyze
        known_entities: Dictionary of known entities with their aliases
        
    Returns:
        List of detected entities with positions
    """
    detected = []
    
    # Process characters
    for char in known_entities.get("characters", []):
        name = char["name"]
        # Check for name
        idx = text.lower().find(name.lower())
        if idx >= 0:
            detected.append({
                "id": char["id"],
                "name": name,
                "type": "character",
                "position": idx
            })
        
        # Check for aliases
        for alias in char.get("aliases", []):
            idx = text.lower().find(alias.lower())
            if idx >= 0:
                detected.append({
                    "id": char["id"],
                    "name": name,
                    "alias_used": alias,
                    "type": "character",
                    "position": idx
                })
    
    # Process places
    for place in known_entities.get("places", []):
        name = place["name"]
        # Check for name
        idx = text.lower().find(name.lower())
        if idx >= 0:
            detected.append({
                "id": place["id"],
                "name": name,
                "type": "place",
                "position": idx
            })
        
        # Check for aliases
        for alias in place.get("aliases", []):
            idx = text.lower().find(alias.lower())
            if idx >= 0:
                detected.append({
                    "id": place["id"],
                    "name": name,
                    "alias_used": alias,
                    "type": "place",
                    "position": idx
                })
    
    # Process items
    for item in known_entities.get("items", []):
        name = item["name"]
        # Check for name
        idx = text.lower().find(name.lower())
        if idx >= 0:
            detected.append({
                "id": item["id"],
                "name": name,
                "type": "item",
                "position": idx
            })
        
        # Check for aliases
        for alias in item.get("aliases", []):
            idx = text.lower().find(alias.lower())
            if idx >= 0:
                detected.append({
                    "id": item["id"],
                    "name": name,
                    "alias_used": alias,
                    "type": "item",
                    "position": idx
                })
    
    return detected

def process_text_for_entity_updates(text: str, entities: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Process text to extract updates for multiple entities.
    
    Args:
        text: Text to analyze
        entities: List of entities to update
        
    Returns:
        Dictionary of entity updates by entity ID
    """
    # For MVP, we'll process each entity separately
    # In a production environment, we might want to batch this
    updates = {}
    
    for entity in entities:
        system_prompt = f"""
        You are an assistant helping to update information about a {entity['type']} in a story. 
        The {entity['type']}'s name is {entity['name']}.
        
        From the provided text, identify and extract any new information about this {entity['type']}.
        
        If entity_type is 'character', organize any new information into these categories:
        - physical: Physical appearance and characteristics
        - personality: Personality traits, behaviors, and mannerisms
        - background: History, origin, and past experiences
        - goals: Motivations, desires, and objectives
        - relationships: Connections with other characters or entities
        
        If entity_type is 'place', organize any new information into these categories:
        - physical: Physical attributes, appearance, and characteristics
        - environment: Surrounding environment, atmosphere, and conditions
        - purpose: Function, role, or purpose of the place
        - history: Background, past events, and origin
        - location: Where this place is situated relative to other locations
        
        If entity_type is 'item', organize any new information into these categories:
        - physical: Physical appearance, size, material, and other characteristics
        - function: Purpose, use, and functionality
        - origin: Where it came from, who made it, its history
        - ownership: Who owns it or has possessed it
        - properties: Special properties, powers, or unique attributes
        
        Format your response as a JSON object with these categories as keys. 
        Include only categories that have new information.
        If no new information is found, return an empty JSON object.
        """
        
        # Make the API call
        response = openai.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Here is the text context:\n\n{text}"}
            ],
            response_format={"type": "json_object"}
        )
        
        # Extract and process the result
        try:
            content = response.choices[0].message.content
            import json
            result = json.loads(content)
            
            # Only add to updates if there's actual content
            if result and any(result.values()):
                updates[str(entity['id'])] = {
                    "type": entity['type'],
                    "updates": result
                }
        except Exception as e:
            # Just skip problematic entities for MVP
            continue
    
    return updates