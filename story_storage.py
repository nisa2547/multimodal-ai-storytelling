import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class StoryStorage:
    """
    A storage system for managing story content and generating recaps for GPT-4.
    """
    
    def __init__(self, story_id: Optional[str] = None):
        """
        Initialize a new story storage instance.
        
        Args:
            story_id: Optional identifier for the story. If not provided, a timestamp-based ID will be created.
        """
        self.story_id = story_id or f"story_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.sections = []
        self.metadata = {
            "title": "",
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "section_count": 0,
            "characters": [],
            "settings": [],
            "tags": []
        }
        self.storage_dir = os.path.join("stories", self.story_id)
        
        # Create storage directory if it doesn't exist
        if not os.path.exists(self.storage_dir):
            os.makedirs(self.storage_dir, exist_ok=True)
    
    def add_section(self, content: str, section_title: Optional[str] = None) -> int:
        """
        Add a new section to the story.
        
        Args:
            content: The text content of the section
            section_title: Optional title for this section
            
        Returns:
            The index of the newly added section
        """
        section_number = len(self.sections)
        
        section = {
            "section_number": section_number,
            "title": section_title or f"Section {section_number + 1}",
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        self.sections.append(section)
        self.metadata["section_count"] = len(self.sections)
        self.metadata["last_updated"] = datetime.now().isoformat()
        
        # Save the updated story
        self._save_story()
        
        return section_number
    
    def update_section(self, section_number: int, content: str, section_title: Optional[str] = None) -> bool:
        """
        Update an existing section of the story.
        
        Args:
            section_number: The index of the section to update
            content: The new content for the section
            section_title: Optional new title for the section
            
        Returns:
            True if the update was successful, False otherwise
        """
        if 0 <= section_number < len(self.sections):
            if section_title:
                self.sections[section_number]["title"] = section_title
            
            self.sections[section_number]["content"] = content
            self.sections[section_number]["timestamp"] = datetime.now().isoformat()
            self.metadata["last_updated"] = datetime.now().isoformat()
            
            # Save the updated story
            self._save_story()
            
            return True
        return False
    
    def get_section(self, section_number: int) -> Optional[Dict]:
        """
        Retrieve a specific section of the story.
        
        Args:
            section_number: The index of the section to retrieve
            
        Returns:
            The section data as a dictionary, or None if the section doesn't exist
        """
        if 0 <= section_number < len(self.sections):
            return self.sections[section_number]
        return None
    
    def get_all_sections(self) -> List[Dict]:
        """
        Retrieve all sections of the story.
        
        Returns:
            A list of all section dictionaries
        """
        return self.sections
    
    def generate_recap(self, max_sections: int = 3) -> str:
        """
        Generate a recap of recent story developments for GPT.
        
        Args:
            max_sections: Maximum number of recent sections to include in the recap
            
        Returns:
            A formatted recap string
        """
        if not self.sections:
            return "No story content available yet."
        
        # Get the most recent sections, limited by max_sections
        recent_sections = self.sections[-max_sections:] if len(self.sections) > max_sections else self.sections
        
        recap = f"Story Recap ('{self.metadata['title']}'):\n\n"
        
        # Add a context summary if we're not showing all sections
        if len(recent_sections) < len(self.sections):
            recap += f"[Note: This is a recap of the most recent {len(recent_sections)} out of {len(self.sections)} total sections.]\n\n"
        
        # Add recent section summaries
        for section in recent_sections:
            # Create a summary (first 100 characters + "..." if longer)
            content_summary = section["content"][:100]
            if len(section["content"]) > 100:
                content_summary += "..."
            
            recap += f"Section {section['section_number'] + 1}: {section['title']}\n"
            recap += f"{content_summary}\n\n"
        
        # Add metadata about key story elements
        if self.metadata["characters"]:
            recap += f"Characters: {', '.join(self.metadata['characters'])}\n"
        
        if self.metadata["settings"]:
            recap += f"Settings: {', '.join(self.metadata['settings'])}\n"
        
        return recap
    
    def update_metadata(self, title: Optional[str] = None, characters: Optional[List[str]] = None, 
                        settings: Optional[List[str]] = None, tags: Optional[List[str]] = None) -> None:
        """
        Update story metadata.
        
        Args:
            title: New story title
            characters: List of character names
            settings: List of story settings/locations
            tags: List of tags/themes for the story
        """
        if title:
            self.metadata["title"] = title
        
        if characters:
            self.metadata["characters"] = list(set(self.metadata["characters"] + characters))
        
        if settings:
            self.metadata["settings"] = list(set(self.metadata["settings"] + settings))
        
        if tags:
            self.metadata["tags"] = list(set(self.metadata["tags"] + tags))
        
        self.metadata["last_updated"] = datetime.now().isoformat()
        
        # Save the updated metadata
        self._save_story()
    
    def _save_story(self) -> None:
        """Save the current story state to disk."""
        # Save metadata
        with open(os.path.join(self.storage_dir, "metadata.json"), "w") as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save all sections
        with open(os.path.join(self.storage_dir, "sections.json"), "w") as f:
            json.dump(self.sections, f, indent=2)
    
    def load_story(story_id: str) -> 'StoryStorage':
        """
        Load a story from disk.
        
        Args:
            story_id: The ID of the story to load
            
        Returns:
            A StoryStorage instance with the loaded story data
        """
        storage = StoryStorage(story_id)
        storage_dir = os.path.join("stories", story_id)
        
        # Check if the story exists
        if not os.path.exists(storage_dir):
            raise FileNotFoundError(f"Story with ID '{story_id}' not found")
        
        # Load metadata
        with open(os.path.join(storage_dir, "metadata.json"), "r") as f:
            storage.metadata = json.load(f)
        
        # Load sections
        with open(os.path.join(storage_dir, "sections.json"), "r") as f:
            storage.sections = json.load(f)
        
        return storage
    
    def list_stories() -> List[Dict]:
        """
        List all available stories.
        
        Returns:
            A list of story metadata dictionaries
        """
        stories = []
        stories_dir = "stories"
        
        # Create stories directory if it doesn't exist
        if not os.path.exists(stories_dir):
            os.makedirs(stories_dir, exist_ok=True)
            return stories
        
        # List all story directories
        for story_id in os.listdir(stories_dir):
            metadata_path = os.path.join(stories_dir, story_id, "metadata.json")
            
            if os.path.exists(metadata_path):
                with open(metadata_path, "r") as f:
                    metadata = json.load(f)
                    metadata["story_id"] = story_id
                    stories.append(metadata)
        
        return stories
    
    def delete_story(story_id: str) -> bool:
        """
        Delete a story from disk.
        
        Args:
            story_id: The ID of the story to delete
            
        Returns:
            True if the story was deleted, False otherwise
        """
        storage_dir = os.path.join("stories", story_id)
        
        if os.path.exists(storage_dir):
            # Delete all files in the directory
            for filename in os.listdir(storage_dir):
                file_path = os.path.join(storage_dir, filename)
                if os.path.isfile(file_path):
                    os.unlink(file_path)
            
            # Delete the directory
            os.rmdir(storage_dir)
            return True
        
        return False