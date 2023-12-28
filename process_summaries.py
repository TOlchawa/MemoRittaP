class SummaryManager:
    def __init__(self, storage):
        self.storage = storage

    async def process_summaries(self):
        summaries = self.storage.get_messages_summary()
        for h in summaries:
            print(f'summary: {h}')
