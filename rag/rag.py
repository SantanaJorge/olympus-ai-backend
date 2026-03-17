from __future__ import annotations

from abc import ABC
from enum import Enum
import uuid
from typing import List, Dict, Any, Optional, Union, Callable

import weaviate
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.tools import StructuredTool
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Novo import (sem warning deprecatado)
from langchain_weaviate import WeaviateVectorStore

# Import opcional/lazy para Tavily se quiser evitar erro se não tiver instalado,
# mas como está no requirements, podemos importar direto ou tratar no uso.
try:
    from tavily import TavilyClient
except ImportError:
    TavilyClient = None

try:
    from flashrank import Ranker, RerankRequest
except ImportError:
    Ranker = None


class TypeAccess(Enum):
    READ = "read"
    WRITE = "write"
    ALL = "all"

class Backend(Enum):
    WEAVIATE = "weaviate"


class RAG(ABC):
    """
    Classe base para representar uma coleção de dados usada em RAG
    (tanto memória longa quanto base de conhecimento).

    As classes filhas devem definir, ANTES de chamar super().__init__():

      - self.description: str                      -> descrição da coleção
      - self.backend: Backend                      -> backend (por enquanto só weaviate)
      - self.collection_name: str                  -> nome da class/index no backend
      - self.text_key: str = "content"             -> campo de texto principal
      - self.embedding: Embeddings                 -> instância de Embeddings (OpenAI, etc.)
      - self.client: weaviate.WeaviateClient       -> client do backend (se backend == "weaviate")

      - opcional:
          - self.type_access: TypeAccess           -> nível de acesso (READ, WRITE, ALL). Default: READ
          - self.metadata_fields: List[str]        -> campos que podem ser retornados como metadata
          - self.max_query_results: int            -> top-k padrão (antigo default_k)
          - self.default_filter: dict              -> filtro padrão (ex: por user_id)
          - self.name: str                         -> nome lógico da collection (pra tools)
          - self.chunk_size: int = 1000            -> tamanho do chunk
          - self.chunk_overlap: int = 200          -> overlap do chunk
    """

    def __init__(
        self,
        *,
        default_filter: Optional[Dict[str, Any]] = None,
        name: Optional[str] = None,
        k: Optional[int] = None,
    ):
        # =========================
        # 1. Validações básicas
        # =========================
        if not getattr(self, "description", None):
            raise ValueError(
                f"Description is not initialized in {self.__class__.__name__}"
            )

        if not getattr(self, "backend", None):
            self.backend = Backend.WEAVIATE

        if not getattr(self, "collection_name", None):
            raise ValueError(
                f"collection_name is not initialized in {self.__class__.__name__}"
            )

        if not getattr(self, "text_key", None):
            self.text_key = "content"

        if not getattr(self, "embedding", None):
            raise ValueError(
                f"embedding (Embeddings) is not initialized in {self.__class__.__name__}"
            )

        if not getattr(self, "metadata_fields", None):
            self.metadata_fields: List[str] = []

        if not getattr(self, "max_query_results", None):
            self.max_query_results = 5

        if not getattr(self, "default_filter", None):
            self.default_filter: Optional[Dict[str, Any]] = None

        if not getattr(self, "type_access", None):
            self.type_access = TypeAccess.READ

        if getattr(self, "chunk_size", None) is None:
            self.chunk_size = 1000

        if getattr(self, "chunk_overlap", None) is None:
            self.chunk_overlap = 200

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        # Permite sobrescrever em tempo de instância
        if default_filter is not None:
            self.default_filter = default_filter
        if k is not None:
            self.max_query_results = k
        if name is not None:
            self.name = name

        # Caso não tenha name, usa o collection_name
        if not getattr(self, "name", None):
            self.name = self.__class__.__name__

        # =========================
        # 2. Inicializa o VectorStore conforme o backend
        # =========================
        if self.backend == Backend.WEAVIATE:
            # Se o client não foi passado, tenta instanciar
            if not getattr(self, "client", None):
                skip_checks = getattr(self, "skip_init_checks", True)
                port = getattr(self, "port", 8080)
                
                # Instancia client local
                self.client = weaviate.connect_to_local(
                    port=port,
                    skip_init_checks=skip_checks
                )

            # WeaviateVectorStore do pacote langchain-weaviate (sem deprecation)
            self.vectorstore = WeaviateVectorStore(
                client=self.client,
                index_name=self.collection_name,
                text_key=self.text_key,
                embedding=self.embedding,
                attributes=self.metadata_fields,
            )
        else:
            raise ValueError(
                f"Backend '{self.backend.value}' not supported yet in {self.__class__.__name__}"
            )

        # =========================
        # 3. Cria retriever padrão
        # =========================
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs=self._build_search_kwargs()
        )

        # =========================
        # 4. Inicializa Reranker (FlashRank)
        # =========================
        if Ranker:
            # Modelo default = NanoBERT (super leve)
            self.ranker = Ranker()
        else:
            self.ranker = None

    # =========================
    # Helpers internos
    # =========================

    def _build_search_kwargs(
        self,
        *,
        k: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Monta o dicionário de search_kwargs (especialmente para Weaviate),
        combinando max_query_results e default_filter com os argumentos recebidos.
        """
        kwargs: Dict[str, Any] = {"k": k or self.max_query_results}

        final_filter = None
        if self.default_filter and where:
            # Junta filtros com AND
            final_filter = {
                "operator": "And",
                "operands": [self.default_filter, where],
            }
        elif where:
            final_filter = where
        elif self.default_filter:
            final_filter = self.default_filter

        if final_filter is not None:
            # Para Weaviate, o filtro vai no campo "where"
            kwargs["where"] = final_filter

        return kwargs

    # =========================
    # API principal: search / write
    # =========================

    def search(
        self,
        query: str,
        *,
        k: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None,
    ) -> List[Document]:
        """
        Faz uma busca semântica na coleção.
        """
        search_kwargs = self._build_search_kwargs(k=k, where=where)
        docs = self.vectorstore.similarity_search(query, **search_kwargs)
        return docs

    def smart_search(
        self,
        query: str,
        search_depth: str = "basic", # basic | deep
        min_k: int = 3,
        max_k: int = 25 # Fetch size para deep mode
    ) -> List[Document]:
        """
        Busca inteligente com estratégias adaptativas:
        1. basic: Busca padrão (k definido no init ou default=5)
        2. deep: Busca ampla (max_k) -> Reranking (FlashRank) -> Top-K refinement
        """
        
        # --- Configuração da Estratégia ---
        if search_depth == "deep":
            # Deep: Busca muito (20~30), Reranqueia, devolve top 5~10 melhores
            fetch_k = max_k
            final_k = 10 # Retorna mais contexto
            use_rerank = True
        else:
            # Basic: Busca padrão
            fetch_k = self.max_query_results
            final_k = self.max_query_results
            use_rerank = False

        # --- 1. Retrieval (Weaviate) ---
        # Usamos search normar pois o flashrank vai reavaliar
        search_kwargs = self._build_search_kwargs(k=fetch_k)
        docs = self.vectorstore.similarity_search(query, **search_kwargs)

        if not docs:
            return []

        # --- 2. Reranking (FlashRank) ---
        if use_rerank and self.ranker:
            passages = []
            for doc in docs:
                passages.append({
                    "id": getattr(doc, 'id', str(uuid.uuid4())), # Flashrank pede ID
                    "text": doc.page_content,
                    "meta": doc.metadata
                })
            
            rerank_request = RerankRequest(query=query, passages=passages)
            results = self.ranker.rerank(rerank_request)
            
            # Reconstrói Documents ordenados
            final_docs = []
            for res in results[:final_k]:
                # Aplica um threshold de segurança no score do reranker se quiser
                # score do flashrank é geralmente < 1.0 (sigmoid)
                # if res['score'] < 0.2: continue 

                d = Document(
                    page_content=res['text'],
                    metadata=res['meta']
                )
                d.metadata['_rerank_score'] = res['score']
                final_docs.append(d)
            
            return final_docs
        
        # Se não tiver rerank ou falhar, retorna o que veio do vectorstore
        return docs[:final_k]

    def write(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        source_ids: Optional[List[str]] = None,
    ) -> List[str]:
        """
        Indexa textos na coleção (memória longa ou conhecimento).
        
        Args:
            texts: Lista de textos para salvar.
            metadatas: Lista de metadados correspondentes.
            source_ids: Lista de IDs únicos da FONTE (ex: URL ou hash do arquivo).
                        Se fornecido, os chunks gerados terão IDs determinísticos baseados neste ID.
                        Isso permite deduplicação (sobrescreve chunks antigos da mesma fonte).
        """
        if metadatas is None:
            metadatas = [{} for _ in texts]

        # Processo de chunking
        all_texts = []
        all_metadatas = []
        all_ids = []

        for i, (text, meta) in enumerate(zip(texts, metadatas)):
            # Cria docs temporários para usar o splitter
            docs = self.text_splitter.create_documents([text], [meta])
            
            # Se temos um ID de fonte, geramos IDs determinísticos para os chunks
            source_id = source_ids[i] if source_ids and i < len(source_ids) else None

            for chunk_index, d in enumerate(docs):
                all_texts.append(d.page_content)
                all_metadatas.append(d.metadata)
                
                if source_id:
                    # Gera um UUID determinístico para o chunk: UUID5(NAMESPACE_DNS, source_id + chunk_index)
                    # Usamos o source_id como namespace se for um UUID válido, ou geramos um hash dele
                    try:
                        # Tenta usar como UUID se for string de UUID
                        namespace = uuid.UUID(source_id)
                    except ValueError:
                        # Se não for UUID, gera um a partir da string
                        namespace = uuid.uuid5(uuid.NAMESPACE_DNS, source_id)
                    
                    chunk_id = str(uuid.uuid5(namespace, str(chunk_index)))
                    all_ids.append(chunk_id)
                else:
                    all_ids.append(None)

        # Filtra None se não tivermos IDs para todos (o add_texts lida com ids=None gerando aleatórios)
        # Mas se passarmos uma lista com alguns Nones, pode dar erro dependendo da impl.
        # No LangChain Weaviate, se passarmos ids, tem que ser lista de strings.
        
        final_ids = all_ids if any(all_ids) else None

        if final_ids:
            ids = self.vectorstore.add_texts(
                texts=all_texts,
                metadatas=all_metadatas,
                ids=final_ids,
            )
        else:
            ids = self.vectorstore.add_texts(
                texts=all_texts,
                metadatas=all_metadatas,
            )
        return ids

    # =========================
    # Helpers de integração
    # =========================

    def as_retriever(
        self,
        *,
        k: Optional[int] = None,
        where: Optional[Dict[str, Any]] = None,
    ):
        """
        Retorna um retriever do LangChain já configurado.
        """
        search_kwargs = self._build_search_kwargs(k=k, where=where)
        return self.vectorstore.as_retriever(search_kwargs=search_kwargs)

    def as_tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        k: Optional[int] = None,
    ) -> StructuredTool:
        """
        Expõe essa coleção como uma Tool de busca semântica.

        A tool recebe:
          - `query`: string (consulta) para busca semântica
          - `text_to_save`: string para ser salva na coleção
          - `metadata`: dict opcional com metadados

        O comportamento depende de self.type_access:
          - READ: apenas busca (query)
          - WRITE: apenas escrita (text_to_save)
          - ALL: busca e escrita
        """

        can_read = self.type_access in (TypeAccess.READ, TypeAccess.ALL)
        can_write = self.type_access in (TypeAccess.WRITE, TypeAccess.ALL)

        def rag_wrapper(
            query: Optional[str] = None,
            text_to_save: Optional[str] = None,
            search_depth: str = "basic", # basic vs deep
            metadata: Optional[Dict[str, Any]] = None,
        ) -> Union[str, List[Dict[str, Any]]]:
            # 1. Escrita
            if can_write and text_to_save:
                meta = metadata or {}
                self.write(texts=[text_to_save], metadatas=[meta])
                return f"Informação salva com sucesso: '{text_to_save}'"
            elif text_to_save and not can_write:
                return "Erro: Esta ferramenta não tem permissão de escrita."

            # 2. Leitura
            if can_read and query:
                # Usa smart_search ao invés de search direto
                docs = self.smart_search(query, search_depth=search_depth)
                return [
                    {
                        "page_content": doc.page_content,
                        "metadata": doc.metadata,
                    }
                    for doc in docs
                ]
            elif query and not can_read:
                return "Erro: Esta ferramenta não tem permissão de leitura."

            # 3. Mensagem de ajuda se nenhum parâmetro adequado foi passado
            msgs: List[str] = []
            if can_read:
                msgs.append("`query` para buscar (opcional: `search_depth`='deep' para busca profunda)")
            if can_write:
                msgs.append("`text_to_save` para salvar")

            if not msgs:
                return "Erro: Esta ferramenta não possui operações permitidas (leitura/escrita)."

            return f"Erro: Forneça {' ou '.join(msgs)}."

        return StructuredTool.from_function(
            func=rag_wrapper,
            name=name or self.name,
            description=description or self.description,
        )

    def close(self):
        """
        Fecha a conexão com o cliente Weaviate se estiver aberta.
        """
        if getattr(self, "client", None):
            self.client.close()


class WebRAG(RAG):
    """
    Extensão do RAG para realizar buscas na Web (via Tavily) e salvar os resultados.
    As classes filhas devem definir:
      - tavily_api_key: str
      - max_web_results: int (opcional, default 5)
    """

    def _get_tavily_client(self):
        """Helper para obter cliente Tavily lazy-loaded"""
        if not hasattr(self, "_tavily_client"):
            if not getattr(self, "tavily_api_key", None):
                print("Aviso: tavily_api_key não configurada.")
                self._tavily_client = None
                return None
                
            try:
                if TavilyClient is None:
                    raise ImportError("Biblioteca 'tavily' não instalada.")
                self._tavily_client = TavilyClient(api_key=self.tavily_api_key)
            except Exception as e:
                print(f"Aviso: Não foi possível inicializar TavilyClient: {e}")
                self._tavily_client = None
        return self._tavily_client

    def research_and_store(self, query: str) -> str:
        """
        Realiza busca na web e salva no RAG.
        """
        client = self._get_tavily_client()
        if not client:
            return "Erro: Cliente Tavily não configurado ou biblioteca ausente."

        # Pega o limite de resultados da web (default 5)
        max_results = getattr(self, "max_web_results", 5)

        try:
            # Busca
            response = client.search(
                query=query,
                search_depth="basic",
                max_results=max_results,
                include_answer=True
            )
            
            results = response.get("results", [])
            answer = response.get("answer", "")
            
            if not results and not answer:
                return "Nenhum resultado encontrado."

            # Prepara dados
            texts = []
            metadatas = []
            source_ids = []
            summary = []

            if answer:
                texts.append(f"Resumo AI: {answer}")
                metadatas.append({"source": "tavily_answer", "query": query})
                # ID determinístico para o resumo da query
                source_ids.append(str(uuid.uuid5(uuid.NAMESPACE_URL, f"tavily_answer:{query}")))
                summary.append(f"Resumo: {answer[:100]}...")

            for res in results:
                content = res.get("content", "")
                url = res.get("url", "")
                title = res.get("title", "")
                
                if content:
                    texts.append(f"Title: {title}\nURL: {url}\nContent: {content}")
                    metadatas.append({"source": "tavily", "url": url, "title": title, "query": query})
                    
                    # Gera UUID baseado na URL para deduplicação
                    if url:
                        url_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, url))
                        source_ids.append(url_uuid)
                    else:
                        # Fallback se não tiver URL (raro)
                        source_ids.append(str(uuid.uuid4()))
                        
                    summary.append(f"- [{title}]({url})")

            # Salva
            if texts:
                self.write(texts=texts, metadatas=metadatas, source_ids=source_ids)
                return f"Pesquisa realizada e salva com sucesso.\n" + "\n".join(summary)
            
            return "Nada relevante para salvar."

        except Exception as e:
            return f"Erro na pesquisa: {str(e)}"

    def as_tool(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        k: Optional[int] = None,
    ) -> List[StructuredTool]:
        """
        Retorna as tools de pesquisa:
        1. Web Search (busca na internet e salva)
        2. Read Cache (busca no banco local)
        """
        base_name = name or self.name
        
        # Tool 1: Web Search
        web_tool = StructuredTool.from_function(
            func=self.research_and_store,
            name=f"{base_name}_WebSearch",
            description=f"Realiza buscas na web sobre um tópico e grava na memória. Use para buscar informações novas. (Custo: Créditos Tavily)",
        )

        # Tool 2: Read Cache
        # Reutiliza a lógica de leitura do RAG, mas empacotada com nome específico
        def read_cache_wrapper(query: str) -> str:
            docs = self.search(query, k=k)
            if not docs:
                return "Nenhum documento encontrado no cache local."
            
            summary = []
            for doc in docs:
                title = doc.metadata.get("title", "Sem título")
                url = doc.metadata.get("url", "Sem URL")
                content = doc.page_content[:200].replace("\n", " ")
                summary.append(f"- [{title}]({url}): {content}...")
            
            return "Encontrado no cache local:\n" + "\n".join(summary)

        cache_tool = StructuredTool.from_function(
            func=read_cache_wrapper,
            name=f"{base_name}_ReadCache",
            description=f"Busca apenas na memória local (cache) do agente de pesquisa. Use ANTES de buscar na web para economizar créditos.",
        )

        return [web_tool, cache_tool]
