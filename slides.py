### TODO:
# - persist audio files in Slide

import json


class SlideDeck:
    """
    A class representing a collection of slides organized around a specific topic.

    The SlideDeck class manages multiple Slide objects and provides functionality
    for serialization and deserialization of the slide deck data.

    Attributes:
        topic (str): The main topic or title of the slide deck
        slides (list[Slide]): A list of Slide objects contained in the deck
    """

    def __init__(self, topic, slides):
        """
        Initialize a new SlideDeck instance.

        Args:
            topic (str): The main topic or title of the slide deck
            slides (list[Slide]): A list of Slide objects to include in the deck
        """
        self.topic = topic
        self.slides = slides

    def to_dict(self):
        """
        Convert the SlideDeck instance to a dictionary format.

        Returns:
            dict: A dictionary containing the slide deck data with the following structure:
                {
                    "topic": str,
                    "slides": list[dict]
                }
        """
        return {
            "topic": self.topic,
            "slides": [slide.to_dict() for slide in self.slides],
        }

    def save_to_file(self, filename):
        """
        Save the slide deck to a JSON file.

        Args:
            filename (str): The path to the file where the slide deck should be saved
        """
        with open(filename, "w") as file:
            json.dump(self.to_dict(), file, indent=4)

    @classmethod
    def load_from_file(cls, filename):
        """
        Create a SlideDeck instance from a JSON file.

        Args:
            filename (str): The path to the JSON file containing the slide deck data

        Returns:
            SlideDeck: A new SlideDeck instance populated with the data from the file
        """
        with open(filename, "r") as file:
            data = json.load(file)
            slides = [Slide(**slide_data) for slide_data in data["slides"]]
            return cls(data["topic"], slides)


class Slide:
    """
    A class representing a single slide in a slide deck.

    Each slide contains information about its section, topic, narration text,
    and bullet points for presentation.

    Attributes:
        section (str): The section or chapter the slide belongs to
        topic (str): The specific topic or title of the slide
        narration (str): The narration text associated with the slide
        bullets (list[str]): A list of bullet points to be displayed on the slide
    """

    def __init__(self, section, topic, narration, bullets):
        """
        Initialize a new Slide instance.

        Args:
            section (str): The section or chapter the slide belongs to
            topic (str): The specific topic or title of the slide
            narration (str): The narration text associated with the slide
            bullets (list[str]): A list of bullet points to be displayed on the slide
        """
        self.section = section
        self.topic = topic
        self.narration = narration
        self.bullets = bullets

    def to_dict(self):
        """
        Convert the Slide instance to a dictionary format.

        Returns:
            dict: A dictionary containing the slide data with the following structure:
                {
                    "section": str,
                    "topic": str,
                    "narration": str,
                    "bullets": list[str]
                }
        """
        return {
            "section": self.section,
            "topic": self.topic,
            "narration": self.narration,
            "bullets": self.bullets,
        }

    def render(self, display_narration=False):
        """
        Render the slide content in markdown format.

        Args:
            display_narration (bool, optional): Whether to include the narration text
                in the rendered output. Defaults to False.

        Returns:
            str: The slide content formatted as markdown text, including section title,
                topic, numbered bullet points, and optionally the narration text.
        """
        markdown_text = f"# {self.section}\n## {self.topic}\n"
        for index, bullet in enumerate(self.bullets, start=1):
            markdown_text += f"{index}. {bullet.strip()}\n\n"
        if display_narration:
            markdown_text += "---\n\n\n"  # Separator line
            markdown_text += f"*{self.narration}*"
        return markdown_text
