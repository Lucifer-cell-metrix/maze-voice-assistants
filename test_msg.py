from assistant.brain import _try_actions
from config import CONTACTS

# Mocking the contact just in case
CONTACTS["yashank"] = "+919876543210"

print("Result:", _try_actions("send hello to yashank on whatsapp"))
