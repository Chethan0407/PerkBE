class DocumentService:
    @staticmethod
    async def upload(plan_id: int, file):
        # TODO: Implement file upload
        return {"filename": file.filename}

    @staticmethod
    async def get_all(plan_id: int):
        # TODO: Implement document retrieval
        return [] 