from pathlib import Path
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class KnowledgeBase:
    """
    A lightweight RAG-style document search engine.
    """

    def __init__(self, data_folder="data"):

        self.data_folder = Path(data_folder)

        # Load all documents
        self.chunks = self._load_documents()

        # Count documents
        self.document_count = len(
            list(self.data_folder.glob("*.txt"))
        )

        self.vectorizer = None
        self.matrix = None

        # Create search vectors
        if self.chunks:

            self.vectorizer = TfidfVectorizer(
                stop_words="english"
            )

            self.matrix = self.vectorizer.fit_transform(
                self.chunks
            )


    def _load_documents(self):
        """
        Load text files from the data folder.
        """

        chunks = []

        # Find all text files
        for file in self.data_folder.glob("*.txt"):

            # Read file content
            text = file.read_text(
                encoding="utf-8",
                errors="ignore"
            ).strip()

            if not text:
                continue

            # Split document into paragraphs
            paragraphs = re.split(
                r"\n\s*\n",
                text
            )

            # Add each paragraph as a searchable chunk
            for paragraph in paragraphs:

                paragraph = paragraph.strip()

                if paragraph:

                    chunks.append(
                        f"Source: {file.name}\n"
                        f"{paragraph}"
                    )

        return chunks


    def search(
        self,
        query,
        top_k=4,
        min_score=0.05
    ):
        """
        Search the knowledge base and return
        the most relevant document chunks.
        """

        # Check if knowledge base exists
        if (
            not self.vectorizer
            or self.matrix is None
        ):
            return ""

        # Convert user query into a vector
        query_vector = self.vectorizer.transform(
            [query]
        )

        # Calculate similarity scores
        scores = cosine_similarity(
            query_vector,
            self.matrix
        ).flatten()

        # Get highest scoring results
        ranked_indexes = scores.argsort()[::-1]

        results = []

        for index in ranked_indexes[:top_k]:

            # Only return relevant results
            if scores[index] >= min_score:

                results.append(
                    self.chunks[index]
                )

        # Combine results
        return "\n\n---\n\n".join(results)
