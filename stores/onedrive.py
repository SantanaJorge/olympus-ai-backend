from rag.base import TypeAccess
from rag.ragie import RagieRAG


class OneDrive(RagieRAG):
    description = """
        Base de conhecimento sincronizada com o OneDrive.
        Use para buscar documentos, arquivos e informações armazenados no OneDrive.
        Apenas busca é permitida.
    """

    partition = "test"
    type_access = TypeAccess.READ
