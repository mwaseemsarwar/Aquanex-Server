import re
from typing import List

INFORMAL_PATTERNS: List[str] = [
    "hi", "hello", "hey", "what's up", "how are you", "good morning", "good evening", "good afternoon",
    "thank you", "thanks", "yo", "greetings", "sup", "hiya", "hey there", "heya", "howdy",
    "what's good", "wassup", "holla", "cheers", "thank u", "thanx", "ty", "gm", "gn", "morning",
    "evening", "afternoon", "hello there", "hi there", "nice to meet you", "pleasure to meet you",
    "how’s it going", "how you doing", "what’s going on", "yo bro", "yo man", "yo dude", "hey buddy",
    "hey mate", "namaste", "vanakkam", "salaam", "hello sir", "hello ma'am", "hey team", "hello everyone",
    "hey folks", "good day", "greetings of the day", "hope you are doing well",
    "i hope this message finds you well", "dear sir", "dear madam", "dear team", "respected sir",
    "respected madam", "with due respect", "to whom it may concern", "i would like to inquire",
    "may i know", "kindly assist", "thank you for your time", "sincerely", "regards", "best regards",
    "warm regards", "respectfully", "please let me know", "appreciate your help", "i am writing to",
    "thank you in advance", "looking forward to your response", "awaiting your reply",
    "hope you had a great day", "thank you for your attention", "i appreciate your time",
    "your assistance is highly valued",
]

ALLOWED_TOPICS: List[str] = [
    "aquaculture", "fish farming", "pisciculture", "fisheries", "catla", "shrimp", "feed management",
    "pond cleaning", "irrigation", "soil health", "poultry", "agriculture", "organic", "crop rotation",
    "harvesting", "fertilizer", "climate", "farming", "biofloc", "hydroponics", "tilapia", "disease",
    "water quality", "aquaponics", "hatchery management", "fish breeding", "livestock", "vermicomposting",
    "greenhouse farming", "integrated farming", "pasture management", "drip irrigation", "pest control",
    "sustainable farming", "seed treatment", "crop yield", "farm equipment", "traceability",
    "fish nutrition", "duck farming", "desilting", "fingerlings",
]

FALLBACK_TEXT = (
    "<!--FALLBACK-->🐟 Oops! Just a heads-up: **SORRY**\n"
    "I'm trained specifically in **aquaculture, agriculture, fish, and poultry** topics.\n"
    "I was developed by **Aquanex Systems**, so that's my specialty!\n"
    "Please ask me something in those areas — I'd love to help! 🙏"
)

def includes_any(text: str, patterns: List[str]) -> bool:
    low = text.lower()
    return any(p in low for p in patterns)

THINK_BLOCK_RE = re.compile(r"<think>([\s\S]*?)</think>", re.IGNORECASE)

def strip_fallback_marker(text: str) -> str:
    return text.replace("<!--FALLBACK-->", "")
