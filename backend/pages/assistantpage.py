from __future__ import annotations
from abc import ABC, abstractmethod

from pydantic import BaseModel, create_model, Field

import json

from backend.pages.templates.entity_templates import generate_character_sheet

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import JsonOutputParser

import json

from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate
)

"""
File for all pages for the assistant. Includes entities, metadata, etc.
"""

class Entity(ABC):
    @abstractmethod
    def add_alias(self, new_alias: str):
        """
        Adds an alias for the entity.
        Aliases are any text that refers to the entity.
        """
        raise NotImplementedError("Must be overriden by subclass")
    
    @abstractmethod
    def removes_alias(self, to_remove: str):
        """
        Removes an alias for the entity.
        Aliases are any text that refers to the entity.
        """
        raise NotImplementedError("Must be overriden by subclass")
        
    @abstractmethod
    def reset(self):
        """
        Resets the sheet to square one.
        """
        raise NotImplementedError
    
    @abstractmethod
    def initial_pass(self):
        """
        Does an initial reading of text and creates a character sheet.
        Should only be called once unless reset.
        Raises a runtime error if its already called.
        """
        raise NotImplementedError
    
    @abstractmethod
    def update(self):
        """
        Updates the sheet for the specific entity.
        Invokes a specific LLM chain.
        """
        raise NotImplementedError("Must be overriden by subclass")
    
    @abstractmethod
    def as_dict(self) -> dict:
        raise NotImplementedError
    
    @abstractmethod
    def as_json(self) -> str:
        raise NotImplementedError("Must be overridden by subclass")

class Character(Entity):
    """
    An entity representing any character
    """
    def __init__(self, name: str):
        self.name = name
        self.reset()
        
    def add_alias(self, new_alias):
        self.aliases.add(new_alias)
        
    def removes_alias(self, to_remove):
        self.aliases.remove(to_remove)

    def reset(self):
        self.initialized_flag = False
        self.aliases = {self.name}
        self.physical_traits: str = "Physical Traits:\n To be created. (Call an update to create)"
        self.personality_traits: str = "Personality Traits:\n To be created. (Call an update to create)"
        self.actions: str = "Actions:\n To be created. (Call an update to create)"
        self.relationships: str = "Relationships: To be created. (Call an update to create)"

    def initial_pass(self):
        if self.initialized_flag:
            raise RuntimeError("Already initialized")
        
        raise NotImplementedError

    def update(self, passages):
        self.initialized_flag = True
        template: ChatPromptTemplate = generate_character_sheet(passages, self.name, self.aliases)
        llm = ChatOpenAI(model='gpt-4o')
        parser = JsonOutputParser()
        
        llm_chain = template | llm | parser
        
        passage_block = ""
        
        for i in range(len(passages)):
            passage_block += passages[i]
            if i > 0 and i < len(passages) - 1:
                passage_block += "\n"
                passage_block += "======================"
                passage_block += "\n"
        
        return llm_chain.invoke({"passage_block": passage_block})

    def as_dict(self) -> dict:
        character_dict = {
                "name": self.name,
                "physical_traits": self.physical_traits,
                "personality_traits": self.personality_traits,
                "actions": self.actions,
                "relationships": self.relationships,
        }
        return character_dict
    
    def as_json(self) -> str:
        return json.dumps(self.as_dict, indent=4)





    
class Setting(Entity):
    """
    An entity representing any location or place in the story.
    """
    def __init__(self, name: str):
        self.name = name
        self.aliases = {name}
        self.basic_role = "To be Created (Call an update to create)"
        self.physical_descriptions = "To be Created (Call an update to create)"
        self.personality_descriptions = "To be Created (Call an update to create)"
        self.stake_in_the_story = "To be Created (Call an update to create)"
        self.change_development = "To be Created (Call an update to create)"
        self.relationships = "To be Created (Call an update to create)"
        
    def add_alias(self, new_alias):
        self.aliases.add(new_alias)
        
    def removes_alias(self, to_remove):
        self.aliases.remove(to_remove)

    def update(self):
        raise NotImplementedError

    def as_dict(self) -> dict:
        setting_dict = {
                "name": self.name,
                "description": self.description,
                "special_traits": self.special_traits,
                "story_relevance": self.story_relevance,
                "general_location": self.general_location
        }
        return setting_dict
    
    def as_json(self) -> str:
        return json.dumps(self.as_dict, indent=4)

class Macro:
    """
    A macro is a word that refers to an entity.
    """
    def __init__(self, text: str, entity: Entity):
        self.text = text
        self.entity = entity
        
    def same_entity(self, other: Macro):
        return self.entity == other.entity
    
if __name__ == "__main__":
    char = Character("Achilles")
    
    passage = """
   Why is she here? She’s ruining everything, Achilles complained to himself. The stranger girl stood out, unfamiliar and out of place. Everything else was in order, and exactly how he wanted. 
His plate was just the way he liked- three pastries in a triangle, one with custard, one with pine nuts, one with apricot, and a jar of maple butter in the center. Next to it sat a chalice of peach cider, aged to perfection with cinnamon and cardamom, the same way his mother liked it. She was across the banquet table, along with his sister as they shared a platter of venison and rye. Beside them was his little brother, chasing and catching butterflies in an old glass jar. Half a dozen guards dressed in gold armor stood by watching. They were fierce and seasoned, half wielding spears and half wielding swords, each with a blue banner wrapped across their chest from their torso to their shoulder. The lush meadow clearing was sunny and quiet- aside from the laughter and conversation. He felt this strange sensation, like he was overjoyed to be alive. There was nothing that could ruin this moment, or at least he thought.
	It wasn’t just the girl’s face that was unfamiliar- it was everything. She did not look, dress, or act like anyone he had ever seen. Her hair was silky and long, flowing over her slender shoulders and down her back with a graceful choppy elegance. A sleek, dark yet colorful shade of navy blue tinted her hair, a liquid night sky cascading down to the ending strands where the deep blue dissolved into vibrant hues of violet, cyan, and indigo, branching off in different directions. She wore a hooded cloak that looked like a canvas and a wool tunic meshed into one, tattered with splotches of rustic paint around the edges of her sleeves and the bottom of her collar. Past the bottom of her collar was a strange metal lining that followed the edge of her coat down to its end around her lower waist.
	There were many questions he wanted to ask- “Why are you here?”, “Where did you get those clothes?”, or “How did you get your hair to look like that?”. However his peace mattered more than his curiosity, so he stayed silent. Maybe if he ignored her long enough she would just disappear, and his blissful quiet would remain undisturbed.
	“What are you wearing?” she asked, disturbing the quiet. What am I wearing? Achilles was perplexed, and the question shocked him out of his silence. He was not the person here who needed to explain his fashion choices, but he decided to play along. He gripped his tunic, a garment colored with royal blues, and pulled it forward for her to see. 
“It’s a tunic. The Sacrosanct wear it,” he said proudly as if that wasn’t common knowledge. She kneeled, looking down to inspect it. 
“What's that symbol? Is that a unicorn?”
	“A what?” 
	She pointed at the emblem ingrained on his tunic- a golden yellow emblem of a helmed horse and a cross with a sword pointing from the top of its head, ending right below where the mane began. 
“Oh! That's just a horse. It's the Sacrosanct’s coat of arms” he proudly stated, puzzled by why she didn’t recognize it. She must have grown up under a rock.
	“Why’s there a cross behind the horse?”
	“It represents the Sacroscants’s commitment to the blessing of light from-”
	“Sorry, that was a silly question.” She cut him off, her attention jumping from one item to another. “What are you eat-”
	“Who are you?”
	She paused, then let out a chuckle. “Right, I probably should have started with that. My name is Amelie, and I am a..., how should I put it” 
	“A Journeyman?” He jumped in, then immediately regretted not saying journeywoman instead.
	Amelie’s eyes lit up as she smiled, clearly impressed. “Yes! Kind of. More like a tourist.” 
	“A tourist?” Now he felt like the one who grew up under a rock.
	“Yeah. It's people who like to visit places I guess.”
	I guess? She doesn’t even understand the words she's saying. “So you're just here on an adventure then?”
	She laughed, pulled out a chair close to him, and sat down. “Sure, I guess. I’m here for other things as well”
	“Such as?”
	“Such as..." She took a second to ponder her answer. “I’m also a jailbreaker and a researcher.”
	A jailbreaker? He knew about the jailers- the guards, the wardens who work over them, and the sentinel who works over them. Maybe the royalty made it a role after half a dozen squads were captured at the Battle of Maverick Castle. “What do you research? Magic?”
	“Kind of, more like engineering and chemistry”. She scanned his face for any signs of comprehension and found none. “Or I guess, blacksmithing and alchemy”
	“Oh, I see, you study both?” That was impressive. Men had worked their whole lives to be either, and she was just both? Either she was a prodigy, or something was off. Very few people in the Commonwealth could score two roles, let alone someone of her youth.
	“Yeah, sometimes I do even more.” She let out a sly endearing smile. “Is that your family over there?” She pointed across the table.
	“Ah, yes!” Achilles’s tone jumped in energy and excitement. “That’s my little brother Kieran over there, the one chasing bugs, he's a bit of a wild animal, most tribesmen are.” He laughed, there were few things that brought him more joy than watching his brother do, well, anything. “My older sister Artemis is over there” He pointed to the opposite end of the table, where the rest of his family was too engrossed in their food and conversation to notice the girl. “She’s a commander, she leads the vanguard on their missions. They say she's one of the greatest military minds of all time.” There was a hint of pride in his voice. “Next to her is my mother, the one in the blue dress.” He needn’t say anything else, the reverence in his voice told Amelie enough.
	“Your brother’s a tribesperson? I thought your family were knights. Are people both?”
	“That's because, um...” His cheerful tone in his voice swiftly turned into concern and confusion.
	“Nevermind, don’t worry about that, I didn’t mean to stress you out,” Amelie warmly said, swiftly changing the subject.
	“Stress?” Achilles questioned.
	“It's- actually nevermind” She paused for a second, nervously brushed some of her navy strands back past her ear, then continued. “Why are you here?” She asked, with a warm but curious inflection.
	Why am I here? She’s the one who just showed up out of nowhere, Achilles thought to himself. “I am... enjoying time with my family.” Achilles said, speaking much slower, his voice riddled with uncertainty.
	“Okay,” She seemed discontent with his response. “But, sorry for being blunt, but…” She looked around, at the guards, at the table, at his family, at the food, at his clothes, and at his face. “Why are you actually here?”
	What? I just answered! His jaw clenched, and he moved his hands from his plating, rested them on the top of his knees, and turned his eyes away from her. Who is this person? She just appears, with some ridiculous hair speaking absolute nonsense, and pestering me with these silly questions! How did she even find us here? Why are the guards not doing anything? She's ruining it all! It was perfect, everything was perfect! Achilles rambled in his mind. I just answered that question, what do I even say? I’m enjoying time with my family. I’m enjoying good food with my noble accomplished family. I’m enjoying... His thoughts, the facts he knew for certain, turned into guesses. He glanced up at her face with a stern expression. “I already answered that question. Now, if you don’t leave me alone...” Nervousness began racking up in his voice as his demeanor shifted. “I will call the guards and have you removed. I swear it.” He turned his head to the soldiers and began to raise one of his hands to call them over, but she quickly grabbed his hand and brought it down to the table. Her skin felt smooth like porcelain, and it soothed Achilles’ nerves as her fingers pressed into his hand. His eyes darted back to her, and he grew silent, but he was quick to bring his hand away from her and back to rest on top of his knees.
	“What’s the last thing you remember?” She asked, slowly and sincerely. His nails began to dig into the top of his kneecaps. His breath grew rapid and laboured.
	“I am, I was... wait, I think I’m confused” His eyes began to drift down toward the ground, his mind stopped racing and just froze.
	“Listen, what do you— look at me” She commanded gently. He slowly turned his head to her, his face riddled with uncertainty and confusion. “What’s the last thing you remember before coming to this area? Before sitting down, before coming to this clearing, what’s the last thing you remember!?” 
	“I uhhh—, I think” He took a minute to recall, each second he grew more upset. “I remember water. Yes, there was water.” His eyes began to swell up with tears, and his nails dug so hard into his knees that they began to tear the fabric of his trousers.
	“So, you remember water?” She looked extremely concerned, yet curious. “Water, okay. Were you in the water?”
	“... Yes” His voice began to break, and his right leg started jittering and bouncing up and down. Blood began to seep out where his nails had been digging.
	“Okay, what were you doing in the water”
	“I was... I was drowning. I think I’m dying.” He spoke in terrified upset whispers, his leg bouncing fast enough to shake the entire banquet table, but no one seemed to notice. His head dropped and hung down. He began to panic as he lifted the hands he was just using to tear into his legs and raised them to his head, wrapping them around his skull to form a cocoon and he slammed his elbows into the tabletop as his thoughts spiraled. “I’m uhhhhh...” He let out a defeated chuckle. “I’m unsure what to do. This might be it.” His voice dropped with each word he said as he resigned himself to whatever fate was in store for him. Not a single guard even looked in their direction, and his brother was still running around in the field, and his sister and mother were still blabbering about nonsense, but Amelie took notice.
	“Listen, look at me.” She said again, then rose with enough speed to knock her chair backward into the grass. She paced over to where he was sitting and wrenched his arms away from his head. She stood over him as he turned to look up. “You’re still here. You’re still able to talk to me. You just held an entire conversation.” Achilles didn’t respond, he just nodded. She sat on top of the table, getting closer, as her voice became soft and cheery. “That means you're still alive. Not just surviving, but you're alive!”
	“Yes!” He finally spoke again, this time with a slight semblance of newfound purpose and hope.
	“As long as you are you, as long as you can think, and dream, as long as your mind is intact, there's still hope. You understand? It doesn’t matter how much water is in your lungs, you're still here, you're talking to me, your mind is still working, you are still you!”
	“You're right, you... you are right!” His jaw unclenched, and his breathing slowed. 
	“What are you going to do now?” She asked, clearly hoping for a specific answer.
	How could I be so pathetic? His mind screamed internally. A fall in water was enough to make him surrender his will? He was a bladesman, a warrior, and possessed all the bravery and valor that came with. “I’m going to live. I’m going to win!” He proclaimed, with a strength he had not felt in a long time. Despite knowing that it was probably a lie, he was content knowing he would at least try, and in the worst case, die honorably, sword in hand.
	“Good, good! I’m very proud of you. Now, Achilles” She looked at him, with a strong sense of admiration. “Wake Up!”
    """
    
    print(json.dumps(char.update(passage), indent=4))