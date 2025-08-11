from typing import Any, Text, Dict, List
from pymongo import MongoClient
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

client = MongoClient("mongodb+srv://Admin:12345@justicebot.84nmsn0.mongodb.net/?retryWrites=true&w=majority&appName=JusticeBot")
db = client.get_database("JusticeBot") 

class ActionGetCaseStatus(Action):

    def name(self) -> Text:
        return "action_get_case_status"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        case_number = next(tracker.get_latest_entity_values("case_number"), None)

        if not case_number:
            dispatcher.utter_message(text="Please provide a valid case number.")
            return []

        cases_collection = db.get_collection("cases")  # your MongoDB collection
        result = cases_collection.find_one({"case_number": case_number})

        if result:
            dispatcher.utter_message(text=f"The status of case {case_number} is: {result.get('status', 'not available')}")
        else:
            dispatcher.utter_message(text=f"No information found for case {case_number}.")

        return []

# === Action: Get Number of Judges ===
class ActionGetJudgeCount(Action):

    def name(self) -> Text:
        return "action_get_judge_count"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        judges_collection = db.get_collection("judges")
        count = judges_collection.count_documents({})

        dispatcher.utter_message(text=f"There are currently {count} judges available.")
        return []

# === Action: Get Judge Availability ===
class ActionCheckJudgeAvailability(Action):

    def name(self) -> Text:
        return "action_check_judge_availability"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        judge_name = next(tracker.get_latest_entity_values("judge_name"), None)

        if not judge_name:
            dispatcher.utter_message(text="Please provide a judge's name.")
            return []

        judges_collection = db.get_collection("judges")
        judge = judges_collection.find_one({"name": {"$regex": judge_name, "$options": "i"}})

        if judge:
            dispatcher.utter_message(text=f"Judge {judge_name} is currently {judge.get('status', 'available')}.")
        else:
            dispatcher.utter_message(text=f"No information available for Judge {judge_name}.")

        return []
