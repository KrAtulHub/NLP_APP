from huggingface_hub import InferenceClient

from secret import HF_TOKEN


class API:

    def __init__(self):

        self.client = InferenceClient(api_key=HF_TOKEN)


    def perform_ner(self, text):

        result = self.client.token_classification(text, model="dslim/bert-base-NER")

        entities = []

        for item in result:

            entities.append(f"{item.word} : {item.entity_group}")

        return "\n".join(entities)

    def perform_emotion_detection(self, text):

        result = self.client.text_classification(
            text, model="j-hartmann/emotion-english-distilroberta-base"
        )

        return {"emotion": result[0].label, "confidence": round(result[0].score, 2)}
